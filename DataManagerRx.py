from Queue import Queue
import Custom_Class
from datetime import datetime, timedelta
import threading

in_multicast_queue = Queue()
out_multicast_queue = Queue()
dataRXQueue = Queue()
locTable = []
locTableIds = []

VALIDITY = timedelta(0, 10)


def update_LocTable(msgId, time, x, y, locTable):
    index = locTable.index(msgId)
    locTable[index].time = time
    locTable[index].x = x
    locTable[index].y = y
    locTable[index].timestamp = datetime.now()
    locTable[index].val = VALIDITY


def rxd_platform(out_multicast_queue, id, locTable, locTableIds):
    print('rxd_platform\n')

    while True:
        msg = out_multicast_queue.get()
        if isinstance(msg, Custom_Class.CAM) or isinstance(msg,
                                                           Custom_Class.DENM):
            if msg.id == id:
                pass

            elif msg.ttl > 0:
                msg.ttl = msg.ttl - 1
                in_multicast_queue.put(msg)
                pass

        elif isinstance(msg, Custom_Class.CAM) and msg.ttl == 0:
            if msg.id in locTableIds:
                lock = threading.Lock()
                update_LocTable(msg.id, msg.time, msg.x, msg.y, locTable)
                lock.release()

            else:
                locM = Custom_Class.LOCM(msg.id, msg.time, msg.x, msg.y, datetime.now(), VALIDITY)
                lock = threading.Lock()
                locTable.append(locM)
                locTableIds.append(locM.id)
                lock.release()

        elif isinstance(msg, Custom_Class.DENM):
            dataRXQueue.put(msg)
    print('terminating xd_platform\n')
    return


def check_mgs_validity(locTable, locTableIds):
    for msg in locTable:
        if msg.time + msg.val > datetime.now():
            lock = threading.Lock()
            locTable.remove(msg)
            locTableIds.remove(msg.id)
            lock.release()
    return


def check_validity_thread():
    rt = Custom_Class.RepeatedTimer(2, check_mgs_validity, locTable, locTableIds)
    return rt
