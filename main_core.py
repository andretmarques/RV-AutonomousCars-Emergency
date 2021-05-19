#!/usr/bin/env python
import sys, time
from threading import Thread, Event
from Queue import *
from message_gen import message_generator
from Custom_Class import *
import random
from User import *

# lock = threading.Lock()
in_multicast_queue = Queue()
out_multicast_queue = Queue()
dataTxQueue = Queue()
in_buffer_queue = Queue()

shared_info = 0
locMessages = []

uid = random.randint(1, 250)


def user_interface(denm_event):
    print("User interface\n")
    t = Thread(target=wait_for_code, args=(denm_event, ))
    t.start()
    user = User(uid, "")
    print("################################", user.id)
    return user


def wait_for_code(denm_event):
    code = ""
    while len(code) != 6:
        code = input("Insert your code: ")

    user = User(uid, code)
    denm_event.set()
    print("################################", user.id, user.code)
    return user


def message_gen(dataTxQueue, denm_event):
    message_generator(dataTxQueue, denm_event)
    return


def tx_buffer():
    print("Transmission buffer\n")
    return


def rx_buffer():
    print("Receptor buffer\n")
    return


def txd_platform(in_multicast_queue, in_buffer_queue, dataTxQueue):
    msg = dataTxQueue.get()
    if not locMessages:
        in_buffer_queue.put(msg)
    else:
        in_multicast_queue.put(msg)
    return


def txd_multicast(in_multicast_queue):
    print('txd_multicast\n')
    msg = dict()
    msg = in_multicast_queue.get()
    print('200 OK {}'.format(msg))
    print('terminating txd_multicast\n')
    return


def rxd_multicast(out_multicast_queue):
    print('rxd_multicast\n')
    time.sleep(1)
    print('terminating txd_multicast\n')
    return


def rxd_platform(out_multicast_queue):
    print('rxd_platform\n')
    print('shared variable {}'.format(shared_info))
    print('terminating xnamed_platform\n')
    return


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
        t = Thread(target=user_interface, args=(denm_event, ))
        t.start()
        threads.append(t)
        print('thread create: user_interface\n')

        t = Thread(target=message_gen, args=(dataTxQueue, denm_event))
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
        t = Thread(target=txd_platform, args=(in_multicast_queue, in_buffer_queue, dataTxQueue))
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
        t = Thread(target=rxd_platform, args=(out_multicast_queue,))
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
