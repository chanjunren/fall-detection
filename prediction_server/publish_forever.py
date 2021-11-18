from multiprocessing import Process, Event, Semaphore, Queue, current_process
from multiprocessing import Manager
from queue import Empty as QueueEmpty
from bleak import BleakClient
from client import ClassificationClient
from paho.mqtt.client import Client
import os
import asyncio
import platform
import sys
import time
import math
import csv
import cv2
import datetime
import array
import numpy as np


from parameters import MQTT_USER, MQTT_PASS, MQTT_BROKER_HOST, MQTT_BROKER_PORT
from Movement import Mov
from parameters import TAG_PERIOD, TIME_STEPS


async def publish_data_forever(address, channel, period, start_event, sem, queue):
    ADDRESS = (
        address[0] if platform.system() != "Darwin" else address[1]
    )

    async with BleakClient(ADDRESS) as central:
        print((central.is_connected, central.mtu_size))
        imu = Mov(central, address, channel, queue) # puts data into queue
        await imu.setPeriod(period)
        await imu.setConfig(True,True,False,False,Mov.ACC_RANGE_2)
        per = await imu.getPeriod()
        if per != period:
            raise Exception("Period not set!")
        sem.release()
        #####################
        start_event.wait()
        await imu.subscribe()
        while True:
            await asyncio.sleep(60)

def run(address, channel, period, start_event, sem, queue):
    print("TAG", channel, current_process().name)
    return asyncio.run(publish_data_forever(address, channel, period, start_event, sem, queue))

def sync_start(n, start_event, sem):
    print("SYNC     ", current_process().name)
    for _ in range(n):
        sem.acquire()

    time.sleep(0.500)
    print("\nSTART!")
    start_event.set()

def window_inputs_loop(
    fall_stride, fall_window, fall_queue,
    har_stride, har_window, har_queue,
    queue0_in, queue1_in,
    sem, start_event, queue_timeout):

    print("WINDOW   ", current_process().name)

    sem.release()
    start_event.wait()
    har_buffer = list()
    fall_buffer = list()
    har_n = 0
    fall_n = 0
    try:
        while True:
            data0 = queue0_in.get(timeout=queue_timeout)
            data1 = queue1_in.get(timeout=queue_timeout)

            data0.extend(data1)
            fall_buffer.append(data0)
            fall_n += 1
            har_buffer.append(data0)
            har_n += 1

            if har_n == har_window:
                har_queue.put(har_buffer)
                har_n -= har_stride
                har_buffer = har_buffer[har_stride:]
            if fall_n == fall_window:
                fall_queue.put(fall_buffer)
                fall_n -= fall_stride
                fall_buffer = fall_buffer[fall_stride:]
            # print(queue0_in.qsize(), queue1_in.qsize())

    except QueueEmpty:
        print(f"No data from tags after {queue_timeout}s")


def handle_server_response_loop(sem, start_event, response_queue, queue_timeout, response_handler):
    print("RESPONSE   ", current_process().name)
    sem.release()
    start_event.wait()
    try:
        while True:
            request_id, response = response_queue.get(timeout=queue_timeout)
            response_handler(request_id, response)
    except QueueEmpty:
        print(f"No response recieved after {queue_timeout}s")


def phone_on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.subscribe('phoneapp_falling_resp')
        print('Server Successfully Connected to Broker')
    else:
        print("Failed to connect to broker", rc)

def handle_server_response_loop_har(sem, start_event, response_queue, queue_timeout, response_handler):
    print("TO_PHONE   ", current_process().name)
    client = Client()
    client.username_pw_set(MQTT_USER, password=MQTT_PASS)
    client.connect(MQTT_BROKER_HOST)
    client.loop_start
    client.on_connect = phone_on_connect

    sem.release()
    start_event.wait()
    try:
        while True:
            request_id, response = response_queue.get(timeout=queue_timeout)
            label = response_handler(request_id, response)
            client.publish('phone_app', label.encode())

    except QueueEmpty:
        print(f"No response recieved after {queue_timeout}s")

def handle_server_response_loop_fall(sem, start_event, response_queue, queue_timeout, response_handler):
    print("TO_PHONE   ", current_process().name)
    client = Client()
    client.username_pw_set(MQTT_USER, password=MQTT_PASS)
    client.connect(MQTT_BROKER_HOST)
    client.loop_start
    client.on_connect = phone_on_connect

    sem.release()
    start_event.wait()
    try:
        while True:
            request_id, response = response_queue.get(timeout=queue_timeout)
            label = response_handler(request_id, response)
            if response['label'][0][0] == 'falling':
                client.publish('phone_app', 'falling'.encode())


    except QueueEmpty:
        print(f"No response recieved after {queue_timeout}s")

##### TODO:  MODIFY THESE IF NECESSARY ######
def har_response_handler(request_id, response):
    # pass
    label = response['label'][0][0]
    if label.startswith('climb'):
        label = 'climbing'
    print('ACTIVITY', label)
    return label

##### TODO:  MODIFY THESE IF NECESSARY ######
def fall_response_handler(request_id, response):
    label = response['label'][0][0]
    if label == 'falling':
        print('Fall Detected!')
    return label

def make_requests_loop(model, sem, start_event, window_queue, response_queue, queue_timeout):
    print(f"CLIENT({model})", current_process().name)

    def enqueue_repsonse(request_id, response):
        response_queue.put((request_id, response))

    client = ClassificationClient(model, callback=enqueue_repsonse)
    client.start()
    sem.release()
    start_event.wait()
    try:
        while True:
            window = window_queue.get(timeout=queue_timeout)
            window = np.expand_dims(np.stack(window), 0)
            client.request_prediction(window)

    except QueueEmpty:
        print(f"No windows for {model} model")

def make_windowed_requests(period, fall_window, fall_stride, har_window, har_stride):
    wristAddress = ("54:6c:0e:B7:90:84", "5FED95F3-EC32-4D3B-AD80-042D49AC1174")
    waistAddress = ("54:6C:0E:53:35:E2", "DB6C6D52-CD50-45E4-9365-0F2A5697C96E")

    start_event = Event()
    sem = Semaphore(0)
    queue0_in = Manager().Queue()
    queue1_in = Manager().Queue()
    queue_out = Manager().Queue()
    fall_window_queue = Manager().Queue()
    har_window_queue = Manager().Queue()
    fall_resp_queue = Manager().Queue()
    har_resp_queue = Manager().Queue()

    data_consumer_timeout = 6
    fall_window_consumer_timeout = 6
    har_window_consumer_timeout = 6

    processes = []
    # enable both tags
    processes.append(Process( target=run, args=(waistAddress, 0, period, start_event, sem, queue0_in)))
    processes.append(Process(target=run, args=(wristAddress, 1, period, start_event, sem, queue1_in)))

    processes.append(Process(
        target=window_inputs_loop,
        args=(
            fall_stride, fall_window, fall_window_queue,
            har_stride, har_window, har_window_queue,
            queue0_in, queue1_in,
            sem, start_event, data_consumer_timeout
            )))

    processes.append(Process(
        target=make_requests_loop,
        args=(
            'fall_detection',
            sem, start_event,
            fall_window_queue, fall_resp_queue, fall_window_consumer_timeout)))

    processes.append(Process(
        target=make_requests_loop,
        args=(
            'activity_recognition',
            sem, start_event,
            har_window_queue, har_resp_queue, har_window_consumer_timeout)))

    processes.append(Process(
        target=handle_server_response_loop_har,
        args=(sem, start_event, har_resp_queue, har_window_consumer_timeout, har_response_handler)))

    processes.append(Process(
        target=handle_server_response_loop_fall,
        args=(sem, start_event, fall_resp_queue, fall_window_consumer_timeout, fall_response_handler)))

    processes.append(Process(target=sync_start, args=(len(processes), start_event, sem)))

    for p in processes:
        p.start()

    for p in processes:
        p.join()


def main():
    make_windowed_requests(TAG_PERIOD, 25, 5, 50, 5)

if __name__ == "__main__":
    main()
