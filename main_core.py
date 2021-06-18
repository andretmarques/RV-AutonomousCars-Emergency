#!/usr/bin/env python
import random
import select
import sys
import threading
import time
from threading import Thread, Event, RLock

from Buffer import *
from Custom_Class import *
from DataManagerRx import rxd_platform
from User import User
from mcast4 import rxd_multicast, txd_multicast
from message_gen import message_generator
from Queue import *
from control_services import read_gpio_conf, gpio_init, stop_control, stop_gpio, control_engines


in_multicast_queue = Queue()
out_multicast_queue = Queue()
dataTxQueue = Queue()
to_buffer_queue = Queue()
data_tx_queue = Queue()
data_rx_queue = Queue()
in_buffer_queue = Queue()
in_coord_queue = Queue()

shared_info = 0
locTable = []
locTableIds = []

uid = random.randint(1, 250)


def user_interface(denm_event):
    print("User interface\n")
    user = User(uid, "")
    while True:
        ins, _, _ = select.select([sys.stdin], [], [])
        if ins[0] == sys.stdin:
            code = sys.stdin.readline().strip()
            if len(code) == 6 and user.code == "":
                user = User(uid, code)
                denm_event.set()
                print("################################ User with ID:", user.id, " inserted CODE: ", user.code)
            elif code == "stop":
                denm_event.clear()
                user = User(uid, "")
    return


def readCoor(in_coord_queue, car_event):
    gpio_data = {}
    gpio_data = read_gpio_conf("gpio_pins")
    pwm_motor = {}
    gpio_init(gpio_data, pwm_motor)

    direction = 'forward_dir'

    coord = ['0', '0', 'N']
    x = coord[0]
    y = coord[1]
    buss = coord[2]
    while True:
        # TODO semaphore flag OP

        if buss == 'N':
            y = int(y) + 1
            coord[1] = str(y)
        elif buss == 'S':
            y = int(y) - 1
            coord[1] = str(y)
        elif buss == 'E':
            x = int(x) + 1
            coord[0] = str(x)
        elif buss == 'O':
            x = int(x) - 1
            coord[0] = str(x)
        in_coord_queue.put(coord)

        if not car_event.is_set():
            direction = 'forward_dir'
        else:
            direction = 'stop'
        control_engines(gpio_data, direction, pwm_motor)




def stop_den_messages(denm_event):
    while input() != "stop":
        denm_event.clear()


def message_gen(dataTxQueue, denm_event, uid, in_coord_queue):
    message_generator(dataTxQueue, denm_event, uid, in_coord_queue)
    return


def tx_buffer(to_buffer_queue, in_buffer_queue, in_multicast_queue):
    tx_buffer_decides(to_buffer_queue, in_buffer_queue, in_multicast_queue)
    return


def txd_platform(in_multicast_queue, to_buffer_queue, data_tx_queue):
    while True:
        msg = data_tx_queue.get()

        if type(msg) == BEACON:
            in_multicast_queue.put(msg)

        else:
            if len(locTable) == 0:
                print("Message to Buffer\n")
                to_buffer_queue.put(msg)

            else:
                print("Message sent to Multicast\n")
                in_multicast_queue.put(msg)


def check_mgs_validity(locTable, locTableIds):
    lock = RLock()
    lock.acquire()
    for i in range(len(locTable)):
        if locTable[i].time + locTable[i].val < datetime.now():
            locTableIds.remove(locTableIds[i])
            locTable.remove(locTable[i])
    lock.release()
    return


def check_validity_thread():
    rt = Custom_Class.RepeatedTimer(2, check_mgs_validity, locTable, locTableIds)
    return rt


##################################################
## MAIN-.ITS_core
##################################################
def main(argv):
    threads = []
    print('starting the code \n')
    try:
        print('creating threads \n')
        # these are the treads that you might need to use. They are crated according to the information flow
        denm_event = Event()
        car_event = Event()
        t = Thread(target=user_interface, args=(denm_event,))
        t.start()
        threads.append(t)
        print('thread create: user_interface\n')

        t = Thread(target=readCoor, args=(in_coord_queue,car_event,))
        t.start()
        threads.append(t)
        print('thread create: \n')

        t = Thread(target=message_gen, args=(data_tx_queue, denm_event, uid, in_coord_queue,))
        t.start()
        threads.append(t)
        print('thread create: message_generator\n')

        t = Thread(target=tx_buffer, args=(to_buffer_queue, in_buffer_queue, in_multicast_queue,))
        t.start()
        threads.append(t)
        print('thread create: transmission buffer\n')

        # thread for sending data for transmission
        # arguments: queue to send data to txd_multicast.
        t = Thread(target=txd_platform, args=(in_multicast_queue, to_buffer_queue, data_tx_queue,))
        t.start()
        threads.append(t)
        print('thread create: txd_platform\n')

        # thread for transmission data to other node
        # arguments: queue to receive  data from txd_platform.
        t = Thread(target=txd_multicast, args=(in_multicast_queue,))
        t.start()
        threads.append(t)
        print('thread create: txd_multicast\n')

        # thread for reception from other node
        # arguments: queue to send data  to rxd_platform.
        t = Thread(target=rxd_multicast, args=(out_multicast_queue,))
        t.start()
        threads.append(t)
        print('thread create: rxd_multicast\n')

        # #thread for receiving data from other node
        # # arguments: queue to receive data from rxd_multicast. shared data structure to communicate with txd_platform
        t = Thread(target=rxd_platform,
                   args=(out_multicast_queue, uid, locTable, locTableIds, data_rx_queue, in_multicast_queue, car_event,))
        t.start()
        threads.append(t)
        print('thread create: rxd_platform\n')

        t = Thread(target=check_validity_thread)
        t.start()
        threads.append(t)
        print('thread create: check_validity_thread\n')

    except:
        # exit the program if there is an error when opening one of the threads
        print('Time: {}\tError opening one of the threads. Try again'.format(time.time()))
        for t in threads:
            t.join()
            sys.exit()
    return


if __name__ == "__main__":
    main(sys.argv[0:])
