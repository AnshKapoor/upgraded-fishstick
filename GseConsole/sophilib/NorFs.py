import struct

from SpaceWire import *
from Telecommand import *

class NorFs():

	def __init__(self, spw):
                self.spw = spw

        def moveNorToSdram(self, fileno_nor, filename_sdram):
                """Move file from NOR-Flash to SDRAM FS"""

                payload = struct.pack('>B', fileno_nor)
                payload += filename_sdram
                payload += '\x00' # Terminate string
                self.spw.cmd(SpwCmdGrp.NorFs, NorFsCmds.MoveNorToMm, payload)

        def moveSdramToNor(self, filename_sdram, fileno_nor):
                """Move file from SDRAM to NOR-Flash FS"""
              
                payload = struct.pack('>B', fileno_nor)
                payload += filename_sdram
                payload += '\x00' # Terminate string
                self.spw.cmd(SpwCmdGrp.NorFs, NorFsCmds.MoveMmToNor, payload)

        def delete(self, fileno_nor):
                """Delete file in NOR-Flash FS"""
                
                payload = struct.pack('>B', fileno_nor)
                self.spw.cmd(SpwCmdGrp.NorFs, NorFsCmds.Delete, payload)

        def fileInfo(self, fileno_nor):
                """Show file information on file in NOR-Flash FS"""
                
                payload = struct.pack('>B', fileno_nor)
                self.spw.cmd(SpwCmdGrp.NorFs, NorFsCmds.PrintFileInfo, payload)
        
        def printFat(self):
                """Print NOR-Flash file allocation table"""
                
                self.spw.cmd(SpwCmdGrp.NorFs, NorFsCmds.PrintFAT)

        def format(self):
                """Format NOR-Flash file system"""
                
                self.spw.cmd(SpwCmdGrp.NorFs, NorFsCmds.Format)

      
