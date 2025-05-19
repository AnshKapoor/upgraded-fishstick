import os
import time
import sys
import struct

from SpaceWire import *
from sophilib import SoCWire, PathSetup

class Cmd_SoCWire():

	def __init__(self, spw):
                self.spw = spw
                self.socwire = SoCWire(spw)

        def do_socreg_write(self, prm): 
		p_list = prm.split()
		
		if(len(p_list) < 3): 
			print('Invalid parameter')
			return False
			
		parameters = struct.pack('>B', int(p_list[1],0))
		parameters += struct.pack('>B', int(p_list[0],0))
		parameters += struct.pack('>B', 1)
		parameters += struct.pack('>H', int(p_list[2],0))
			
		self.spw.cmd(2, 5, parameters)
			
	def do_socreg_read(self, prm): 
		p_list = prm.split()
		
		if(len(p_list) < 2): 
			print('Invalid parameter')
			return False
			
		parameters = struct.pack('>B', int(p_list[1],0))
		parameters += struct.pack('>B', int(p_list[0],0))
		parameters += struct.pack('>B', 1)
			
		self.spw.cmd(2, 4, parameters)

        def do_socpathtable_setup(self, prm):
                p_list = prm.split()
		
		if(len(p_list) < 1): 
			print('Invalid parameter')
			return False

                if p_list[0] == 'none':
                        self.socwire.pathtable_setup(PathSetup.Empty)
                elif p_list[0] == 'iss':
                        self.socwire.pathtable_setup(PathSetup.Iss)
                elif p_list[0] == 'acquisition':
                        self.socwire.pathtable_setup(PathSetup.Acquisition)
                elif p_list[0] == 'preproc':
                        self.socwire.pathtable_setup(PathSetup.Preproc)
