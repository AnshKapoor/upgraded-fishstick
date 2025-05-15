import socket
import os
import time
import sys
import struct

from SpaceWire import *
from Telecommand import *

from sophilib import Nand

class Cmd_Nand():

	def __init__(self, spw):
                self.spw = spw
                self.nand = Nand(spw)

        # TODO: shift to sophilib
        def do_nand_power(self, prm): 
		part   = 1
		on_off = 0

		p_list = prm.split()
		
		if(len(p_list) < 2): 
			print('Invalid parameter')
			return False
		
		if(p_list[0] == 'part1'): part = 1
		if(p_list[0] == 'part2'): part = 2
		
		if(p_list[1] == 'on'):  on_off = 1
		if(p_list[1] == 'off'): on_off = 0
		
		#print(part)
		#print(on_off)

		test = struct.pack('>B', part)
		test += struct.pack('>B', on_off)

		self.spw.cmd(12, 17, test)

        def do_nand_read(self, prm): 
		p_list = prm.split()
                
		if(len(p_list) < 1): 
			print('Invalid parameter')
			return False
                elif(len(p_list) < 3):
                        block_len = 1
                        partition = 1
                elif(len(p_list) < 2):
                        block_len = p_list[1]
                        partition = 1
                else:
                        block_len = p_list[1]
                        partition = p_list[2]

                block_addr = p_list[0]

		payload = struct.pack('<H', int(block_addr))
		payload += struct.pack('>B', int(block_len))
                payload += struct.pack('>B', int(partition))

                #self.spw.events.SoCWRxDone.clear()
                
		self.spw.cmd(SpwCmdGrp.Nand, NandCmds.ReadBlocksSoCWire, payload)

                #self.spw.events.SoCWRxDone.wait()
                #print('Read from NAND done...')

        def do_nand_read_to_rfpga(self, prm): 
                self.nand.set_interrupts(True)
                self.nand.read_to_rfpga(0, 1, 1)    

        def do_nand_devices(self, prm):
                self.spw.cmd(SpwCmdGrp.Nand, NandCmds.ReadUId)

        def do_nand_interrupts(self, prm):
                p_list = prm.split()
                
                if(len(p_list) < 1): 
			print('Invalid parameter')
			return False
                else:
                        if(p_list[0] == 'True'):
                                enable = True
                        elif(p_list[0] == 'False'):
                                enable = False
                        else:
                                print('Invalid parameter')
			        return False

                self.nand.set_interrupts(enable)

        def do_nand_store_frames16(self, prm):
                self.nand.set_interrupts(True)
                self.nand.store_frames16()

        
