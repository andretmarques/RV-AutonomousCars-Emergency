from Queue import Queue
import Custom_Class
from datetime import datetime, timedelta

in_multicast_queue = Queue()
out_multicast_queue = Queue()
dataRXQueue = Queue()
locTable = []
locTableIds = []

VALIDITY = timedelta(0, 10)
print(VALIDITY)


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
                update_LocTable(msg.id, msg.time, msg.x, msg.y)

            else:
                locM = Custom_Class.LOCM(msg.id, msg.time, msg.x, msg.y, datetime.now(), VALIDITY)
                locTable.append(locM)
                locTableIds.append(locM.id)

        elif isinstance(msg, Custom_Class.DENM):
            dataRXQueue.put(msg)
    print('terminating xd_platform\n')
    return


def check_mgs_validity(locTable, locTableIds):
    for msg in locTable:
        if msg.time + msg.val > datetime.now():
            locTable.remove(msg)
            locTableIds.remove(msg.id)
    return
