import os
import sys
import struct
from Telecommand import *
from RamFs import *
import time

class Preproc():

	def __init__(self, spw):
                self.spw = spw
                self.fft_sizes = [64, 128, 256, 512, 1024, 2048]
                self.ramfs = RamFs(self.spw)

        def store(self, dpu_filename, dest_addr=0, length=0x40000):
                parameters = struct.pack('>I', dest_addr)
		parameters += struct.pack('>I', length)
		parameters += dpu_filename
                parameters += '\x00'
                self.spw.events.SoCWTxDone.clear()
		self.spw.cmd(SpwCmdGrp.Preproc, PreprocCmds.Store, parameters)
                self.spw.events.SoCWTxDone.wait(60.0)

        def store_direct(self, data, dest_addr=0):
                fillup = len(data) % 8
                if(fillup > 0):
                        data += '\x00' * (8 - fillup)
                self.spw.upload_data('store.raw', data)
                self.store('store.raw', dest_addr, len(data)/8)
                self.ramfs.delete('store.raw')

        def load(self, start_addr, length):
                parameters = struct.pack('>I', start_addr)
		parameters += struct.pack('>I', length)
                self.spw.events.SoCWRxDone.clear()
		self.spw.cmd(SpwCmdGrp.Preproc, PreprocCmds.Load, parameters)
                self.spw.events.SoCWRxDone.wait(60.0)

        def load_direct(self, start_addr, length):
                self.load(start_addr, length)
                data = self.spw.download_file('fimage.raw')
                self.ramfs.delete('fimage.raw')
                return data

        def load_to_nand(self, start_addr, length, part, file_num):
                parameters = struct.pack('>I', start_addr)
		parameters += struct.pack('>I', length)
                parameters += struct.pack('>B', part)
                parameters += struct.pack('>I', file_num)
                
                self.spw.events.NandDone.clear()
		self.spw.cmd(SpwCmdGrp.Preproc, PreprocCmds.LoadToNand, parameters)
                self.spw.events.NandDone.wait(10*60)
                
        def add(self, read1_addr=0, read2_addr=0,\
                write_addr=0, length=0x40000):

                payload = struct.pack('>I', read1_addr)
		payload += struct.pack('>I', read2_addr)
                payload += struct.pack('>I', write_addr)
                payload += struct.pack('>I', length)

                self.spw.events.PreprocDone.clear()
		self.spw.cmd(SpwCmdGrp.Preproc, PreprocCmds.Add, payload)
                self.spw.events.PreprocDone.wait(5)
                #time.sleep(15)

        def sub(self, read1_addr=0, read2_addr=0,\
                write_addr=0, length=0x40000):

                payload = struct.pack('>I', read1_addr)
		payload += struct.pack('>I', read2_addr)
                payload += struct.pack('>I', write_addr)
                payload += struct.pack('>I', length)

                self.spw.events.PreprocDone.clear()
		self.spw.cmd(SpwCmdGrp.Preproc, PreprocCmds.Sub, payload)
                self.spw.events.PreprocDone.wait(5)
                #time.sleep(15)
                
        def mult(self, read1_addr=0, read2_addr=0,\
                 write_addr=0, length=0x40000):

                payload = struct.pack('>I', read1_addr)
		payload += struct.pack('>I', read2_addr)
                payload += struct.pack('>I', write_addr)
                payload += struct.pack('>I', length)

                self.spw.events.PreprocDone.clear()
		self.spw.cmd(SpwCmdGrp.Preproc, PreprocCmds.Mult, payload)
                self.spw.events.PreprocDone.wait(5)
	        #time.sleep(15)

        def cmult(self, read1_addr=0, read2_addr=0,\
                  write_addr=0, length=0x40000):

                payload = struct.pack('>I', read1_addr)
		payload += struct.pack('>I', read2_addr)
                payload += struct.pack('>I', write_addr)
                payload += struct.pack('>I', length)

                self.spw.events.PreprocDone.clear()
		self.spw.cmd(SpwCmdGrp.Preproc, PreprocCmds.Cmult, payload)
                #self.spw.events.PreprocDone.wait(5)
	        time.sleep(15)

        def div(self, read1_addr=0, read2_addr=0,\
                write_addr=0, length=0x40000):

                payload = struct.pack('>I', read1_addr)
		payload += struct.pack('>I', read2_addr)
                payload += struct.pack('>I', write_addr)
                payload += struct.pack('>I', length)

                self.spw.events.PreprocDone.clear()
		self.spw.cmd(SpwCmdGrp.Preproc, PreprocCmds.Div, payload)
                #self.spw.events.PreprocDone.wait(5)
	        time.sleep(15)
                
	def fft(self, read_addr=0,\
                write_addr=None, fft_length=2048,\
                length=2048, vertical=False,\
                scaling=0):

                if(not fft_length in self.fft_sizes):
                        print('FFT length invalid')
                        return
                
                if(write_addr == None):
                        write_addr = size * length

                mode = (int(vertical) << 1) | 0x0c
                        
		payload = struct.pack('>I', read_addr)
		payload += struct.pack('>I', write_addr)
                payload += struct.pack('>I', length)
                payload += struct.pack('>H', fft_length)
                payload += struct.pack('>B', mode)

                self.spw.events.PreprocDone.clear()
		self.spw.cmd(SpwCmdGrp.Preproc, PreprocCmds.Fft, payload)
                self.spw.events.PreprocDone.wait(5)
                #time.sleep(15)
                
        def ifft(self, read_addr=0,\
                 write_addr=None, fft_length=2048,\
                 length=2048, vertical=False,\
                 scaling=0):

                if(not fft_length in self.fft_sizes):
                        print('FFT length invalid')
                        return
                
                if(write_addr == None):
                        write_addr = size * length

                mode = (int(vertical) << 1) | 0x0c
                        
		payload = struct.pack('>I', read_addr)
		payload += struct.pack('>I', write_addr)
                payload += struct.pack('>I', length)
                payload += struct.pack('>H', fft_length)
                payload += struct.pack('>B', mode)

                self.spw.events.PreprocDone.clear()
		self.spw.cmd(SpwCmdGrp.Preproc, PreprocCmds.Ifft, payload)
                self.spw.events.PreprocDone.wait(5)
                #time.sleep(15)
