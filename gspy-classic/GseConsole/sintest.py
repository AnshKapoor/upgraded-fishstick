#!/usr/bin/env python
import os
import time
import sys
import struct
import numpy as np
import matplotlib.pyplot as plt
import math
#import TestVector

#tv = TestVector.TestVector()
#tv.data_convert(8, 5, 12)

length = 64
freq = 20
shift = 12

# generate sine test vector
t = np.linspace(0, 2*np.pi, length)
y = np.sin(freq * t)

yf = np.fft.fft(y)
n = len(y)/2+1
freq = np.fft.fftfreq(t.shape[-1])
dt= t[1] - t[0]
fa = 1.0 / dt
x = np.linspace(0, fa/2, n)
#print(t)
#plt.figure(1)
#plt.subplot(2, 1, 1)
plt.plot(abs(yf[:n]))
#plt.plot(freq, yf.real, freq, yf.imag)
#plt.plot(freq, abs(yf))
#plt.subplot(2, 1, 2)
#plt.plot(t, yf.imag)
plt.show()
#print(yf)

# shift values and convert to 32 bit integer
y = y * np.power(2, shift)
y = np.floor(y)
y = np.int32(y)

zf = np.fft.fft(y)

#print(zf)

# build complex vales with imaginary part zero
cf = np.empty((2*y.size,), dtype=y.dtype)
cf[0::2] = zf.real
cf[1::2] = zf.imag

#print(cf)

# build complex vales with imaginary part zero
c = np.empty((2*y.size,), dtype=y.dtype)
c[0::2] = y
c[1::2] = 0

#for i in range(len(c)):
#    print(hex(c[i]))

#c = np.arange(0, 32, 1)
#c.newbyteorder('>')
payload = ''
for i in range(len(c)):
    payload += struct.pack("<i", c[i])
    
#payload = memoryview(c).tobytes()

#for i in range(0, len(payload), 2):
#    print('%0#6x' % struct.unpack('<H', payload[i:i+2])[0])

#print(len(c))
