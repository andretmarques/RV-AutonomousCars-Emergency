from datetime import datetime

from Custom_Class import CAM, DENM, BEACON, RepeatedTimer, CAMSEM
from Queue import Empty

last_coord = [0, 0, 'N']


def create_and_send_denm(queue, identifier, state):
    dt = str(datetime.now())
    ttl = 5
    msg = DENM(identifier, state, dt, ttl)
    print("Send DENM message")
    add_message_to_queue(queue, msg)
    return msg


def create_and_send_cam(queue, identifier, in_coord_queue):
    global last_coord
    try:
        coord = in_coord_queue.get(block=False)
        last_coord = coord
    except Empty:
        coord = last_coord
    dt = str(datetime.now())
    ttl = 5
    msg = CAM(identifier, coord[0], coord[1], coord[2], dt, ttl)
    print("Send CAM message")
    add_message_to_queue(queue, msg)
    return msg


def create_and_send_beacon(queue, identifier):
    dt = str(datetime.now())
    ttl = 5
    msg = BEACON(identifier, dt, ttl)
    print("Send BEACON message")
    add_message_to_queue(queue, msg)
    return msg


def add_message_to_queue(queue, msg):
    queue.put(msg)
    return


def cam_loop(queue, identifier, in_coord_queue):
    rt = RepeatedTimer(2, create_and_send_cam, queue, identifier, in_coord_queue)
    return rt


def beacon_loop(queue, identifier):
    rt = RepeatedTimer(2, create_and_send_beacon, queue, identifier)
    return rt


def denm_loop(queue, identifier):
    rt = RepeatedTimer(2, create_and_send_denm, queue, identifier, True)
    rt.stop()
    return rt


def message_generator(queue, event, uid, in_coord_queue):
    state = False
    identifier = uid
    cam_timer = cam_loop(queue, identifier, in_coord_queue)
    beacon_timer = beacon_loop(queue, identifier)
    denm_timer = denm_loop(queue, identifier)

    while True:
        while event.is_set():
            if not state:
                print()
                print("========== Starting DENM ==========")
                print()
                denm_timer.start()
                state = True
        if state:
            print()
            print("========== Stopping DENM ==========")
            print()
            denm_timer.stop()
            create_and_send_denm(queue, identifier, False)
            state = False


def create_and_send_cam_rsu(queue, identifier, sem_event, emsH_event, emsV_event, ems_event):
    x = [150, 225, 225, 150]
    y = [150, 150, 225, 225]
    buss = ["O", "S", "E", "N"]
    dt = str(datetime.now())
    ttl = 5
    state = check_state(sem_event, emsH_event, emsV_event, ems_event)
    msg1 = CAMSEM(identifier, x[0], y[0], buss[0], dt, ttl, state[0])
    msg2 = CAMSEM(identifier, x[1], y[1], buss[1], dt, ttl, state[1])
    msg3 = CAMSEM(identifier, x[2], y[2], buss[2], dt, ttl, state[2])
    msg4 = CAMSEM(identifier, x[3], y[3], buss[3], dt, ttl, state[3])
    print("Send CAM message")
    add_message_to_queue(queue, msg1)
    add_message_to_queue(queue, msg2)
    add_message_to_queue(queue, msg3)
    add_message_to_queue(queue, msg4)
    return 0


def check_state(sem_event, emsH_event, emsV_event, ems_event):
    if ems_event.is_set():
        if not emsH_event.is_set() and not emsV_event.is_set():
            return ["EMS", "RED", "RED", "RED"]
        elif not emsH_event.is_set() and emsV_event.is_set():
            return ["RED", "RED", "EMS", "RED"]
        elif emsH_event.is_set() and not emsV_event.is_set():
            return ["RED", "EMS", "RED", "RED"]
        elif emsH_event.is_set() and emsV_event.is_set():
            return ["RED", "RED", "RED", "EMS"]
    else:
        if not sem_event.is_set():
            return ["GREEN", "RED", "GREEN", "RED"]
        elif sem_event.is_set():
            return ["RED", "GREEN", "RED", "GREEN"]


def cam_loop_RSU(queue, identifier, sem_event, emsH_event, emsV_event, ems_event):
    rt = RepeatedTimer(2, create_and_send_cam_rsu, queue, identifier, sem_event, emsH_event, emsV_event, ems_event)
    return rt


def message_generator_rsu(queue, uid, sem_event, emsH_event, emsV_event, ems_event):
    identifier = uid
    cam_timer = cam_loop_RSU(queue, identifier, sem_event, emsH_event, emsV_event, ems_event)
    beacon_timer = beacon_loop(queue, identifier)
