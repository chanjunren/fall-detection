from multiprocessing import Process, Barrier
import asyncio
import platform
import sys
import time
import math
from bleak import BleakClient
from Movement import Mov

async def collect_data(address, filename, channel, barrier):
    ADDRESS = (
        address
        if platform.system() != "Darwin"
        else "5FED95F3-EC32-4D3B-AD80-042D49AC1174"
    )
    async with BleakClient(ADDRESS) as central:
        print((central.is_connected, central.mtu_size))
        imu = Mov(central, address, channel)
        period = 33
        time_s = 90
        e = math.floor(1 + time_s * 1000 / (period * Mov.SENSOR_PERIOD_RESOLUTION))
        print("Expected # of readings is:", e)
        await imu.setPeriod(period)
        await imu.setConfig(True,True,False,False,Mov.ACC_RANGE_2)
        per = await imu.getPeriod()
        print("Period: ", per)
        barrier.wait()
        #####################
        await imu.subscribe()
        await asyncio.sleep(time_s)
        await imu.unsubscribe()
        imu.save_to_csv(filename)
        #####################
        await imu.disable()
        await asyncio.sleep(1)

def run(address, filename, channel, barrier):
    asyncio.run(collect_data(address, filename, channel, barrier))

def ready():
    print('ready')

if __name__ == "__main__":
    wristAddress = "54:6c:0e:B7:90:84"
    waistAddress = "54:6C:0E:53:35:E2"
    filename = sys.argv[1]
    barrier = Barrier(2, ready) 
    print(f"Saving to file: {filename}")
    wrist_process = Process(target=run, args=(wristAddress, filename+'-wrist', 1, barrier))
    waist_process = Process(target=run, args=(waistAddress, filename+'-waist', 0, barrier))
    wrist_process.start()
    waist_process.start()
    wrist_process.join()
    waist_process.join()
