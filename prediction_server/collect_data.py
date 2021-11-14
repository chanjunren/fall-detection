from mixer import MqttMixer
import sys
from array import array
from queue import Empty as QueueEmpty
from multiprocessing import Queue
from concurrent.futures import ProcessPoolExecutor as Executor
import time
import csv
import pandas as pd

def init_globals(cq, tq):
    global COMBINED, TIMED
    COMBINED = cq
    TIMED = tq

def save_output(output):
    COMBINED.put(output)

def write_to_csv_combined(file, timeout):
    fields = [
        'Timestamp',
        'waist_ax', 'waist_ay', 'waist_az', 'waist_gx', 'waist_gy', 'waist_gz',
        'wrist_ax', 'wrist_ay', 'wrist_az', 'wrist_gx', 'wrist_gy', 'wrist_gz'
    ]
    print('write_process')
    with open(file, 'a', newline='') as f:
        write = csv.writer(f)
        write.writerow(fields)
        try:
            while True:
                time, raw0, raw1 = TIMED.get(timeout=timeout)
                arr = array('d')
                arr.frombytes(raw0)
                arr.frombytes(raw1)
                write.writerow([time] + list(arr))
        except QueueEmpty:
            pass
        finally:
            f.close()

    print('TIMED OUT, saved to', file)
    df = pd.read_csv(file, index_col[0])
    df.to_csv(file)
    print('samples', df.shape[0])

def collection_ps():
    print('collect_process')
    mixer = MqttMixer(2, 'data_collection', align=True, timeout=2)
    mixer.on_output = save_output
    mixer.start()
    # print('collect_process')


def time_input():
    print('time_process')
    while True:
        wa, wr = COMBINED.get()
        timestamp = time.time_ns()
        TIMED.put((timestamp, wa, wr))
        print(timestamp)

if __name__ == "__main__":
    import sys
    timed_q = Queue()
    combined_q = Queue()

    with Executor(6, initializer=init_globals, initargs=(combined_q, timed_q)) as pool:
        pool.submit(time_input)
        pool.submit(time_input)
        pool.submit(time_input)
        pool.submit(time_input)
        pool.submit(collection_ps)
        pool.submit(write_to_csv_combined, f'{sys.argv[1]}_combined_{sys.argv[2]}.csv', int(sys.argv[3]))
