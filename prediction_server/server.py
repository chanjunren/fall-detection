from paho.mqtt import client as mqttclient
import json
from struct import pack, unpack
import numpy as np
from model import get_binary_model, get_multi_model, decode_prediction_binary, decode_prediction_multi
from concurrent.futures import ProcessPoolExecutor as Pool
from multiprocessing import Queue, Barrier
from threading import Thread
from os import path, getpid
from parameters import MQTT_BROKER_HOST, INPUT_TYPE_NP, MQTT_USER, MQTT_PASS

def init_worker(br, jq, pq):
    global barrier, job_q, pub_q
    barrier = br
    job_q = jq
    pub_q = pq

def print_when_lifted():
    print('\n>>>>>>>>> Server is ready for prediction <<<<<<<<<<\n')

### recv array from mqtt server along w request_id + client_id
def decode_mqtt_payload(payload):
    len = unpack('I', payload[:4])[0]
    metadata = json.loads(payload[4:4+len])
    buffer = payload[4+len:]
    client_id = metadata['client_id']
    request_id = metadata['request_id']
    x = np.frombuffer(buffer, dtype=INPUT_TYPE_NP).reshape(metadata['shape'])
    return client_id, request_id, x

## return json serialized resoponse
def encode_mqtt_response(request_id, y, classes):

    pred = decode_prediction_binary(y, .5, classes)

    data = json.dumps({
        'request_id': request_id,
        'label': pred.tolist(),
        'conf': y.tolist()
    })
    return data

def classification_loop(worker_id, get_model_fxn, model_version):
    try:
        model, features, classes, _ = get_model_fxn(model_version)
        input_shape = model.input.shape
        test = np.random.rand(1, input_shape[1], input_shape[2])
        model.predict(test)
        barrier.wait()
        while True:
            client_id, request_id, x = job_q.get()
            y = model.predict(x)
            pub_q.put((client_id, request_id, y))
    except Exception as e:
        print(f'\n>>>>>>>>>>>> Process {getpid()} failed! <<<<<<<<<<<<\n', e)


class ClassificationServer(mqttclient.Client):
    def __init__(self, n_workers, get_model_fxn, model_version):
        super().__init__()
        self.n_workers = n_workers
        self.barrier = Barrier(n_workers + 2, print_when_lifted)
        self.job_q = Queue()
        self.pub_q = Queue()
        _, features, classes, _ = get_model_fxn(model_version)
        self.get_model_fxn = get_model_fxn
        self.model_version = model_version
        self.features = features
        self.classes = classes

    def publish_response_loop(self):
        self.barrier.wait()
        while True:
            client_id, request_id, y = self.pub_q.get()
            data = encode_mqtt_response(request_id, y, self.classes)
            self.publish(path.join('results', client_id), data)
            print(f'[SEND  to  {client_id[:4]}] Request#{request_id} -> [{y.shape}]')

    def on_message(self, _, userdata, message):
        client_id, request_id, x = decode_mqtt_payload(message.payload)
        self.job_q.put((client_id, request_id, x))
        print(f'[RECV from {client_id[:4]}] Request#{request_id} <- [{x.shape}]')

    def on_connect(self, _, userdata, flags, rc):
        if rc == 0:
            self.subscribe(path.join('request', '#'))
            print('Server Successfully Connected to Broker')
        else:
            print("Failed to connect to broker", rc)

    def start(self):
        pool = Pool(self.n_workers, initializer=init_worker, initargs=(self.barrier, self.job_q, self.pub_q,))
        for i in range(self.n_workers):
            pool.submit(classification_loop, i, self.get_model_fxn, self.model_version)
        Thread(target=self.publish_response_loop).start()
        self.username_pw_set(MQTT_USER, password=MQTT_PASS)
        self.connect(MQTT_BROKER_HOST)
        self.loop_start()
        self.barrier.wait()

if __name__ == "__main__":
    import sys
    n_workers = int(sys.argv[1])
    model_path = sys.argv[2]
    server = ClassificationServer(n_workers, get_binary_model, 1)
    server.start()
