# Copyright (c) 2010-2011 iMatix Corporation and Contributors

import binascii
import os

import zmq

def dump(msg_or_socket):
    """Received all message parts from socket, prints neatly"""
    if isinstance(msg_or_socket, zmq.Socket):
        # it's a socket, call on current message
        return dump(msg_or_socket.recv_multipart())
    else:
        msg = msg_or_socket

    print("-" * 40)
    for part in msg:
        print("[%03d]" % len(part)),
        print(part)

def socket_set_hwm(socket, hwm=-1):
    """libzmq 2/3 compatible set hwm"""
    try:
        socket.sendhwm = socket.rcvhwm = hwm
    except AttributeError:
        socket.hwm = hwm

def zpipe(ctx):
    """Build inproc pipe for talking to threads

    mimic pipe used in czmq zthread_fork.

    Returns a pair of PAIRs connected via inproc
    """
    a = ctx.socket(zmq.PAIR)
    a.linger = 0
    b = ctx.socket(zmq.PAIR)
    b.linger = 0
    socket_set_hwm(a, 1)
    socket_set_hwm(b, 1)
    iface = "inproc://%s" % binascii.hexlify(os.urandom(8))
    a.bind(iface)
    b.connect(iface)
    return a, b