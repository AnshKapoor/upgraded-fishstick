import struct
from Telecommand import *

class PathSetup():
    Empty,\
    Iss,\
    Acquisition,\
    Preproc = range(4)

class SoCWire():

	def __init__(self, spw):
                self.spw = spw

        def pathtable_setup(self, path_setup):
                parameters = struct.pack('>B', path_setup)
		self.spw.cmd(SpwCmdGrp.SoCWire, SoCWireCmds.SetupPathTable, parameters)

