#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from myhdl import *

from components import *
from ula import *
from seq import *


@block
def toplevel(LEDR, SW, KEY, HEX0, HEX1, HEX2, HEX3, HEX4, HEX5, CLOCK_50, RESET_N):
    we, re = [Signal(bool(0)) for _ in range(2)]
    we_wait, re_wait = [Signal(bool(0)) for _ in range(2)]
    din, dout = [Signal(modbv(0)[6:]) for i in range(2)]
    full, empty = [Signal(bool(0)) for i in range(2)]

    fifo1 = fifo(
        dout,
        din,
        we,
        re,
        full,
        empty,
        CLOCK_50,
        RESET_N,
        8,
        32,
    )

    @always_comb
    def comb():
        LEDR[8:].next = dout
        din.next = SW[8:]
        LEDR[9].next = full
        LEDR[8].next = empty

    @always_seq(CLOCK_50.posedge, reset=RESET_N)
    def pulse():
        if (KEY[0] == 0) and (we_wait == 0):
            we.next = 1
            we_wait.next = 1
        elif (KEY[0] == 0) and (we_wait == 1):
            we.next = 0
        else:
            we_wait.next = 0

        if (KEY[1] == 0) and (re_wait == 0):
            re.next = 1
            re_wait.next = 1
        elif (KEY[1] == 0) and (re_wait == 1):
            re.next = 0
        else:
            re_wait.next = 0

    return instances()


LEDR = Signal(intbv(0)[10:])
SW = Signal(intbv(0)[10:])
KEY = Signal(intbv(0)[4:])
HEX0 = Signal(intbv(1)[7:])
HEX1 = Signal(intbv(1)[7:])
HEX2 = Signal(intbv(1)[7:])
HEX3 = Signal(intbv(1)[7:])
HEX4 = Signal(intbv(1)[7:])
HEX5 = Signal(intbv(1)[7:])
CLOCK_50 = Signal(bool())
RESET_N = ResetSignal(0, active=0, isasync=True)

top = toplevel(LEDR, SW, KEY, HEX0, HEX1, HEX2, HEX3, HEX4, HEX5, CLOCK_50, RESET_N)
top.convert(hdl="verilog")
