import socket
import os
import time
import sys
import struct
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

from SpaceWire import *
from sophilib import Preproc
from sophilib import TestVector

class Cmd_Preproc():

	def __init__(self, spw):
                self.spw = spw
                self.preproc = Preproc(self.spw)
		
        def do_preproc_store(self, prm):
                p_list = prm.split()

                if(len(p_list) < 1):
                        dpu_filename = 'store.raw'
                        start_addr = 0
                        length = 0x40000
                elif(len(p_list) < 2):
                        dpu_filename = p_list[0]
                        start_addr = 0
                        length = 0x40000
                elif(len(p_list) < 3):
                        dpu_filename = p_list[0]
		        start_addr = int(p_list[1], 0)
                        length = 0x40000
                else:
                        dpu_filename = p_list[0]
                        start_addr = int(p_list[1], 0)
                        length     = int(p_list[2], 0)

                self.preproc.store(dpu_filename, start_addr, length)
		
	def do_preproc_load(self, prm):
                p_list = prm.split()
                
                if(len(p_list) < 1):
                        start_addr = 0
                        length = 0x40000
                elif(len(p_list) < 2):
		        start_addr = int(p_list[0], 0)
                        length = 0x40000
                else:
                        start_addr = int(p_list[0], 0)
                        length     = int(p_list[1], 0)

                self.preproc.load(start_addr, length)      
		
        def do_preproc_feed(self, prm):
                testvector = TestVector()
                testvector.gen_sindata(512, [7, 50], 6)
                #testvector.image('testdata/QM2.png', 0)
                self.preproc.store_direct(testvector.payload)
                #testvector.image('testdata/sin8d.gif', 0)
                #self.preproc.store_direct(testvector.payload, 0x40000)

        def do_fft_run(self, prm):
                p_list = prm.split()
                
                if(len(p_list) < 1):
                        offset = 0
                else:
		        offset = int(p_list[0], 0)

                #vertical = (p_list[1] == 'True')
                
                self.preproc.fft(offset, 0x40000+offset, 512, 1)

        def do_ifft_run(self, prm):
                p_list = prm.split()
                
                if(len(p_list) < 1):
                        offset = 0
                else:
		        offset = int(p_list[0], 0)

                vertical = (p_list[1] == 'True')
                
                self.preproc.ifft(offset, 0x40000+offset, 512, 512, vertical)
                
        def do_fft_eval(self, prm):
                self.spw.download_file('fimage.raw')

                data = TestVector.gen_rearrange(self.spw.downdata)
                #for i in range(0, len(data), 2):
                #        print(hex(struct.unpack('<H', data[i:i+2])[0]))
                        
                ac = np.frombuffer(data, np.uint32)
                bc = ac.astype(np.float) / np.power(2, 6)
                #print(bc[0])
                #print(bc[1])
                #print(bc[2])
                #print(bc[3])
                bc = bc[0:1024]
                z = np.empty(512, np.complex)
                z.imag = bc[0::2]
                z.real = bc[1::2]
                #print(z)

                length = 512
                f1 = 7
                f2 = 50
                shift = 6

                # generate sine test vector
                t = np.linspace(0, 2*np.pi, length)
                y = 2 + np.sin(f1 * t) + np.sin(f2 * t)

                yf = np.fft.fft(y)
                #print(yf)

                n = len(yf)/2+1
                
                plt.figure(1)
                plt.subplot(2, 1, 1)
                plt.plot(yf.imag, 'blue')
                plt.subplot(2, 1, 2)
                plt.plot(z.imag, 'red')
                #plt.plot(z.real)
                #plt.plot(y.real)
                plt.show()

        def do_image(self, prm):
                data = self.spw.download_file('image.raw')
                c = np.frombuffer(data, np.uint16)
                c = c.reshape((2048, 2048))
                bc = c.astype(np.float32)
                mpimg.imsave('image.png', bc, cmap='gray');
                plt.imshow(bc, cmap='gray')
                plt.show()

        def do_cimage(self, prm):
                data = self.spw.download_file('fimage.raw')
                TestVector.ret_image(data, 0)

        def do_testimage(self, prm):
                data = np.arange(0, 2048*2048, dtype=np.uint16)
                self.spw.upload_data('image.raw', data)

        def do_sinimage(self, prm):
                testvector = TestVector()
                testvector.gen_sindata2(512, [5, 50], 0)
             
