#!/usr/bin/env python
import sys
import time
from threading import Thread, Event, Lock
from message_gen import message_generator
import random
from User import User
from Queue import *
import Custom_Class
from datetime import datetime, timedelta
from DataManagerRx import rxd_platform
from mcast4 import rxd_multicast, txd_multicast

# lock = threading.Lock()
in_multicast_queue = Queue()
out_multicast_queue = Queue()
data_tx_queue = Queue()
data_rx_queue = Queue()
in_buffer_queue = Queue()

shared_info = 0
locTable = []
locTableIds = []

uid = random.randint(1, 250)


def user_interface(denm_event):

    print("User interface\n")
    tDEN = Thread(target=wait_for_code, args=(denm_event,))
    tDEN.start()

    tStop = Thread(target=stop_den_messages, args=(denm_event,))
    tStop.start()
    user = User(uid, "")
    print("################################ User has ID:", user.id)

    tDEN.join()
    tStop.join()
    return


def wait_for_code(denm_event):
    code = ""
    while len(code) != 6:
        code = input("Insert your code: ")

    user = User(uid, code)
    denm_event.set()
    print("################################ User with ID:", user.id, " inserted CODE: ", user.code)
    return


def stop_den_messages(denm_event):
    while input() != "stop":
        denm_event.clear()


def message_gen(dataTxQueue, denm_event):
    message_generator(dataTxQueue, denm_event)
    return


def tx_buffer():
    print("Transmission buffer\n")
    return


def rx_buffer():
    print("Receptor buffer\n")
    return


def txd_platform(in_multicast_queue, in_buffer_queue, data_tx_queue):
    while True:
        msg = data_tx_queue.get()
        if len(locTable) != 0:
            print("Message to Buffer\n")
            in_buffer_queue.put(msg)
        else:
            locTable.clear()
            locTableIds.clear()
            print("Message sent to Multicast\n")
            in_multicast_queue.put(msg)


def check_mgs_validity(locTable, locTableIds):
    for msg in locTable:
        if msg.time + msg.val > datetime.now():
            lock = Lock()
            locTable.remove(msg)
            locTableIds.remove(msg.id)
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
        t = Thread(target=user_interface, args=(denm_event,))
        t.start()
        threads.append(t)
        print('thread create: user_interface\n')

        t = Thread(target=message_gen, args=(data_tx_queue, denm_event))
        t.start()
        threads.append(t)
        print('thread create: message_generator\n')

        t = Thread(target=tx_buffer, args=())
        t.start()
        threads.append(t)
        print('thread create: transmission buffer\n')

        t = Thread(target=rx_buffer, args=())
        t.start()
        threads.append(t)
        print('thread create: receptor buffer\n')

        # thread for sending data for transmission
        # arguments: queue to send data to txd_multicast.
        t = Thread(target=txd_platform, args=(in_multicast_queue, in_buffer_queue, data_tx_queue))
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
        t = Thread(target=rxd_platform, args=(out_multicast_queue, uid, locTable, locTableIds, data_rx_queue, in_multicast_queue))
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
