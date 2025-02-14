#!/usr/bin/python

import socket
import thread
import struct
from spw_drv import *

class Wrapper(object):
    def __init__(self):
        self.bridge = SpaceWireBridgeShimafuji('134.169.116.99', tcp_port=10029)
        self.bridge.open()
        self.s_rx = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s_tx = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.s_rx.bind(("", 3002))
        self.s_tx.bind(("", 3003))
        self.s_rx.listen(1)
        self.s_tx.listen(1)
        self.conn = False

        self.komm_rx, addr = self.s_rx.accept()
        self.komm_tx, addr = self.s_tx.accept()
        self.conn = True
        print('GRMON connected')

        thread.start_new_thread(self.grmon2bridge_thread, ())
        thread.start_new_thread(self.bridge2grmon_thread, ())

    def grmon2bridge_thread(self):
        while True: 
            data = ''
            header = ''
            try:
                while(len(header) < 4):
                    header += self.komm_rx.recv(4)
                    length = struct.unpack('>L', header[0:4])[0] & 0x00ffffff
                while(len(data) < length):
                    data += self.komm_rx.recv(1)
                
                if data:
                    self.bridge.send(data)
                    #print(len(data))
            except:
                self.conn = False
                break
                    
    def bridge2grmon_thread(self):       
        cnt = 0
        while True:
            message = self.bridge.receive()

            if message[0] == '\x20':
                length = len(message)
                if length > 0:
       	            payload = struct.pack('>I', length)
	            #payload += struct.pack('>B', )
	            payload += message
                    #print(str(hex(ord(message[0]))))
                    if self.conn:
                        self.komm_tx.send(payload)
                        cnt = cnt + 1
                        #print(length)
                    else:
                        break
        

w = Wrapper()
while(w.conn == True):
    pass

