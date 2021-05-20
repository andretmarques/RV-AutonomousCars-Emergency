from datetime import datetime, timedelta
import Custom_Class
NULL = 0

in_multicast_queue = Queue()
dataRXQueue = Queue()
locTable = []
locTableIds = []
in_buffer_queue = Queue()

validity = timedelta(0, 10)

def isValid (msg, locTable):
    if msg.id in locTableIds:
        if msg.validity > 0:
            return True
        else:
            locTableIds.remove(msg)
            return
    else:
        return False

def in_LocTable_ids(msg, locTable):
    for ids in len(locTable):
        id = ids.id
        locTIds = locTIds.append(id)
    if msg.id in locTIds:
        return True
    else:
        return False

def tx_buffer_decides(to_buffer_queue, in_buffer_queue, in_multicast_queue):
    while True:
        msg_to_buffer = to_buffer_queue.get()
        if isinstance(msg_to_buffer, Custom_Class.CAM) or isinstance(msg_to_buffer, Custom_Class.DENM):
            if msg_to_buffer.id == id:
                pass
            elif isValid(msg_to_buffer):
                updatePktLifetime(msg_to_buffer);
                write_in_buffer(msg_to_buffer)
                pass
        msg_to_transmit = in_buffer_queue.get()
        if isinstance(msg_to_buffer, Custom_Class.CAM) or isinstance(msg_to_buffer, Custom_Class.DENM):
            if msg_to_buffer.id == id:
                pass
            elif isValid(msg_to_transmit):
                updatePktLifetime(msg_to_transmit)
                send_packet(msg_to_transmit)
                pass
    return


def write_in_buffer(packet):
    if in_buffer_queue.full():
        return
    else:
        in_buffer_queue.put(packet)
    return


def remove_buffer_head():
    in_buffer_queue.get()
    return


def send_packet(packet):
    if in_LocTable_ids(packet, locTable):
        in_multicast_queue.put()
    else:
        print("Exceeded packet lifetime. Too late to send packet")
    return


def flush_buffer():
    while not in_buffer_queue.empty():
        packet = in_buffer_queue.get()
        send_packet(in_buffer_queue, packet)
    return


def getPktLifetime(msg):
    return msg.ttl


def updatePktLifetime(msg):
    msg.ttl = msg.ttl - 1
    return msg.ttl


def remainingLifetime(msg):
    return msg.ttl - 1
