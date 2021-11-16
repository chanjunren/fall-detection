import json
import uuid
import numpy as np
from os import path
from paho.mqtt import client as mqttclient
from parameters import INPUT_TYPE_NP, SAMPLE_RATE, MQTT_BROKER_HOST, MQTT_PASS, MQTT_USER, TIME_STEPS
from struct import pack, unpack

def encode_mqtt_request(client_id, request_id, x):
    metadata = json.dumps({
        'client_id': client_id,
        'request_id': request_id,
        'shape': x.shape,
    }).encode()
    header = pack('I', len(metadata))
    data = header + metadata + x.tobytes()
    return data

# to send np.array over MQTT
def decode_mqtt_payload2(payload):
    data = json.loads(payload)
    request_id = data['request_id']
    y = {
        'label': data['label'],
        'conf': data['conf']
    }
    return request_id, y

class ClassificationClient(mqttclient.Client):
    def __init__(self):
        super().__init__()
        self.id = uuid.uuid4().hex
        self.request_id = -1

    def request_prediction(self, x):
        self.request_id += 1
        data = encode_mqtt_request(self.id, self.request_id, x.astype(INPUT_TYPE_NP))
        self.publish('request', data)
        # print(f'[SEND] Request#{self.request_id} -> {x.shape}')

    def on_message(self, _, userdata, message):
        request_id, y = decode_mqtt_payload2(message.payload)
        print(request_id, y['label'], y['conf'])
        # print(f'[RECV] Request#{request_id} <- [{y.shape}]')

    def on_connect(self, _, userdata, flags, rc):
        if rc == 0:
            self.subscribe(path.join('results', self.id))
            print('Client Successfully Connected to Broker')
        else:
            print("Failed to connect to broker!", rc)

    def start(self):
        self.username_pw_set(MQTT_USER, password=MQTT_PASS)
        self.connect(MQTT_BROKER_HOST)
        self.loop_start()

if __name__ == "__main__":
    import time
    client = ClassificationClient()
    client.start()
    while True:
        time.sleep(1/20)
        batch_sz = 2
        client.request_prediction(np.random.rand(batch_sz, TIME_STEPS, 12))
