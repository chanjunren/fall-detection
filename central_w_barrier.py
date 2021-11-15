from multiprocessing import Process, Event, Semaphore
import asyncio
import platform
import sys
import time
import math
from bleak import BleakClient
from Movement import Mov

async def collect_data(address, filename, channel, period, time_s, start_event, sem):
    ADDRESS = (
        address[0] if platform.system() != "Darwin" else address[1]
    )

    async with BleakClient(ADDRESS) as central:
        print((central.is_connected, central.mtu_size))
        imu = Mov(central, address, channel)
        await imu.setPeriod(period)
        await imu.setConfig(True,True,False,False,Mov.ACC_RANGE_2)
        per = await imu.getPeriod()
        print("Period: ", per)
        sem.release()
        #####################
        start_event.wait()
        await imu.subscribe()
        await asyncio.sleep(time_s)
        await imu.unsubscribe()
        imu.save_to_csv(filename)
        #####################
        await imu.disable()
        await asyncio.sleep(1)

def run(address, filename, channel, period, time_s, start_event, sem):
    return asyncio.run(collect_data(address, filename, channel, period, time_s, start_event, sem))


def sync_start(n, start_event, sem):
    for _ in range(n):
        sem.acquire()
    # delay to allow for latency (e.g. setConfig taking effect on sensor tags)
    time.sleep(1)
    print("START!")
    start_event.set()

def main():
    wristAddress = ("54:6c:0e:B7:90:84", "5FED95F3-EC32-4D3B-AD80-042D49AC1174")
    waistAddress = ("54:6C:0E:53:35:E2", "DB6C6D52-CD50-45E4-9365-0F2A5697C96E")

    filename = sys.argv[1]
    start_event = Event()
    sem = Semaphore(0)
    print(f"Saving to file: {filename}")
    period = 33
    time_s = 5
    e = math.floor(1 + time_s * 1000 / (period * Mov.SENSOR_PERIOD_RESOLUTION))
    print("Expected # of readings is:", e)
    wrist_process = Process(target=run, args=(wristAddress, filename+'-wrist', 1, period, time_s, start_event, sem))
    waist_process = Process(target=run, args=(waistAddress, filename+'-waist', 0, period, time_s, start_event, sem))
    timer_process = Process(target=sync_start, args=(2, start_event, sem))

    timer_process.start()
    wrist_process.start()
    waist_process.start()
    waist_process.join()
    wrist_process.join()
    timer_process.join()

if __name__ == "__main__":
    main()
