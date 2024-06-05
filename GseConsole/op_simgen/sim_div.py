#!/usr/bin/python
import os,sys
import PreprocSim
import numpy as np

s = PreprocSim.PreprocSim('./socw_in.dat')

#data = 'Hallo Welt! bla!'
path_div = [4]

dividend = np.uint32(np.ones(32)) << 8
divider = np.uint32(np.empty(32))
divider[0::4]  = np.uint32(np.ones(8)) << 8
divider[1::4]  = np.uint32(np.ones(8)) << 9
divider[2::4]  = np.uint32(np.ones(8)) << 10
divider[3::4]  = np.uint32(np.ones(8)) << 11

for n in divider:
    print(n)

data1 = bytearray(dividend)
data2 = bytearray(divider)

s.store(data1, 0x0000)
s.store(data2, 0x0010)
s.div(0x0000, 0x0010, 0x0020, 0x10)

s.sim.wait(100, 'us')

s.load(0x0000, 0x10)
