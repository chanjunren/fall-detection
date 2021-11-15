from multiprocessing import Process, Event, Semaphore, Queue, current_process
from queue import Empty as QueueEmpty
import asyncio
import platform
import sys
import time
import math
import csv
from bleak import BleakClient
from Movement import Mov
import cv2
import datetime

async def collect_data(address, channel, period, time_s, start_event, sem, queue):
    ADDRESS = (
        address[0] if platform.system() != "Darwin" else address[1]
    )

    async with BleakClient(ADDRESS) as central:
        print((central.is_connected, central.mtu_size))
        imu = Mov(central, address, channel, queue)
        await imu.setPeriod(period)
        await imu.setConfig(True,True,False,False,Mov.ACC_RANGE_2)
        per = await imu.getPeriod()
        if per != period:
            raise Exception("Period not set!")
        sem.release()
        #####################
        start_event.wait()
        await imu.subscribe()
        await asyncio.sleep(time_s)
        await imu.unsubscribe()
        sem.release()
        #####################
        await imu.disable()
        await asyncio.sleep(1)

def window_list(queue_in, queue_out, window_sz, stride, sem, start_event):
    print("window", current_process().name)
    buffer = []
    n = 0
    sem.release()
    start_event.wait()
    try:
        while True:
            buffer.append(queue_in.get(timeout=2))
            n+=1
            if n == window_sz:
                queue_out.put(buffer)
                buffer=buffer[stride:]
                n-=stride
    except QueueEmpty:
        return

def process_window_q(queue_out, sem, start_event):
    print("process1", current_process().name)
    sem.release()
    start_event.wait()
    try:
        while True:
            print(len(queue_out.get(timeout=5)))
    except QueueEmpty:
        return

def process_2_window_q(queue0_out, queue1_out, sem, start_event):
    print("process2", current_process().name)
    sem.release()
    start_event.wait()
    try:
        while True:
            w0 = queue0_out.get(timeout=5)
            w1 = queue1_out.get(timeout=5)
            print("do something with 2 windows @", time.time_ns()//1000000)
    except QueueEmpty:
        return

def run(address, channel, period, time_s, start_event, sem, queue):
    print("tag", channel, current_process().name)
    return asyncio.run(collect_data(address, channel, period, time_s, start_event, sem, queue))

def sync_start(n, start_event, sem):
    print("SYNC", current_process().name)
    for _ in range(n):
        sem.acquire()
    # delay to allow for latency (e.g. setConfig taking effect on sensor tags)
    time.sleep(0.500)
    print("START!")
    start_event.set()

def timestamp_inputs(queue_in, queue_out, sem, start_event, time_s):
    print("timestamp", current_process().name)
    sem.release()
    start_event.wait()
    try:
        while True:
            data = queue_in.get(timeout=time_s+2)
            queue_out.put([time.time_ns()] + data)
    except QueueEmpty:
        return

def webcam(start_event, sem, queue, time_s):
    print("WEBCAM", current_process().name)
    cam = cv2.VideoCapture(0)
    try:
        print('FPS', cam.get(cv2.CAP_PROP_FPS))
        if not cam.isOpened():
            raise Exception("WEBCAM NOT OPEN")

        sem.release()
        start_event.wait()

        start = time.time_ns()
        curr = start
        queue.put((start, None))
        while((curr - start)/1000000000 < time_s):
            _, frame = cam.read()
            curr = time.time_ns()
            queue.put((curr, frame))
    except Exception as e:
        print(e)
    finally:
        cam.release()
        print("WEBCAM DONE")

def label(label_q, csv_name):
    f0 = open(f'{csv_name}-label' + '.csv', 'a', newline='')
    write0 = csv.writer(f0)
    write0.writerow(['Timestamp', 'label'])

    print("label", current_process().name)
    cv2.startWindowThread()
    cv2.namedWindow("LABEL_ME, q to stop")
    i = 0
    w_label = []
    labelling = True

    start, _ = label_q.get_nowait()
    while labelling:
        try:
            curr,f = label_q.get_nowait()
        except QueueEmpty:
            break

        print(i,'@',(curr-start)/1000000000)
        cv2.imshow('LABEL_ME, q to stop', f)
        key = cv2.waitKey(0) & 0xff
        label = None

        if key == ord('q'):
            labelling = False
            print("STOP LABELING @", curr)
            break
        i+=1
        if key == ord('1'):
            label = 'fall'
        elif key == ord('0'):
            label = 'not-fall'
        else:
            label = 'unknown'
        print(i,'@',curr, 'is', label)
        write0.writerow([curr, label])

    try:
        while True:
            label_q.get(timeout=.1)
    except QueueEmpty:
        pass

    f0.close()
    cv2.destroyAllWindows()

def save(queue0_out, queue1_out, csv_name):
    fields = ['Timestamp', 'ax', 'ay', 'az', 'gx', 'gy', 'gz']
    f0 = open(f'{csv_name}-waist' + '.csv', 'a', newline='')
    f1 = open(f'{csv_name}-wrist' + '.csv', 'a', newline='')
    write0 = csv.writer(f0)
    write1 = csv.writer(f1)
    write0.writerow(fields)
    write1.writerow(fields)
    rows0 = []
    rows1 = []
    diff = []
    try:
        while True:
            d0 = queue0_out.get(timeout=0.1)
            d1 = queue1_out.get(timeout=0.1)
            # ns to ms
            t0 = d0[0]/1000000
            t1 = d1[0]/1000000
            rows0.append(d0)
            rows1.append(d1)
            diff.append(t0-t1)
    except QueueEmpty:
        write0.writerows(rows0)
        write1.writerows(rows1)
        f0.close()
        f1.close()
        avg = 0
        for x in diff:
            avg+=x
        print(diff[:100]) # print first 100 differences
        avgdiff = round(avg/len(diff), 3)
        with open(f'{csv_name}-avgdiff.txt', 'w') as f:
            f.write('waist ahead of wrist by (milliseconds)\n')
            f.write(str(avgdiff))

        print('avg difference:', avgdiff, 'ms')
        pass

def main():
    wristAddress = ("54:6c:0e:B7:90:84", "5FED95F3-EC32-4D3B-AD80-042D49AC1174")
    waistAddress = ("54:6C:0E:53:35:E2", "DB6C6D52-CD50-45E4-9365-0F2A5697C96E")

    filename = sys.argv[1]
    period = 30
    time_s = 1
    n_timestampers = 2
    e = math.floor(1 + time_s * 1000 / (period * Mov.SENSOR_PERIOD_RESOLUTION))

    start_event = Event()
    sem = Semaphore(0)
    queue0_in = Queue(e+20)
    queue1_in = Queue(e+20)
    queue0_out = Queue(e+20)
    queue1_out = Queue(e+20)
    webcam_queue = Queue()
    label_queue = Queue()
    print(f"Saving to file: {filename}")
    print(f'Recording data for {time_s}s')
    print(f'Period={period*Mov.SENSOR_PERIOD_RESOLUTION}ms')
    print("Expected # of readings is:", e)

    processes = []
    processes.append(Process(target=run, args=(waistAddress, 0, period, time_s, start_event, sem, queue0_in)))
    processes.append(Process(target=run, args=(wristAddress, 1, period, time_s, start_event, sem, queue1_in)))
    processes.extend([Process(target=timestamp_inputs, args=(queue0_in, queue0_out, sem, start_event, time_s)) for i in range(n_timestampers)])
    processes.extend([Process(target=timestamp_inputs, args=(queue1_in, queue1_out, sem, start_event, time_s)) for i in range(n_timestampers)])
    processes.append(Process(target=webcam, args=(start_event, sem, webcam_queue, time_s)))
    processes.append(Process(target=sync_start, args=(2+1+2*n_timestampers, start_event, sem)))

    for p in processes:
        p.start()

    # empty queue so webcam process can end
    try:
        start_event.wait()
        while True:
            label_queue.put(webcam_queue.get(timeout=1))
    except QueueEmpty:
        pass

    for p in processes:
        p.join()

    save(queue0_out, queue1_out, filename)
    label(label_queue, filename)



    # #### window + processes window
    # window_len = 50
    # stride_len = 5
    # processes.append(Process(target=window_list, args=(queue0_in, queue0_out, window_len, stride_len, sem, start_event)))
    # processes.append(Process(target=window_list, args=(queue1_in, queue1_out, window_len, stride_len, sem, start_event)))
    # processes.append(Process(target=process_window_q, args=(queue0_out, sem, start_event)))
    # processes.append(Process(target=process_window_q, args=(queue1_out, sem, start_event)))
    # processes.append(Process(target=sync_start, args=(2+4, start_event, sem)))
    # for p in processes:
    #     p.start()
    # for p in processes:
    #     p.join()

    # ### window + processes pair of window
    # window_len = 50
    # stride_len = 5
    # processes.append(Process(target=window_list, args=(queue0_in, queue0_out, window_len, stride_len, sem, start_event)))
    # processes.append(Process(target=window_list, args=(queue1_in, queue1_out, window_len, stride_len, sem, start_event)))
    # processes.append(Process(target=process_2_window_q, args=(queue0_out, queue1_out, sem, start_event)))
    # processes.append(Process(target=sync_start, args=(2+3, start_event, sem)))
    # for p in processes:
    #     p.start()
    # for p in processes:
    #     p.join()


if __name__ == "__main__":
    main()
