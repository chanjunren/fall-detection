from paho.mqtt.client import Client
import struct
import time
import sys
import numpy as np
import array

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print('Client Successfully Connected to Broker')
    else:
        print("Failed to connect to broker!", rc)

c = Client()
c.on_connect = on_connect
c.connect('localhost')
c.loop_start()
topic = f'mixer/{sys.argv[1]}/in/{sys.argv[2]}'
print(topic)
while True:
    time.sleep(1/25 + np.random.uniform(-5/1000, 5/1000, 1)[0])
    a = array.array('d', [1,2,3,123,123,123, 4.2, -2.3, 123.2, 0,0,1])
    c.publish(topic, a.tobytes())
