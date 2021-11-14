# -*- coding: utf-8 -*-

import asyncio
import platform
import struct
import csv
import queue
import time


from functools import partial

from bleak import BleakClient

wristAccelDataQueue = queue.Queue()
wristGyroDataQueue = queue.Queue()
waistAccelDataQueue = queue.Queue()
waistGyroDataQueue = queue.Queue()

connectionStatus = []

class Service:
    """
    Here is a good documentation about the concepts in ble;
    https://learn.adafruit.com/introduction-to-bluetooth-low-energy/gatt

    In TI SensorTag there is a control characteristic and a data characteristic which define a service or sensor
    like the Light Sensor, Humidity Sensor etc

    Please take a look at the official TI user guide as well at
    https://processors.wiki.ti.com/index.php/CC2650_SensorTag_User's_Guide
    """

    def __init__(self):
        self.data_uuid = None
        self.ctrl_uuid = None

class Sensor(Service):
    def callback(self, sender: int, data: bytearray):
        raise NotImplementedError()

    async def start_listener(self, client, *args):
        # start the sensor on the device
        write_value = bytearray([0x01])
        await client.write_gatt_char(self.ctrl_uuid, write_value)
        # Wait abit before beginning notifs
        # listen using the handler
        await client.start_notify(self.data_uuid, self.callback)

class MovementSensorMPU9250SubService:
    def __init__(self):
        self.bits = 0

    def enable_bits(self):
        return self.bits

    def cb_sensor(self, data, device):
        raise NotImplementedError

class MovementSensorMPU9250(Sensor):
    GYRO_XYZ = 7
    ACCEL_XYZ = 7 << 3
    MAG_XYZ = 1 << 6
    ACCEL_RANGE_2G  = 0 << 8
    ACCEL_RANGE_4G  = 1 << 8
    ACCEL_RANGE_8G  = 2 << 8
    ACCEL_RANGE_16G = 3 << 8

    def __init__(self):
        super().__init__()
        self.data_uuid = "f000aa81-0451-4000-b000-000000000000"
        self.ctrl_uuid = "f000aa82-0451-4000-b000-000000000000"
        self.ctrlBits = 0
        self.sub_callbacks = []

    def register(self, cls_obj: MovementSensorMPU9250SubService):
        self.ctrlBits |= cls_obj.enable_bits()
        self.sub_callbacks.append(cls_obj.cb_sensor)

    async def start_listener(self, client, *args):
        # start the sensor on the device
        await client.write_gatt_char(self.ctrl_uuid, struct.pack("<H", self.ctrlBits))
        # listen using the handler
        # await client.start_notify(self.data_uuid,self.callback)
        await client.start_notify(self.data_uuid, partial(self.new_callback, device=args[0]))
        # Make sure both sensortags start saving data at the same time
        reset_queues()

    def callback(self, sender: int, data: bytearray):
        unpacked_data = struct.unpack("<hhhhhhhhh", data)
        for cb in self.sub_callbacks:
            cb(unpacked_data)
    
    def new_callback(self, sender: int, data: bytearray, device: str):
        timestamp = current_milli_time()
        unpacked_data = struct.unpack("<hhhhhhhhh", data)
        for cb in self.sub_callbacks:
            cb(unpacked_data, device, timestamp)

class AccelerometerSensorMovementSensorMPU9250(MovementSensorMPU9250SubService):
    def __init__(self):
        super().__init__()
        self.bits = MovementSensorMPU9250.ACCEL_XYZ | MovementSensorMPU9250.ACCEL_RANGE_4G
        self.scale = 8.0/32768.0 # TODO: why not 4.0, as documented? @Ashwin Need to verify

    def cb_sensor(self, data, device, timestamp):
        '''Returns (x_accel, y_accel, z_accel) in units of g'''
        rawVals = data[3:6]
        processed_data = [timestamp] + [ v*self.scale for v in rawVals ]
        # wristAccelDataQueue.put(processed_data)
        if device == "54:6c:0e:B7:90:84":
            wristAccelDataQueue.put(processed_data)
        else:
            waistAccelDataQueue.put(processed_data)
        # print(f"[{device}] Accelerometer:", tuple([ v*self.scale for v in rawVals ]))

class GyroscopeSensorMovementSensorMPU9250(MovementSensorMPU9250SubService):
    def __init__(self):
        super().__init__()
        self.bits = MovementSensorMPU9250.GYRO_XYZ
        self.scale = 500.0/65536.0

    def cb_sensor(self, data, device, timestamp):
        '''Returns (x_gyro, y_gyro, z_gyro) in units of degrees/sec'''
        rawVals = data[0:3]
        processed_data = [timestamp] + [ v*self.scale for v in rawVals ]
        # wristGyroDataQueue.put(processed_data)
        if device == "54:6c:0e:B7:90:84":
            wristGyroDataQueue.put(processed_data)
        else:
            waistGyroDataQueue.put(processed_data)
        # print(f"[{device}] Gyroscope:", tuple([ v*self.scale for v in rawVals ]))

async def connect_to_device(address):
    print("Starting", address, "loop")
    async with BleakClient(address, timeout=5.0) as client:
        print(f"Attempting connection to {address}")
        x = await client.is_connected()
        print(f"Connected to {x}")
        global connectionStatus
        connectionStatus.append(True)
        try:
            acc_sensor = AccelerometerSensorMovementSensorMPU9250()
            gyro_sensor = GyroscopeSensorMovementSensorMPU9250()
            movement_sensor = MovementSensorMPU9250()
            movement_sensor.register(acc_sensor)
            movement_sensor.register(gyro_sensor)
            await movement_sensor.start_listener(client, address)
            # Terminates after 60s
            await asyncio.sleep(60.0)
        except Exception as e:
            print(e)
            save_to_csv()
    print(f"Disconnected from {address}")

def reset_queues():
    print("Clearing Queues on connect")
    with wristAccelDataQueue.mutex:
        wristAccelDataQueue.queue.clear()
    with wristGyroDataQueue.mutex:
        wristGyroDataQueue.queue.clear()
    with waistAccelDataQueue.mutex:
        waistAccelDataQueue.queue.clear()
    with waistGyroDataQueue.mutex:
        waistGyroDataQueue.queue.clear()

def save_to_csv():
    print(f"wristAccel: {len(list(wristAccelDataQueue.queue))}")
    print(f"wristGyro: {len(list(wristGyroDataQueue.queue))}")
    print(f"waistAccel: {len(list(waistAccelDataQueue.queue))}")
    print(f"waistGyro: {len(list(waistGyroDataQueue.queue))}")
    wristDataList = [a + b[1::] for a, b in zip(list(wristAccelDataQueue.queue), list(wristGyroDataQueue.queue))]
    waistDataList = [a + b[1::] for a, b in zip(list(waistGyroDataQueue.queue), list(waistGyroDataQueue.queue))]
    fields = ['Timestamp', 'ax', 'ay', 'az', 'gx', 'gy', 'gz']
    with open('wristData.csv', 'a', newline='') as f:
        write = csv.writer(f)
        write.writerow(fields)
        write.writerows(wristDataList)
        f.close()

    with open('waistData.csv', 'a', newline='') as f:
        write = csv.writer(f)
        write.writerow(fields)
        write.writerows(waistDataList)
        f.close()

def current_milli_time():
    return round(time.time() * 1000)
    # return time.time()

async def main(addresses):
    return await asyncio.gather(*(connect_to_device(address) for address in addresses))

if __name__ == "__main__":
    import os
    os.environ["PYTHONASYNCIODEBUG"] = str(1)
    # addresses = ["54:6c:0e:B7:90:84", "54:6C:0E:B4:23:85"]
    addresses = ["54:6c:0e:B7:90:84", "54:6C:0E:B7:AA:84"]
    # addresses = ["54:6c:0e:B7:90:84"]
    asyncio.run(main(addresses))  
    save_to_csv()