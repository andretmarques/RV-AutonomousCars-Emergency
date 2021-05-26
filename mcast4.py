#!/usr/bin/env python
# #################################################
## SENDING/RECEIVING MULTICAST
#################################################
import dataclasses
import json
import socket
import struct

from Custom_Class import CAM, DENM, BEACON

PORT = 4261
MYGROUP_4 = '225.0.0.250'
MYTTL = 1  # Increase to reach other networks

MSG_SIZE = 1024


def rxd_multicast(out_multicast_queue):
    print('rxd_multicast')

    r = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    r.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    r.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    r.bind(('', PORT))

    group_bin = socket.inet_pton(socket.AF_INET, MYGROUP_4)
    mreq = group_bin + struct.pack('=I', socket.INADDR_ANY)
    r.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    while True:
        rxd_data, sender = r.recvfrom(MSG_SIZE)
        data = rxd_data.decode(encoding='UTF-8')
        while data[-1:] != '\0':
            i = 0
        data = data[:-1]  # Strip trailing \0's
        data = json.loads(data)
        if data["type"] == "CAM":
            del data["type"]
            data = CAM(**data)
        elif data["type"] == "DENM":
            del data["type"]
            data = DENM(**data)
        elif data["type"] == "BEACON":
            del data["type"]
            data = BEACON(**data)
        out_multicast_queue.put(data)
    return


def txd_multicast(in_multicast_queue):
    print('txd_multicast')

    addrinfo = socket.getaddrinfo(MYGROUP_4, None)[0]
    s = socket.socket(addrinfo[0], socket.SOCK_DGRAM)

    ttl_bin = struct.pack('@I', 1)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl_bin)
    while True:
        data = in_multicast_queue.get()
        if isinstance(data, CAM):
            data = dataclasses.asdict(data)
            data["type"] = "CAM"
        elif isinstance(data, DENM):
            data = dataclasses.asdict(data)
            data["type"] = "DENM"
        elif isinstance(data, BEACON):
            data = dataclasses.asdict(data)
            data["type"] = "BEACON"
        data = json.dumps(data)
        data = data + '\0'
        data_to_send = data.encode(encoding='UTF-8')
        s.sendto(data_to_send, (addrinfo[4][0], PORT))
    return
