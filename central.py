from multiprocessing import Process
import logging
# logging.basicConfig(level=logging.DEBUG)
import asyncio
import platform
import sys
import time
import math
from bleak import BleakClient
from Movement import Mov

async def collect_data(address, filename, channel):
    ADDRESS = (
        #"54:6c:0e:B7:90:84" # TODO: not set yet
        # "54:6C:0E:B4:23:85"
        # "54:6C:0E:B7:AA:84"
        address
        if platform.system() != "Darwin"
        else "5FED95F3-EC32-4D3B-AD80-042D49AC1174"
    )
    async with BleakClient(ADDRESS) as central:
        print((central.is_connected, central.mtu_size))
        imu = Mov(central, address, channel)
        period = 33
        time_s = 90
        e = math.floor(1 + time_s * 1000 / (period * Mov.SENSOR_PERIOD_RESOLUTION)) # resolution = 10ms
        print("Expected # of readings is:", e)
        await imu.setPeriod(period)
        await imu.setConfig(True,True,False,False,Mov.ACC_RANGE_2)
        per = await imu.getPeriod()
        print("Period: ", per)
        #####################
        await imu.subscribe()
        await asyncio.sleep(time_s)
        await imu.unsubscribe()
        imu.save_to_csv(filename)
        #####################
        await imu.disable()
        # valid = await imu.setPeriod(Mov.SENSOR_MIN_UPDATE_PERIOD)
        await asyncio.sleep(1)

def run(address, filename, channel):
    asyncio.run(collect_data(address, filename, channel))

if __name__ == "__main__":
    # "54:6c:0e:B7:90:84" # TODO: not set yet
    # "54:6C:0E:B4:23:85"
    # "54:6C:0E:B7:AA:84"
    # "54:6C:0E:53:35:E2"
    wristAddress = "54:6c:0e:B7:90:84"
    waistAddress = "54:6C:0E:53:35:E2"
    filename = sys.argv[1]
    print(f"Saving to file: {filename}")
    # 0 = wrist channel , 1 = waist channel
    wrist_process = Process(target=run, args=(wristAddress, filename+'-wrist', 1))
    waist_process = Process(target=run, args=(waistAddress, filename+'-waist', 0))
    wrist_process.start()
    waist_process.start()
    wrist_process.join()
    waist_process.join()
