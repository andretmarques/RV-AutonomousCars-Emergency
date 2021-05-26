from datetime import datetime, timedelta

import Custom_Class
from main_core import in_buffer_queue

NULL = 0
VALID = 10


def isValid(msg):
    if datetime.now() - datetime.strptime(msg.time, '%Y-%m-%d %H:%M:%S.%f') >= timedelta(0, VALID):
        return False
    else:
        return True


def tx_buffer_decides(to_buffer_queue, in_buffer_queue, in_multicast_queue):
    while True:
        msg_to_buffer = to_buffer_queue.get()
        if isinstance(msg_to_buffer, Custom_Class.CAM) or isinstance(msg_to_buffer, Custom_Class.DENM):
            if isValid(msg_to_buffer):
                write_in_buffer(msg_to_buffer)
        msg_to_transmit = in_buffer_queue.get()
        if isinstance(msg_to_transmit, Custom_Class.CAM) or isinstance(msg_to_transmit, Custom_Class.DENM):
            if isValid(msg_to_transmit):
                updatePktLifetime(msg_to_transmit)
                in_multicast_queue.put(msg_to_transmit)
    return


def write_in_buffer(packet):
    if in_buffer_queue.full():
        return
    else:
        in_buffer_queue.put(packet)
    return


def remove_buffer_head():
    in_buffer_queue.get()
    print("Removed from buffer.\n")
    return


def getPktLifetime(msg):
    return msg.ttl


def updatePktLifetime(msg):
    msg.ttl = msg.ttl - 1
    return msg.ttl


def remainingLifetime(msg):
    return msg.ttl - 1
