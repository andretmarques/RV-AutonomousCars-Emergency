from datetime import datetime
from time import sleep

from Custom_Class import CAM, DENM, BEACON, RepeatedTimer
from Queue import *

from threading import Event, Thread


def create_and_send_denm(queue, identifier):
    dt = str(datetime.now())
    ttl = 5
    msg = DENM(identifier, True, dt, ttl)
    print("Send DENM message")
    add_message_to_queue(queue, msg)
    return msg


def create_and_send_cam(queue, identifier, x, y):
    dt = str(datetime.now())
    ttl = 5
    msg = CAM(identifier, x, y, dt, ttl)
    print("Send CAM message")
    add_message_to_queue(queue, msg)
    return msg


def create_and_send_beacon(queue, identifier):
    dt = str(datetime.now())
    ttl = 5
    msg = BEACON(identifier, dt, ttl)
    print("Send BEACON message")
    add_message_to_queue(queue, msg)
    return msg


def add_message_to_queue(queue, msg):
    queue.put(msg)
    print(msg.time)
    return


def cam_loop(queue, identifier, x, y):
    rt = RepeatedTimer(2, create_and_send_cam, queue, identifier, x, y)
    return rt


def beacon_loop(queue, identifier):
    rt = RepeatedTimer(2, create_and_send_beacon, queue, identifier)
    return rt


def denm_loop(queue, identifier):
    rt = RepeatedTimer(2, create_and_send_denm, queue, identifier)
    rt.stop()
    return rt


def message_generator(queue, event, uid):
    state = False
    identifier = uid
    cam_timer = cam_loop(queue, identifier, 0, 0)
    beacon_timer = beacon_loop(queue, identifier)
    denm_timer = denm_loop(queue, identifier)

    while True:
        while event.is_set():
            if not state:
                print()
                print("========== Starting DENM ==========")
                print()
                denm_timer.start()
                state = True
        if state:
            print()
            print("========== Stopping DENM ==========")
            print()
            denm_timer.stop()
            state = False









