#!/usr/bin/env python
import random
import select
import sys
import threading
import time
from threading import Thread, Event, RLock

from Buffer import *
from Custom_Class import *
from DataManagerRx import rxd_platform_RSU
from User import User
from mcast4 import rxd_multicast, txd_multicast
from message_gen import message_generator, message_generator_rsu
from semaphore_control import master

from Queue import *

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


def message_gen(dataTxQueue, uid, sem_event, emsH_event, emsV_event, ems_event):
    message_generator_rsu(dataTxQueue, uid, sem_event, emsH_event, emsV_event, ems_event)
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



##################################################
## MAIN-.ITS_core
##################################################
def main(argv):
    threads = []
    print('starting the code \n')
    try:
        print('creating threads \n')
        # these are the treads that you might need to use. They are crated according to the information flow
        ems_timer1 = Event()
        ems_timer2 = Event()
        ems_timer3 = Event()
        ems_timer4 = Event()

        sem_event = Event()
        emsH_event = Event()
        emsV_event = Event()
        ems_event = Event()

        t = Thread(target=message_gen, args=(data_tx_queue, uid, sem_event, emsH_event, emsV_event, ems_event,))
        t.start()
        threads.append(t)
        print('thread create: message_generator\n')

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
        t = Thread(target=rxd_platform_RSU,
                   args=(out_multicast_queue, ems_timer1, ems_timer2, ems_timer3, ems_timer4, uid, locTable,
                         locTableIds, data_rx_queue, in_multicast_queue,))
        t.start()
        threads.append(t)
        print('thread create: rxd_platform\n')

        # #thread for receiving data from other node
        # # arguments: queue to receive data from rxd_multicast. shared data structure to communicate with txd_platform
        t = Thread(target=master,
                   args=(ems_timer1, ems_timer2, ems_timer3, ems_timer4, sem_event, emsH_event, emsV_event, ems_event,))
        t.start()
        threads.append(t)
        print('thread create: rxd_platform\n')

    except:
        # exit the program if there is an error when opening one of the threads
        print('Time: {}\tError opening one of the threads. Try again'.format(time.time()))
        for t in threads:
            t.join()
            sys.exit()
    return


if __name__ == "__main__":
    main(sys.argv[0:])
