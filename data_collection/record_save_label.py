from multiprocessing import Process, Event, Semaphore, Queue, current_process
from multiprocessing import Manager
from queue import Empty as QueueEmpty
from bleak import BleakClient

import os
import asyncio
import platform
import sys
import time
import math
import csv
import cv2
import datetime

from Movement import Mov
from parameters import WAIST_CSV_HEADERS, WRIST_CSV_HEADERS, LABEL_CSV_HEADERS, META_CSV_HEADERS
from parameters import IDS, LABELS, LABEL_NONE
from parameters import TAG_PERIOD
from parameters import DATA_BASE_PATH

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


def run(address, channel, period, time_s, start_event, sem, queue):
    print("TAG", channel, current_process().name)
    return asyncio.run(collect_data(address, channel, period, time_s, start_event, sem, queue))

def sync_start(n, start_event, sem):
    print("SYNC     ", current_process().name)
    for _ in range(n):
        sem.acquire()

    time.sleep(0.500)
    print("\nSTART!")
    start_event.set()

def timestamp_inputs(queue_in, queue_out, sem, start_event, time_s):
    print("TIMESTAMP", current_process().name)
    sem.release()
    start_event.wait()

    try:
        while True:
            data = queue_in.get(timeout=2)
            queue_out.put([time.time_ns()] + data)
            # print(current_process().name)
    except QueueEmpty:
        return
    finally:
        print("TIMESTAMP", current_process().name, "DONE")


def webcam(start_event, sem, queue, time_s, ret_queue):
    # process for running webcam

    cam = cv2.VideoCapture(0)
    fps = cam.get(cv2.CAP_PROP_FPS)
    ret_queue.put(('fps', fps))
    print("WEBCAM   ", current_process().name, '\nFPS is', fps)
    try:
        if not cam.isOpened():
            raise Exception("WEBCAM NOT OPEN, please kill program")
        sem.release()
        start_event.wait()

        start = curr = time.time_ns()
        queue.put((start, None))

        while((curr - start)/1000000000 < time_s):
            _, frame = cam.read()
            curr = time.time_ns()
            small = cv2.resize(frame, (frame.shape[1]//2, frame.shape[0]//2))
            queue.put((curr, small))

    except Exception as e:
        print(e)
        raise e

    finally:
        cam.release()
        print("WEBCAM   ", current_process().name, 'DONE')

def label_init(label_q, csv_name, image_folder):
    f0 = open(csv_name, 'a', newline='')
    write0 = csv.writer(f0)
    write0.writerow(LABEL_CSV_HEADERS)
    idx = 0
    start, _ = label_q.get_nowait()
    try:
        while True:
            t, f = label_q.get(timeout=.1)
            cv2.imwrite(os.path.join(image_folder, f'{idx}.png'), f)
            write0.writerow([t, LABEL_NONE])
            idx += 1
    except QueueEmpty:
        pass
    f0.close()
    return idx

def save(queue0_out, queue1_out, path0, path1):
    f0 = open(path0, 'a', newline='')
    f1 = open(path1, 'a', newline='')
    write0 = csv.writer(f0)
    write1 = csv.writer(f1)
    write0.writerow(WAIST_CSV_HEADERS)
    write1.writerow(WRIST_CSV_HEADERS)

    rows0 = []
    rows1 = []
    n = 0
    avgdiff = 0


    try:
        while True:
            d0 = queue0_out.get(timeout=0.1)
            d1 = queue1_out.get(timeout=0.1)

            # ns to ms
            t0 = d0[0]/1000000
            t1 = d1[0]/1000000

            rows0.append(d0)
            rows1.append(d1)
            n += 1
            avgdiff += (t1-t0)

    except QueueEmpty: # will always  occur
        write0.writerows(rows0)
        write1.writerows(rows1)
        f0.close()
        f1.close()
        avgdiff /= n
        # print(diff[:100]) # print first 100 differences
        print('avg difference:', avgdiff, 'ms')
        return avgdiff, n

def record_save(filename, period, time_s):
    wristAddress = ("54:6c:0e:B7:90:84", "5FED95F3-EC32-4D3B-AD80-042D49AC1174")
    waistAddress = ("54:6C:0E:53:35:E2", "DB6C6D52-CD50-45E4-9365-0F2A5697C96E")

    n_timestampers = 1

    FOLDER_PATH = os.path.join(DATA_BASE_PATH, 'unprocessed', filename)
    if os.path.exists(FOLDER_PATH):
        raise FileExistsError(f'Please specify unique name for recording. The specified path "{FOLDER_PATH}" already exists.')
    print(f"Saving to directory: {filename}")

    WAIST_PATH = os.path.join(FOLDER_PATH, 'waist.csv')
    WRIST_PATH = os.path.join(FOLDER_PATH, 'wrist.csv')
    LABEL_PATH = os.path.join(FOLDER_PATH, 'label.csv')
    META_PATH  = os.path.join(FOLDER_PATH, 'meta.csv')
    FRAME_PATH = os.path.join(FOLDER_PATH, 'frames')
    os.makedirs(FRAME_PATH)

    e = math.floor(1 + time_s * 1000 / (period * Mov.SENSOR_PERIOD_RESOLUTION))
    print(f'Recording data for {time_s}s @ Period : {period*Mov.SENSOR_PERIOD_RESOLUTION}ms')
    print("Expected # of readings is:", e)
    print()

    start_event = Event()
    sem = Semaphore(0)
    queue0_in = Manager().Queue(e+20)
    queue1_in = Manager().Queue(e+20)
    queue0_out = Manager().Queue(e+20)
    queue1_out = Manager().Queue(e+20)
    webcam_queue = Manager().Queue()
    label_queue = Manager().Queue()
    ret_queue = Manager().Queue()

    processes = []
    # enable both tags
    processes.append(Process(target=run, args=(waistAddress, 0, period, time_s, start_event, sem, queue0_in)))
    processes.append(Process(target=run, args=(wristAddress, 1, period, time_s, start_event, sem, queue1_in)))
    # separate process for labelling time
    processes.extend([Process(target=timestamp_inputs, args=(queue0_in, queue0_out, sem, start_event, time_s)) for i in range(n_timestampers)])
    processes.extend([Process(target=timestamp_inputs, args=(queue1_in, queue1_out, sem, start_event, time_s)) for i in range(n_timestampers)])
    # process for capturing frames for later labelling
    processes.append(Process(target=webcam, args=(start_event, sem, webcam_queue, time_s, ret_queue)))
    # to syncronise the start of the tags + rest
    processes.append(Process(target=sync_start, args=(2+1+2*n_timestampers, start_event, sem)))

    for p in processes:
        p.start()

    key, fps = ret_queue.get(timeout=3)
    assert key == 'fps'
    # multiprocessing process is not collected by join until queue is emptied (?) if it puts into queue
    # empty queue so webcam process can be .join()ed
    try:
        start_event.wait()
        while True:
            label_queue.put(webcam_queue.get(timeout=1))
    except QueueEmpty:
        pass

    for p in processes:
        p.join()

    # save both tags
    avg_diff, n_frames_data = save(queue0_out, queue1_out, WAIST_PATH, WRIST_PATH)
    # cv2+imshow + waitkey to label (UX can be improved)
    n_frames_webcam = label_init(label_queue, LABEL_PATH, FRAME_PATH)

    f = open(META_PATH, 'a', newline='')
    write = csv.writer(f)
    write.writerow(META_CSV_HEADERS)
    write.writerow([fps, avg_diff, n_frames_data, n_frames_webcam, period, time_s])
    f.close()




def annotate_img(img, label=None, pos=None, scrub=None, help=False, n_classes=1):
    assert n_classes >= 1
    pad = 10
    white = (255,255,255,255)
    blue = (209, 80, 0, 255)
    f_pos, f_tot, t_pos, t_tot = pos

    # bot left
    x = 0+pad
    y = img.shape[0] - pad
    pos = f'FRAME: {f_pos}/{f_tot}'
    (w, h), base_y = cv2.getTextSize(pos, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
    img = cv2.putText(img, pos, (x,y), cv2.FONT_HERSHEY_SIMPLEX, 1, blue, 5)
    img = cv2.putText(img, pos, (x,y), cv2.FONT_HERSHEY_SIMPLEX, 1, white, 2)

    y -= (pad + h)
    pos = f'  TIME: {t_pos}/{t_tot}'
    (w, h), base_y = cv2.getTextSize(pos, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
    img = cv2.putText(img, pos, (x,y), cv2.FONT_HERSHEY_SIMPLEX, 1, blue, 5)
    img = cv2.putText(img, pos, (x,y), cv2.FONT_HERSHEY_SIMPLEX, 1, white, 2)

    # top left
    x = 0 + pad
    y = 0 + pad
    label = f'LABEL:   {label}'
    (w, h), base_y = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
    y += (pad + h)
    img = cv2.putText(img, label, (x,y), cv2.FONT_HERSHEY_SIMPLEX, 1, blue, 5)
    img = cv2.putText(img, label, (x,y), cv2.FONT_HERSHEY_SIMPLEX, 1, white, 2)

    # top right
    x = img.shape[1] - pad
    y = 0 + pad
    helps = (f'press "h" for help','','') if not help else (f'NAV using arrow keys', f'LABEL using number keys', f'QUIT using esc/q')
    for line in helps:
        (w, h), base_y = cv2.getTextSize(line, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
        y+=(h+pad)
        img2 = cv2.putText(img, line, (x-w,y), cv2.FONT_HERSHEY_SIMPLEX, 1, blue, 5)
        img2 = cv2.putText(img2, line, (x-w,y), cv2.FONT_HERSHEY_SIMPLEX, 1, white, 2)

    #bot right:
    x = img.shape[1] - pad
    y = img.shape[0] - pad
    scrub = f'step size = {scrub}'
    (w, h), base_y = cv2.getTextSize(scrub, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
    x -= w
    img2 = cv2.putText(img2, scrub, (x,y), cv2.FONT_HERSHEY_SIMPLEX, 1, blue, 5)
    img2 = cv2.putText(img2, scrub, (x,y), cv2.FONT_HERSHEY_SIMPLEX, 1, white, 2)

    return img, img2

def label_only(filename):
    import glob
    import pandas as pd
    FOLDER_PATH = os.path.join(DATA_BASE_PATH, 'unprocessed', filename)
    if not os.path.exists(FOLDER_PATH):
        raise FileExistsError(f'Please specify valid filename')

    LABEL_PATH = os.path.join(FOLDER_PATH, 'label.csv')
    FRAME_PATH = os.path.join(FOLDER_PATH, 'frames')
    ANN_PATH = os.path.join(FOLDER_PATH, 'frames_annotated')

    if not os.path.exists(ANN_PATH):
        os.makedirs(ANN_PATH)

    paths = glob.glob(os.path.join(FRAME_PATH,'*.png'))
    frame_idx = sorted(map(lambda x: int(os.path.basename(x)[:-4]), paths))
    paths = [os.path.join(FRAME_PATH, f'{idx}.png') for idx in frame_idx]
    n_frames = len(paths)
    pos = 0
    labelling = True
    scrub_sz = 1

    df = pd.read_csv(LABEL_PATH, index_col=[0])
    start = df.index[0]
    end = df.index[n_frames-1]
    dur = int(end-start)
    time_tmp = datetime.datetime.combine(datetime.date.min, datetime.time.min)
    total = (time_tmp + datetime.timedelta(microseconds=dur//1000)).strftime("%M:%S.%f")[:-3]

    which = {ord(str(id)): label for id,label in zip(IDS[1:], LABELS[1:])}
    help = True

    cv2.setWindowTitle("label", f'LABEL [{filename}]')

    while labelling:

            curr = df.index[pos]
            now = (time_tmp + datetime.timedelta(microseconds=int(curr-start)//1000)).strftime("%M:%S.%f")[:-3]

            label = df.iloc[pos]['label']

            ann_img, ann_img_2 = annotate_img(
                cv2.imread(paths[pos]),
                label= '' if label==LABEL_NONE else label,
                pos=(pos+1, n_frames, now, total),
                scrub=scrub_sz,
                help=help or label==LABEL_NONE,
                n_classes=len(IDS)-2
                )

            cv2.imshow('label', ann_img_2)

            k = cv2.waitKey(0) & 0xff
            old_pos = pos
            old_ss = scrub_sz
            if k == 2: # left arrow
                pos = max(0, pos-scrub_sz)
                help=False
            elif k == 3: # right arrow
                pos = min(n_frames-1, pos+scrub_sz)
                help=False
            elif k == 0:
                scrub_sz = min(scrub_sz + 1, n_frames)
                help=False
            elif k == 1:
                scrub_sz = max(1, scrub_sz - 1)
                help=False
            elif k in which:
                label = which[k]
                df.iloc[pos]['label'] = label
                assert df.iloc[pos]['label'] == label
                pos = min(n_frames-1, pos+scrub_sz)
                help=False
            elif k in [ord('q'), 27]: #escape
                labelling = False
                help = not help
            else:
                help = not help

            label = df.iloc[old_pos]['label']
            ann_img, _ = annotate_img(
                cv2.imread(paths[old_pos]),
                label= '' if label==LABEL_NONE else label,
                pos=(old_pos+1, n_frames, now, total),
                scrub=scrub_sz,
                help=help or label==LABEL_NONE,
                n_classes=len(IDS)-2
                )

            cv2.imwrite(os.path.join(ANN_PATH, os.path.basename(paths[old_pos])), ann_img)


    df.to_csv(LABEL_PATH)

def main():
    filename = sys.argv[1]
    try:
        record_save(filename, TAG_PERIOD, 30) # period, time_s
    except FileExistsError as e:
        print(filename, 'recorded before')
    label_only(filename)


if __name__ == "__main__":
    main()
