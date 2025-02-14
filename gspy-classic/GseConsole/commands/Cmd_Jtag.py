import socket
import os
import time
import sys
import struct

from SpaceWire import *
from sophilib import Jtag

class Cmd_Jtag(Jtag):

	def __init__(self, spw):
                Jtag.__init__(self, spw)

        def do_rfpga_power(self, prm):
                p_list = prm.split()
                
                if(len(p_list) < 1): 
			print('Invalid parameter')
			return False

                if(p_list[0] == 'on'):
                        self.rfpga_power(True)
                elif(p_list[0] == 'off'):
                        self.rfpga_power(False)

        def do_config(self, prm):
		p_list = prm.split()
		
		if(len(p_list) < 2): 
			print('Invalid parameter')
			return False

                self.config(p_list[0], int(p_list[1]))

        def do_config_noscrub(self, prm):
		p_list = prm.split()
		
		if(len(p_list) < 2): 
			print('Invalid parameter')
			return False

                self.config(p_list[0], int(p_list[1]), False)

        def do_rfpga_reset(self, prm):
                p_list = prm.split()
                
                if(len(p_list) < 1): 
			print('Invalid parameter')
			return False

                self.rfpga_reset(int(p_list[0]))
                
#        def do_readback(self, prm):
#		p_list = prm.split()
#		
#		if(len(p_list) < 1): 
#			print('Invalid parameter')
#			return False
#			
#		parameters = struct.pack('>B', 2)
#		parameters += struct.pack('>L', int(p_list[0],0))
#		self.spw.cmd(4, 5, parameters)
