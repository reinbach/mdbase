# Copyright (c) 2010-2011 iMatix Corporation and Contributors

import binascii
import os

import zmq

def dump(msg):
    """Received all message parts from socket, prints neatly"""
    print("-" * 40)
    for part in msg:
        print("[%03d]" % len(part)),
        print(part)

def zpipe(ctx):
    """Build inproc pipe for talking to threads

    mimic pipe used in czmq zthread_fork.

    Returns a pair of PAIRs connected via inproc
    """
    a = ctx.socket(zmq.PAIR)
    a.linger = 0
    a.set_hwm(1)
    b = ctx.socket(zmq.PAIR)
    b.linger = 0
    b.set_hwm(1)
    iface = "inproc://%s" % binascii.hexlify(os.urandom(8))
    a.bind(iface)
    b.connect(iface)
    return a, b