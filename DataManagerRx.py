from datetime import datetime, timedelta
from threading import RLock

import Custom_Class

VALIDITY = timedelta(0, 10)


def update_LocTable(index, time, locTable):
    locTable[index].time = time
    locTable[index].timestamp = datetime.now()
    locTable[index].val = VALIDITY


def rxd_platform(out_multicast_queue, uid, locTable, locTableIds, data_rx_queue, in_multicast_queue):
    print('rxd_platform\n')

    while True:

        msg = out_multicast_queue.get()

        if isinstance(msg, Custom_Class.CAM) or isinstance(msg, Custom_Class.DENM) or isinstance(msg,
                                                                                                 Custom_Class.BEACON):

            if msg.id == uid:
                continue

            elif msg.ttl > 0:
                msg.ttl = msg.ttl - 1
                in_multicast_queue.put(msg)
                continue

        if isinstance(msg, Custom_Class.CAM) or isinstance(msg, Custom_Class.BEACON):
            lock = RLock()
            lock.acquire()

            if msg.id in locTableIds:
                index = locTableIds.index(msg.id)
                time = datetime.strptime(msg.time, '%Y-%m-%d %H:%M:%S.%f')
                update_LocTable(index, time, locTable)

            else:
                time = datetime.strptime(msg.time, '%Y-%m-%d %H:%M:%S.%f')
                locM = Custom_Class.LOCM(msg.id, time, datetime.now(), VALIDITY)
                locTable.append(locM)
                locTableIds.append(locM.id)
            lock.release()

        elif isinstance(msg, Custom_Class.DENM):
            print("$$$$$$$$$$$$ Received DEM \n\n")

            data_rx_queue.put(msg)
    print('terminating xd_platform\n')
    return
