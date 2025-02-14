import socket
import os
import time
import sys
import struct

from SpaceWire import *
from sophilib import NandFs

class Cmd_NandFs():

	def __init__(self, spw):
                self.spw = spw
                self.nandfs = NandFs(spw)

        def do_nandfs_mount(self, prm): 
		part   = 1
		on_off = 0

		p_list = prm.split()
		
		if(len(p_list) < 2): 
			print('Invalid parameter')
			return False
		
	

        def do_nandfs_umount(self, prm): 
		p_list = prm.split()
                
		if(len(p_list) < 1): 
			print('Invalid parameter')
			return False
              


        
