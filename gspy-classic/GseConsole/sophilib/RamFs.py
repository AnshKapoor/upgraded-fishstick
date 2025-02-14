from SpaceWire import *
from Telecommand import *


class RamFs():
    def __init__(self, spw):
        self.spw = spw

    def delete(self, filename):
        self.spw.cmd(SpwCmdGrp.RamFs, RamFsCmds.Delete, filename + '\x00')
