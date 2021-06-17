from datetime import datetime

from Custom_Class import CAM, DENM, BEACON, RepeatedTimer
from Queue import Empty

last_coord = [0, 0, 'N']


def create_and_send_denm(queue, identifier):
    dt = str(datetime.now())
    ttl = 5
    msg = DENM(identifier, True, dt, ttl)
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
    rt = RepeatedTimer(2, create_and_send_denm, queue, identifier)
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
            state = False


def create_and_send_cam_rsu(queue, identifier):
    x = 1
    y = 1
    buss = "N"
    dt = str(datetime.now())
    ttl = 5
    msg = CAM(identifier, x, y, buss, dt, ttl)
    print("Send CAM message")
    add_message_to_queue(queue, msg)
    return msg


def cam_loop_RSU(queue, identifier):
    rt = RepeatedTimer(2, create_and_send_cam_rsu, queue, identifier)
    return rt


def message_generator_rsu(queue, uid):
    identifier = uid
    cam_timer = cam_loop_RSU(queue, identifier)
    beacon_timer = beacon_loop(queue, identifier)


