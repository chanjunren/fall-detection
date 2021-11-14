from os import path
from queue import Queue
from threading import Event, Barrier
from paho.mqtt.client import Client
from queue import Empty as QueueEmpty
from concurrent.futures import ThreadPoolExecutor as PoolExecutor
from array import array
from parameters import MQTT_BROKER_HOST, MQTT_BROKER_PORT, TIME_STEPS, STRIDE, N_FEATURES

class RollingWindow:
    def __init__(self, length:int, stride:int, size:int, type:str, callback):
        assert stride <= length
        assert size > 0
        self.size = size
        self.length = length
        self.stride = stride
        self.n = 0
        self.pos = 0
        self.buffer = array(type, [0 for _ in range(length*size)])
        self.callback = callback

    def write(self, data):
        self.buffer[self.pos*self.size:(self.pos + 1)*self.size] = data
        self.pos = (self.pos + 1) % self.length
        self.n += 1
        if self.n == self.length:
            self.n -= self.stride
            low = (self.pos - self.length) % self.length
            window = self.buffer[low*self.size:self.length*self.size] + self.buffer[:self.pos*self.size]
            self.callback(window)


class MqttMixer(Client):
    def __init__(self, n_channels, name, hostname=MQTT_BROKER_HOST, port=MQTT_BROKER_PORT, timeout=None, align=False):
        super().__init__()
        self.n_channels = n_channels
        self.input_topics = [f'mixer/{name}/in/{n}' for n in range(n_channels)]
        self.output_topic = f'mixer/{name}/out'
        self.hostname = hostname
        self.port = port
        # align should be set to TRUE if incoming data is not assured to be in sync
        self.align = align
        self.timeout = timeout
        self.queue = [Queue() for _ in range(n_channels)]
        self.buffer = [None for _ in range(n_channels)]
        self.output = Queue()
        self.alive = [Event() for _ in range(n_channels)]
        self.barrier = Barrier(2)

    def on_output(self, output):
        data = b''.join(output)
        self.publish(self.output_topic, data)
        # print(output)

    def on_message(self, _, userdata, message):
        base, channel = path.split(message.topic)
        if all([is_alive.is_set() for is_alive in self.alive]):
            self.queue[int(channel)].put(message.payload)
        else:
            self.queue = [Queue() for _ in range(self.n_channels)]
            self.alive[int(channel)].set()

    def on_connect(self, _, userdata, flags, rc):
        if rc == 0:
            for topic in self.input_topics:
                self.subscribe(topic)
                print(f'subscribed to "{topic}"')
        else:
            print("Failed to connect to broker!", rc)

    def on_output_loop(self):
        self.barrier.wait()
        try:
            while True:
                output = self.output.get()
                if self.align and self.n_workers == 2:
                    q0 = self.queue[0].qsize()
                    q1 = self.queue[1].qsize()
                    print(q0, q1)
                    self.on_output(output)
                else:
                    self.on_output(output)
        except Exception as e:
            print(e)

    def mix_input_loop(self):
        def qGet(i_queue):
            i, queue = i_queue
            try:
                return Queue.get(queue, timeout=self.timeout)
            except QueueEmpty:
                self.alive[i].clear()
                print('Q empty!...')
                return None

        with PoolExecutor(3) as pool:
            self.barrier.wait()
            while True:
                for is_alive in self.alive:
                    is_alive.wait()
                result_gen = pool.map(qGet, enumerate(self.queue))
                merged = list(result_gen)
                if None not in merged:
                    self.output.put(merged)

    def start(self):
        with PoolExecutor(2) as executor:
            executor.submit(self.mix_input_loop)
            executor.submit(self.on_output_loop)
            self.connect(self.hostname, self.port)
            self.loop_start()


if __name__ == "__main__":
    import sys
    import numpy as np

    def callb(window):
        a = np.frombuffer(window.tobytes(), dtype=np.float64).reshape(-1, N_FEATURES)
        print(a.shape)

    mixer = MqttMixer(int(sys.argv[2]), sys.argv[1], align=False, timeout=1/10)
    window = RollingWindow(TIME_STEPS, STRIDE, N_FEATURES, 'd', callb)

    def on_output(output):
        a = array('d')
        a.frombytes(output[0])
        a.frombytes(output[1])
        window.write(a)

    mixer.on_output = on_output
    mixer.start()
