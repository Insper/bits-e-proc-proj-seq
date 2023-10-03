#!/usr/bin/env python3

import random
import os
import pytest
from myhdl import block, instance, Signal, intbv, delay, bin
from .seq import *
import random

try:
    from telemetry import telemetryMark

    pytestmark = telemetryMark()
except ImportError as err:
    print("Telemetry não importado")


def source(name):
    dir = os.path.dirname(__file__)
    src_dir = os.path.join(dir, ".")
    return os.path.join(src_dir, name)


random.seed(5)
randrange = random.randrange


@pytest.mark.telemetry_files(source("seq.py"))
def test_ram():
    WIDTH = 32
    DEPTH = 16
    din, dout = [Signal(modbv(0)[WIDTH:]) for i in range(2)]
    addr = Signal(modbv(0)[DEPTH:])
    we, clk = [Signal(bool(0)) for i in range(2)]
    rst = ResetSignal(0, active=1, isasync=True)
    ram_inst = ram(dout, din, addr, we, clk, rst, WIDTH, DEPTH)

    @always(delay(1))
    def clkgen():
        clk.next = not clk

    @instance
    def stimulus():
        for i in range(5):
            din.next = i
            addr.next = i
            we.next = 1
            yield clk.negedge

        we.next = 0
        for i in range(5):
            addr.next = i
            yield clk.negedge
            assert addr == i

    sim = Simulation(ram_inst, [stimulus, clkgen])
    traceSignals(ram_inst)
    sim.run(20)


@pytest.mark.telemetry_files(source("seq.py"))
def test_pc():
    WIDTH = 16
    i, output = [Signal(modbv(0)[WIDTH:]) for i in range(2)]
    inc, load, clk = [Signal(bool(0)) for i in range(3)]
    rst = ResetSignal(0, active=1, isasync=True)
    pc_inst = pc(inc, load, i, output, WIDTH, clk, rst)

    @always(delay(10))
    def clkgen():
        clk.next = not clk

    @instance
    def stimulus():
        rst.next = 1
        inc.next = 0
        yield clk.negedge
        assert output == 0

        rst.next = 0
        for n in range(10):
            yield clk.negedge
            assert output == 0

        inc.next = 1
        for n in range(10):
            yield clk.negedge
            assert output == n + 1

        i.next = 32
        load.next = 1
        yield clk.negedge
        assert output == 32

        load.next = 0
        inc.next = 1
        yield clk.negedge
        assert output == 33

    sim = Simulation(pc_inst, [stimulus, clkgen])
    traceSignals(pc_inst)
    sim.run(500)
    sim.quit()


@pytest.mark.telemetry_files(source("seq.py"))
def test_registerN():
    N = 32
    i, output = [Signal(modbv(0)[N:]) for n in range(2)]
    load, clk = [Signal(bool(0)) for n in range(2)]
    rst = ResetSignal(0, active=1, isasync=True)
    regN_inst = registerN(i, load, output, N, clk, rst)

    @always(delay(10))
    def clkgen():
        clk.next = not clk

    @instance
    def stimulus():
        for n in range(32):
            yield clk.negedge
            i.next = randrange(2**N - 1)
            load.next = 1
            yield clk.negedge
            i.next = 0
            load.next = 0
            assert i == output

    sim = Simulation(regN_inst, [stimulus, clkgen])
    traceSignals(regN_inst)
    sim.run(20)


@pytest.mark.telemetry_files(source("seq.py"))
def test_register8():
    i, output = [Signal(modbv(0)[8:]) for i in range(2)]
    load, clk = [Signal(bool(0)) for i in range(2)]
    rst = ResetSignal(0, active=1, isasync=True)
    reg8_inst = register8(i, load, output, clk, rst)

    @always(delay(10))
    def clkgen():
        clk.next = not clk

    @instance
    def stimulus():
        for n in range(10):
            yield clk.negedge
            i.next = randrange(2**8 - 1)
            load.next = 1
            yield clk.negedge
            i.next = 0
            load.next = 0
            assert i == output

    sim = Simulation(reg8_inst, [stimulus, clkgen])
    traceSignals(reg8_inst)
    sim.run(200)


@pytest.mark.telemetry_files(source("seq.py"))
def test_binaryDigit():
    i, load, output, clk = [Signal(bool(0)) for i in range(4)]
    rst = ResetSignal(0, active=1, isasync=True)
    bd_inst = binaryDigit(i, load, output, clk, rst)

    @always(delay(10))
    def clkgen():
        clk.next = not clk

    @instance
    def stimulus():
        assert output == 0
        yield delay(30)
        i.next = 1
        load.next = 1
        yield delay(25)
        assert output == 1
        load.next = 0
        yield delay(25)
        i.next = 0
        load.next = 1
        yield delay(20)
        assert output == 0
        load.next = 0

    sim = Simulation(bd_inst, [stimulus, clkgen])
    traceSignals(bd_inst)
    sim.run(200)


@pytest.mark.telemetry_files(source("seq.py"))
def test_dff():
    q, d, clear, presset, clk = [Signal(bool(0)) for i in range(5)]
    rst = ResetSignal(0, active=1, isasync=True)
    dff_inst = dff(q, d, clear, presset, clk, rst)

    @always(delay(10))
    def clkgen():
        clk.next = not clk

    @always(clk.negedge)
    def stimulus():
        d.next = not q

    @instance
    def cleargen():
        clear.next = 1
        yield delay(20)
        i = 0
        while i < 5:
            assert q == 0
            yield delay(10)
            i = i + 1
        clear.next = 0

    sim = Simulation(dff_inst, [stimulus, clkgen, cleargen])
    traceSignals(dff_inst)
    sim.run(200)


@pytest.mark.telemetry_files(source("seq.py"))
def test_fifo():
    dout, din = [Signal(modbv(0)[10:]) for i in range(2)]
    we, re, empty, full, clk = [Signal(bool(0)) for i in range(5)]
    rst = ResetSignal(0, active=1, isasync=True)
    fifo_inst = fifo(dout, din, we, re, empty, full, clk, rst, 10, 10)

    @always(delay(10))
    def clkgen():
        clk.next = not clk

    @instance
    def test():
        we.next = 0
        re.next = 0

        yield delay(20)
        din.next = 5
        we.next = 1
        yield delay(20)
        din.next = 22
        we.next = 0
        yield delay(20)
        we.next = 1
        yield delay(20)
        we.next = 0
        yield delay(20)
        re.next = 1
        yield delay(20)
        re.next = 0

    sim = Simulation(fifo_inst, [clkgen, test])
    traceSignals(fifo_inst)
    sim.run(400)
