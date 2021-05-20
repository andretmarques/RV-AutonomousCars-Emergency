from Queue import Queue
import Custom_Class
from datetime import datetime, timedelta
from threading import RLock
VALIDITY = timedelta(0, 10)



def update_LocTable(index, time, x, y, locTable):
    locTable[index].time = time
    locTable[index].x = x
    locTable[index].y = y
    locTable[index].timestamp = datetime.now()
    locTable[index].val = VALIDITY


def rxd_platform(out_multicast_queue, uid, locTable, locTableIds, data_rx_queue, in_multicast_queue):
    print('rxd_platform\n')

    while True:
        print(" LOCTABLE ", str(locTable), "\n\n")

        msg = out_multicast_queue.get()

        if isinstance(msg, Custom_Class.CAM) or isinstance(msg,
                                                           Custom_Class.DENM):

            if msg.id == uid:
                continue

            elif msg.ttl > 0:
                msg.ttl = msg.ttl - 1
                in_multicast_queue.put(msg)
                continue

        if isinstance(msg, Custom_Class.CAM):
            print("\n\n$$$$$$$$$$$$ CAM ", msg)
            lock = RLock()
            lock.acquire()

            if msg.id in locTableIds:
                index = locTableIds.index(msg.id)
                time = datetime.strptime(msg.time, '%Y-%m-%d %H:%M:%S.%f')
                update_LocTable(index, time, msg.x, msg.y, locTable)

            else:
                time = datetime.strptime(msg.time, '%Y-%m-%d %H:%M:%S.%f')
                locM = Custom_Class.LOCM(msg.id, time, msg.x, msg.y, datetime.now(), VALIDITY)
                locTable.append(locM)
                locTableIds.append(locM.id)
            lock.release()

        elif isinstance(msg, Custom_Class.DENM):
            print("$$$$$$$$$$$$ DEM ", msg, "\n\n")

            data_rx_queue.put(msg)
    print('terminating xd_platform\n')
    return
