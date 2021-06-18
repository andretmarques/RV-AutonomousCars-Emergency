from Queue import Queue
import Custom_Class
from datetime import datetime, timedelta
from threading import RLock

VALIDITY = timedelta(0, 10)


def update_LocTable(index, time, locTable):
    locTable[index].time = time
    locTable[index].timestamp = datetime.now()
    locTable[index].val = VALIDITY


def rxd_platform(out_multicast_queue, uid,locTable, locTableIds, data_rx_queue, in_multicast_queue, car_event):
    print('rxd_platform\n')

    while True:

        msg = out_multicast_queue.get()

        if isinstance(msg, Custom_Class.CAM) or isinstance(msg, Custom_Class.DENM) \
                or isinstance(msg, Custom_Class.BEACON) or isinstance(msg, Custom_Class.CAMSEM):

            if msg.id == uid:
                continue

            elif msg.ttl > 0:
                msg.ttl = msg.ttl - 1
                in_multicast_queue.put(msg)
                continue

        if isinstance(msg, Custom_Class.CAM) or isinstance(msg, Custom_Class.BEACON) \
                or isinstance(msg, Custom_Class.CAMSEM):
            # if isinstance(msg, Custom_Class.CAM) or isinstance(msg, Custom_Class.CAMSEM):
            #     print("####################CAM#####################################")
            #     print(msg)
            #     print("####################END_CAM#################################")

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

            if isinstance(msg, Custom_Class.CAMSEM):
                if msg.buss == "O" and msg.state == "RED":
                    car_event.set()
                elif msg.buss == "O" and (msg.state == "GREEN" or msg.state == "EMS"):
                    car_event.clear()


        elif isinstance(msg, Custom_Class.DENM):
            print("$$$$$$$$$$$$ Received DEM \n\n")

            data_rx_queue.put(msg)
    print('terminating xd_platform\n')
    return


def rxd_platform_RSU(out_multicast_queue, ems_timer1, ems_timer2, ems_timer3, ems_timer4,
                     uid, locTable, locTableIds, data_rx_queue, in_multicast_queue):
    print('rxd_platform\n')
    id = -1

    while True:

        msg = out_multicast_queue.get()

        if isinstance(msg, Custom_Class.CAM) or isinstance(msg, Custom_Class.DENM) \
                or isinstance(msg, Custom_Class.BEACON) or isinstance(msg, Custom_Class.CAMSEM):

            if msg.id == uid:
                continue

            elif msg.ttl > 0:
                msg.ttl = msg.ttl - 1
                in_multicast_queue.put(msg)
                continue

        if isinstance(msg, Custom_Class.CAM) or isinstance(msg, Custom_Class.BEACON) \
                or isinstance(msg, Custom_Class.CAMSEM):
            # if isinstance(msg, Custom_Class.CAM):
            #     print("####################CAM#####################################")
            #     print(msg)
            #     print("####################END_CAM#################################")

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

            if isinstance(msg, Custom_Class.CAM) and msg.id == id:
                check_EMS(msg, ems_timer1, ems_timer2, ems_timer3, ems_timer4)


        elif isinstance(msg, Custom_Class.DENM):
            if msg.state:
                id = int(msg.id)
                print("##########################################")
                print("ID= ", id)
            else:
                id = -1
                ems_timer1.clear()
                ems_timer2.clear()
                ems_timer3.clear()
                ems_timer4.clear()

            data_rx_queue.put(msg)
    print('terminating xd_platform\n')
    return


def check_EMS(msg, ems_timer1, ems_timer2, ems_timer3, ems_timer4):
    if int(msg.x) < 150 and msg.buss == "E":
        ems_timer1.set()
    elif int(msg.x) > 225 and msg.buss == "O":
        ems_timer3.set()
    elif int(msg.y) < 150 and msg.buss == "N":
        ems_timer2.set()
    elif int(msg.y) > 225 and msg.buss == "S":
        ems_timer4.set()
