import asyncio
import struct
import time
import csv
import array
import queue
import paho.mqtt.client as mqtt
from bleak import BleakClient

# Wrist channel 1
# Waist channel 0

idx = 0

dataQueue = queue.Queue()
class Mov:
    SERV_UUID = "F000AA80-0451-4000-B000-000000000000" # ?
    DATA_UUID = "F000AA81-0451-4000-B000-000000000000" # R N
    CONF_UUID = "F000AA82-0451-4000-B000-000000000000" # R W
    PERI_UUID = "F000AA83-0451-4000-B000-000000000000" # R W

    '''
    bit masks
    00 00000111  acl
    00 00111000  gyr
    00 01000000  mag
    00 10000000  wom
    11 00000000  range

    '''
    AX_GYR = 0x07
    AX_ACL = 0x38
    EN_MAG = 0x40
    EN_WOM = 0x80
    ACC_RANGE_2     = 0x0
    ACC_RANGE_4     = 0x1
    ACC_RANGE_8     = 0x2
    ACC_RANGE_16    = 0x3
    SENSOR_MIN_UPDATE_PERIOD = 10
    SENSOR_PERIOD_RESOLUTION = 1

    def __init__(self, client:BleakClient, address, channel):
        self.client = client
        self.accRange = Mov.ACC_RANGE_2
        self.address = address
        self.channel = channel
        # self.mqtt_client = mqtt.Client()
        # self.mqtt_client.on_connect = self.on_connect
        # self.mqtt_client.username_pw_set("testuser1", "pass")
        # self.mqtt_client.connect('192.168.10.126', 18831, 60)
        # self.mqtt_topic = f"mixer/data_collection/in/{self.channel}"

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print('Client Successfully Connected to Broker')
        else:
            print("Failed to connect to broker!", rc)

    '''
    calculate acceleration, unit G, range variable
    '''
    def convertAcc(self, int16):
        v = 0.0
        g = 0
        if self.accRange == Mov.ACC_RANGE_2:
            g=2
        elif self.accRange == Mov.ACC_RANGE_2:
            g=4
        elif self.accRange == Mov.ACC_RANGE_2:
            g=8
        elif self.accRange == Mov.ACC_RANGE_2:
            g=16
        else:
            raise Exception()
        return 9.81 * g * int16 / 32768

    '''
    calculate angular velocity, unit deg/s, range +/- 250
    '''
    def convertGyr(self, int16):
        return 500 * int16 / 65536

    '''
    calculate magnetic flux, unit micro Tesla, range +/- 4800
    '''
    def convertMag(self, int16):
        return 9600 * int16 / 65536

    async def disable(self):
        await self.setConfig(False, False, False, False, self.accRange)

    async def getConf(self):
        data = await self.client.read_gatt_char(Mov.CONF_UUID)
        conf_lo, conf_hi = struct.unpack('BB', data)

    async def setConfig(self, acc:bool, gyr:bool, mag:bool, wom:bool, range):
        acc = Mov.AX_ACL if acc else 0
        gyr = Mov.AX_GYR if gyr else 0
        mag = Mov.EN_MAG if mag else 0
        wom = Mov.EN_MAG if wom else 0

        if range not in [Mov.ACC_RANGE_2, Mov.ACC_RANGE_4, Mov.ACC_RANGE_8, Mov.ACC_RANGE_16]:
            raise Exception()

        conf_lo = wom | mag | gyr | acc
        conf_hi = range

        conf = struct.pack('BB', conf_lo, conf_hi)
        res = await self.client.write_gatt_char(Mov.CONF_UUID, conf)
        return res

    async def getPeriod(self):
        peri = await self.client.read_gatt_char(Mov.PERI_UUID)
        peri = struct.unpack('B', peri)[0]
        return peri

    async def setPeriod(self, p):
        peri = struct.pack('B', p)
        await self.client.write_gatt_char(Mov.PERI_UUID, peri)
        return p >= Mov.SENSOR_MIN_UPDATE_PERIOD // Mov.SENSOR_PERIOD_RESOLUTION

    def handle_movement_notif(self, sender:int, data:bytearray):
        # curr_time = round(time.time() * 1000)
        u = struct.unpack('9h', data)

        gyr = (u[0], u[1], u[2])
        acc = (u[3], u[4], u[5])
        mag = (u[6], u[7], u[8])

        acc = self.convertAcc(acc[0]), self.convertAcc(acc[1]), self.convertAcc(acc[2])
        gyr = self.convertGyr(gyr[0]), self.convertGyr(gyr[1]), self.convertGyr(gyr[2])
        # mag = self.convertMag(mag[0]), self.convertMag(mag[1]), self.convertMag(mag[2])

        # global idx
        # idx += 1
        processed_data = [acc[0]] + [acc[1]] + [acc[2]] + [gyr[0]] + [gyr[1]] + [gyr[2]]
        # ar = array.array('d', [acc[0], acc[1], acc[2], gyr[0], gyr[1], gyr[2]])
        dataQueue.put(processed_data)
        # self.mqtt_client.publish(self.mqtt_topic, ar.tobytes())
        # print('ACC x%7.3f y%7.3f z%7.3f | ' % acc, end='')
        # print('GYR x%7.3f y%7.3f z%7.3f | ' % gyr)
        # print('MAG x%7.3f y%7.3f z%7.3f   ' % mag)
        return mag, acc, gyr

    def current_milli_time():
        return round(time.time() * 1000)

    def save_to_csv(self, csv_name):
        # wristDataList = [a + b[1::] for a, b in zip(list(wristAccelDataQueue.queue), list(wristGyroDataQueue.queue))]
        fields = ['Timestamp', 'ax', 'ay', 'az', 'gx', 'gy', 'gz']
        filename = f'{csv_name}' + '.csv'
        with open(filename, 'a', newline='') as f:
            write = csv.writer(f)
            write.writerow(fields)
            write.writerows(list(dataQueue.queue))
            f.close()

    async def subscribe(self):
        await self.client.start_notify(Mov.DATA_UUID, self.handle_movement_notif)


    async def unsubscribe(self):
        print("Got: " , idx)
        await self.client.stop_notify(Mov.DATA_UUID)

if __name__ == "__main__":
    pass

    #m.configure(True, True, False, False, Mov.ACC_RANGE_4)
