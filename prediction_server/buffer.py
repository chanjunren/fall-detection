import logging
import numpy as np
import time
import signal
import threading
import multiprocessing
import queue
from concurrent.futures import ProcessPoolExecutor as Pool
from multiprocessing import shared_memory, Array, current_process
from queue import Queue
from os import path

logger = logging.getLogger('SyncBuffer')
logger.setLevel(logging.INFO)
FORMAT = '%(asctime)s -- %(processName)s -- %(levelname)s \t %(message)s'
logging.basicConfig(format=FORMAT)
SHM_LIST='SyncBuffer_state_vars'
SHM_BUF='SyncBuffer_np_buf'

class SyncBuffer:
    def __init__(self, length, height, stride, shm_list_name=SHM_LIST, shm_buf_name=SHM_BUF):
        self.list_name = shm_list_name
        self.buf_name = shm_buf_name
        self.L = length
        self.H = height
        self.S = stride
        self.shm = None
        self.AB = None
        self.buffer = None
        self.lock = None
        self.callback = None

    def register_lock(self, lock):
        self.lock = lock

    def register_callback(self, callback):
        self.callback = callback

    def clear_state(self):
        self.A = False
        self.B = False
        self.posA = 0
        self.posB = 0
        self.nA = 0
        self.nB = 0
        self.drift = 0

    def reset(self):
        self.lock = None
        self.callback = None

    def open(self):
        size = np.ndarray((self.L, 2*self.H), dtype=np.float32).nbytes
        self.AB = shared_memory.ShareableList([False, False, 0, 0, 0, 0, 0], name=self.list_name)
        self.shm =  shared_memory.SharedMemory(create=True, name=self.buf_name, size=size)
        self.buffer = np.ndarray((self.L, 2*self.H), dtype=np.float32, buffer=self.shm.buf)

    def close(self):
        self.AB.shm.close()
        self.AB.shm.unlink()
        self.shm.close()
        self.shm.unlink()

    @property
    def A(self):
        return self.AB[0]
    @A.setter
    def A(self, value):
        self.AB[0] = value
    @property
    def B(self):
        return self.AB[1]
    @B.setter
    def B(self, value):
        self.AB[1] = value
    @property
    def posA(self):
        return self.AB[2]
    @posA.setter
    def posA(self, value):
        self.AB[2] = value
    @property
    def posB(self):
        return self.AB[3]
    @posB.setter
    def posB(self, value):
        self.AB[3] = value
    @property
    def nA(self):
        return self.AB[4]
    @nA.setter
    def nA(self, value):
        self.AB[4] = value
    @property
    def nB(self):
        return self.AB[5]
    @nB.setter
    def nB(self, value):
        self.AB[5] = value
    @property
    def drift(self):
        return self.AB[6]
    @drift.setter
    def drift(self, value):
        self.AB[6] = value

    def print_state(self):
        print(self.AB)

    def on_full(self):
        assert self.nB == self.nA
        self.nB -= self.S
        self.nA -= self.S
        lowA = self.posA - self.L
        lowB = self.posB - self.L
        window  = np.hstack([
            np.concatenate([self.buffer[lowA%self.L:self.L, self.H:], self.buffer[0:self.posA, self.H:]]),
            np.concatenate([self.buffer[lowB%self.L:self.L, :self.H], self.buffer[0:self.posB, :self.H]]),
        ])
        self.callback(window)

    def writeA(self, one):
        with self.lock:
            # drop previous sample when drift
            if self.A:
                self.posA = (self.posA - 1) % self.L
                self.nA -= 1
                self.drift+=1
                logger.warn('drift')
            else:
                self.drift=0
            # write to buffer
            self.buffer[self.posA, self.H:] = one
            self.posA = (self.posA + 1) % self.L
            self.nA += 1
            self.A = True
            if self.B:
                self.A = False
                self.B = False
                # if buffer if full, ...
                if self.nA == self.L:
                    self.on_full()

    def writeB(self, one):
        with self.lock:
            if self.B:
                # drop previous sample when drift
                self.posB = (self.posB - 1) % self.L
                self.nB -= 1
                self.drift+=1   # number of samples drifted ahead
                logger.warn('drift')

            else:
                self.drift=0
            # d = min(self.L-abs(self.posA-self.posB), abs(self.posA-self.posB))

            # write to buffer
            self.buffer[self.posB, :self.H] = one
            self.posB = (self.posB + 1) % self.L
            self.B = True
            self.nB += 1
            if self.A:
                self.A = False
                self.B = False
                # if buffer if full, ...
                if self.nB == self.L:
                    self.on_full()


def input(sb, A, timeout=None):
    err = ''
    try:
        sb.register_lock(LOCK)
        sb.register_callback(put_in_queue(QUEUE_OUT))
        q = QUEUE_A if A else QUEUE_B
        write_func = sb.writeA if A else sb.writeB
        BARRIER.wait()
        while True:
                job = q.get(timeout=timeout)
                write_func(job)
    except queue.Empty as qe:
        err = 'e1 - No jobs available'
    except Exception as e:
        err = e
    finally:
        if err:
            logger.error('CLIENT_SHUTDOWN:' + err)
        sb.reset()

def feedA(i):
    BARRIER.wait()
    try:
        # time.sleep(.001)
        for _ in range(i):
            time.sleep(1/40 + np.random.uniform(-3/1000,3/1000,1)[0])
            logger.debug('write')
            QUEUE_A.put([1,2,3,4,5,6])
    except Exception as e:
        err = e
    finally:
        if err:
            logging.error(err)

def feedB(i):
    err = ''
    BARRIER.wait()
    try:
        for _ in range(i):
            time.sleep(1/40 + np.random.uniform(-3/1000,3/1000,1)[0])
            QUEUE_B.put([1,2,3,4,5,6])
    except Exception as e:
        err = e
    finally:
        if err:
            logger.error(err)

def put_in_queue(Q):
    def cb(window):
        Q.put(window)
    return cb

def output(timeout):
    err = ''
    try:
        BARRIER.wait()
        while True:
            window = QUEUE_OUT.get(timeout = timeout)
            logger.info(('output', window.shape))
    except queue.Empty:
        err = 'No more output'
    except Exception as e:
        err = e
    finally:
        if err:
            logger.error(err)

def initglobals(lock, qA, qB, qO, barr):
    global LOCK, QUEUE_A, QUEUE_B, QUEUE_OUT, BARRIER
    LOCK = lock
    QUEUE_A = qA
    QUEUE_B = qB
    QUEUE_OUT = qO
    BARRIER = barr
    current_process().name = 'test_drift'

if __name__=="__main__":
    lock = multiprocessing.Lock()
    qA = multiprocessing.Queue()
    qB = multiprocessing.Queue()
    qO = multiprocessing.Queue()
    barrier = multiprocessing.Barrier(5)
    sb = SyncBuffer(60, 6, 20)
    sb.open()
    with Pool(5, initializer=initglobals, initargs=(lock,qA, qB, qO, barrier)) as pool:
        x = pool.submit(input, sb, True, 1)
        x = pool.submit(input, sb, False, 1)
        x = pool.submit(feedA, 210)
        x = pool.submit(feedB, 210)
        x = pool.submit(output, 3)
    sb.print_state()
    logger.info(f'dropped samples A({sb.nA}) and B({sb.nB}) < window size)')
    sb.clear_state()
    sb.close()
