import struct

from SpaceWire import *
from sophilib import NorFs

class Cmd_NorFs():

	def __init__(self, spw):
                self.spw = spw
                self.norfs = NorFs(spw)
                
              


        
