import json
import numpy as np
from paho.mqtt import client as mqttclient
from model import BinaryClassifier
from multiprocessing import Queue, Barrier
from concurrent.futures import ProcessPoolExecutor as Pool
from threading import Thread
from os import path, getpid
from struct import pack, unpack
from parameters import INPUT_SHAPE, MQTT_BROKER_HOST
from h5py import is_hdf5


def init_globals(br, jq, pq):
    global barrier, job_q, pub_q
    barrier = br
    job_q = jq
    pub_q = pq


def print_when_lifted():
    print('\n>>>>>>>>> Server is ready for prediction <<<<<<<<<<\n')


def decode_mqtt_payload(payload):
    len = unpack('I', payload[:4])[0]
    metadata = json.loads(payload[4:4+len])
    buffer = payload[4+len:]
    client_id = metadata['client_id']
    request_id = metadata['request_id']
    x = np.frombuffer(buffer, dtype=np.float32).reshape(metadata['shape'])
    return client_id, request_id, x


def encode_mqtt_response(request_id, y):
    metadata = json.dumps({
        'request_id': request_id,
        'shape': y.shape,
    }).encode()
    header = pack('I', len(metadata))
    data = header + metadata + y.tobytes()
    return data


def classification_loop(worker_id, model_fxn, model_path):
    try:
        model = model_fxn(model_path)
        model.predict(np.random.rand(1, INPUT_SHAPE[0], INPUT_SHAPE[1]))
        barrier.wait()
        while True:
            client_id, request_id, x = job_q.get()
            y = model.predict(x)
            pub_q.put((client_id, request_id, y))
    except Exception as e:
        print(f'\n>>>>>>>>>>>> Process {getpid()} failed! <<<<<<<<<<<<\n', e)
        raise e


class ClassificationServer(mqttclient.Client):
    def __init__(self, n_workers, model_fxn, model_path):
        super().__init__()
        self.n_workers = n_workers
        self.barrier = Barrier(n_workers + 2, print_when_lifted)
        self.job_q = Queue()
        self.pub_q = Queue()
        self.model_fxn = model_fxn
        self.model_path = model_path


    def publish_response_loop(self):
        self.barrier.wait()
        while True:
            client_id, request_id, y = self.pub_q.get()
            data = encode_mqtt_response(request_id, y)
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
        pool = Pool(self.n_workers, initializer=init_globals, initargs=(self.barrier, self.job_q, self.pub_q,))
        for i in range(self.n_workers):
            pool.submit(classification_loop, i, self.model_fxn, self.model_path)
        Thread(target=self.publish_response_loop).start()
        self.connect(MQTT_BROKER_HOST)
        self.loop_start()
        self.barrier.wait()


if __name__ == "__main__":
    import sys
    n_workers = int(sys.argv[1])
    model_path = sys.argv[2]
    server = ClassificationServer(n_workers, BinaryClassifier, model_path)
    server.start()
