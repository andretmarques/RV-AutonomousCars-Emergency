#!/usr/bin/env python
# #################################################
## SENDING/RECEIVING MULTICAST
#################################################
import time
import socket
import struct
import sys
from threading import Thread

PORT = 4261
MYGROUP_4 = '225.0.0.250'
MYTTL = 1  # Increase to reach other networks

MSG_SIZE = 1024


def rxd_multicast(version, t):
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
        while data[-1:] == '\0':
            data = data[:-1]  # Strip trailing \0's
            print(str(sender) + '  ' + repr(data))
        return


def txd_multicast(version, t):
    print('txd_multicast')

    addrinfo = socket.getaddrinfo(MYGROUP_4, None)[0]
    s = socket.socket(addrinfo[0], socket.SOCK_DGRAM)

    ttl_bin = struct.pack('@I', 1)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl_bin)
    while True:
        data = repr(time.time()) + '\0'
        data_to_send = data.encode(encoding='UTF-8')
        s.sendto(data_to_send, (addrinfo[4][0], PORT))
        time.sleep(10)
        return


def main(argv=None):
    version = 6
    t = 0
    command = input('Press enter to start')
    threads = []
    print('starting the code \n')
    try:
        print('trying rxd_multicast \n')
        t = Thread(target=rxd_multicast, args=(version, t))
        t.start()
        threads.append(t)
        print('thread create: rxd_multicast\n')

        print('trying txd_multicast \n')
        t = Thread(target=txd_multicast, args=(version, t))
        t.start()
        threads.append(t)
        print('thread create: txd_multicast\n')

    except:
        print('Time: {}\tError opening one of the threads. Try again'.format(time.time()))
        for t in threads:
            t.join()
            sys.exit()
    while True:
        i = 0
        return


if __name__ == "__main__":
    main(sys.argv[0:])
