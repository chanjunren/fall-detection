import logging
# logging.basicConfig(level=logging.DEBUG)
import asyncio
import platform
import sys
import time
import math
from bleak import BleakClient
from Movement import Mov

ADDRESS = (
    "54:6c:0e:B7:90:84" # TODO: not set yet
    #"54:6C:0E:B4:23:85"
    if platform.system() != "Darwin"
    else "5FED95F3-EC32-4D3B-AD80-042D49AC1174"
)

async def main():
    async with BleakClient(ADDRESS) as central:
        print((central.is_connected, central.mtu_size))
        imu = Mov(central)
        # valid = await imu.setPeriod(9)
        # await asyncio.sleep(.1)
        # period = await imu.getPeriod()
        # assert not valid and period == Mov.SENSOR_MIN_UPDATE_PERIOD, str((valid, period))
        #
        # valid = await imu.setPeriod(10)
        # await asyncio.sleep(.1)
        # period = await imu.getPeriod()
        # assert valid and period == 10, str((valid, period))
        #
        # valid = await imu.setPeriod(11)
        # await asyncio.sleep(.1)
        # period = await imu.getPeriod()
        # assert valid and period == 11, str((valid, period))

        period = 33
        time_s = 30
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
        #####################
        await imu.disable()
        # valid = await imu.setPeriod(Mov.SENSOR_MIN_UPDATE_PERIOD)
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
