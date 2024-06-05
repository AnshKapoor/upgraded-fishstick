#!/usr/bin/python

import socket
import cmd 
import os
import time
import sys
import struct
import thread
import threading
import time

import rmap_crc8
from spw_drv import *

class RmapTest(object):

        def __init__(self, tcp_ip='127.0.0.1',\
                     tcp_port=3000,spw_dest_addr=45):

                self.bridge = SpaceWireBridgeShimafuji(tcp_ip, tcp_port)
                #self.bridge = SpaceWireBridgeGresb('134.169.116.207', 3010)
                self.bridge.open()
                
                #thread.start_new_thread(self.receive_thread, ())
                
        def __del__(self):
                self.bridge.close()
        
        def rmap_write(self, addr, sdata):
                length = len(sdata)
                header = '\x45'  # destination
                header += '\x01' # protocol id
                header += '\x71' # write
                header += '\x00' # destination key
                header += '\x00\x00\x00\x20' # reply address
                header += '\x20' # initiator logical addr.
                header += '\x00\x00' # transaction id
                header += '\x00' # external address
                header += struct.pack('>I', addr) # rmap address
                header += struct.pack('>I', length & 0xffffff)[1:] # length
                
                hash = rmap_crc8.crc8()
                hash.update(header)
                header += hash.digest() # crc
                
                payload = header[1:]
                payload += sdata
                
                hash_data = rmap_crc8.crc8()
                hash_data.update(sdata)
                payload += hash_data.digest()
                
                self.bridge.send(0x45, payload)
                
        def rmap_read(self, addr, length):
                header = '\x45'  # destination
                header += '\x01' # protocol id
                header += '\x4d' # read
                header += '\x00' # destination key
                header += '\x00\x00\x00\x20' # reply address
                header += '\x20' # initiator logical addr.
                header += '\x00\x00' # transaction id
                header += '\x00' # external address
                header += struct.pack('>I', addr) # rmap address
                header += struct.pack('>I', length & 0xffffff)[1:] # length
                
                hash = rmap_crc8.crc8()
                hash.update(header)
                header += hash.digest() # crc
                
                payload = header[1:]
                
                self.bridge.send(0x45, payload)

                data = self.bridge.receive()

                hash_data = rmap_crc8.crc8()
                hash_data.update(data[13:-1])

                if(hash_data.digest() == data[-1]):
                        return data[13:-1]
                else:
                        return ''
                
                        
spw = RmapTest('134.169.116.99', tcp_port=10029)

# Wait until filesystem mounted
invalid = 1
while invalid != 0:
        data = spw.rmap_read(0xA0000008, 4)
        invalid = struct.unpack('>L', data)[0]
        #print(invalid)
        time.sleep(1)
        
fat0 = struct.unpack('>L', spw.rmap_read(0xa0000000, 0x04))[0]
fat1 = struct.unpack('>L', spw.rmap_read(0xa0000004, 0x04))[0]

print('FAT0 at: ' + str(hex(fat0))),
print('FAT1 at: ' + str(hex(fat1)))
#for i in range(len(data)):
#        print(str(hex(ord(data[i]))))

while True:
        time.sleep(0.5)

        data = 0
        pos = 0
        count = 0
        print(chr(27) + "[2J")
        for i in range(65536):
                data = spw.rmap_read(fat1 + pos, 40)
                fileId = struct.unpack('>L', data[0:4])[0]
                if fileId != 0xffffffff:
                        count = count + 1
                        print(pos),
                        print('  '),
                        for i in range(len(data)):
                                print('%02x'%ord(data[i])),
                        print('')
                if count > 15:
                        break
                pos = pos + 40
        


#spw.rmap_write(0x40000000, '\xaf\xfe\xaf\xfe')
#data = spw.rmap_read(0x40000000, 0x04)

#for i in range(len(data)):
#        print(str(hex(ord(data[i]))))

#data = struct.unpack('>L', spw.rmap_read(0x20000004, 0x04))[0]

#if(data & 0x80):
#        data = data & 0xffffff7f
#else:
#        data = data | 0x80

#spw.rmap_write(0x20000004, struct.pack('>L', data))

