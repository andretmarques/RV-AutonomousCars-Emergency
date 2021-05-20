from Queue import Queue
import Custom_Class
from datetime import datetime, timedelta
import threading

VALIDITY = timedelta(0, 10)


def update_LocTable(msgId, time, x, y, locTable):
    index = locTable.index(msgId)
    locTable[index].time = time
    locTable[index].x = x
    locTable[index].y = y
    locTable[index].timestamp = datetime.now()
    locTable[index].val = VALIDITY


def rxd_platform(out_multicast_queue, uid, locTable, locTableIds, data_rx_queue, in_multicast_queue):
    print('rxd_platform\n')

    while True:
        msg = out_multicast_queue.get()

        if isinstance(msg, Custom_Class.CAM) or isinstance(msg,
                                                           Custom_Class.DENM):
            if msg.id == uid:
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
            data_rx_queue.put(msg)
    print('terminating xd_platform\n')
    return

