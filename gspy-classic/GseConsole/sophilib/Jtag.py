# import struct

# from SpaceWire import *
# from Telecommand import *
from RamFs import *


class Jtag(object):
    def __init__(self, spw):
        self.spw = spw
        self.ramfs = RamFs(spw)

    def rfpga_power(self, power):
        if power:
            ctrl_reg = struct.pack('>L', 0x80)  # register value power on
        else:
            ctrl_reg = struct.pack('>L', 0x00)  # register value power off

        ctrl_reg += struct.pack('>L', 0x80)  # register mask

        self.spw.cmd(SpwCmdGrp.System, SystemCmds.SetControlRegister, ctrl_reg)

    def rfpga_reset(self, rfpga):
        if rfpga == 1:
            ctrl_reg = struct.pack('>L', 0x100)  # rfpga1 reset
        elif rfpga == 2:
            ctrl_reg = struct.pack('>L', 0x200)  # rfpga2 reset
        else:
            ctrl_reg = struct.pack('>L', 0x000)

        ctrl_reg += struct.pack('>L', 0x300)  # register mask

        self.spw.cmd(SpwCmdGrp.System, SystemCmds.SetControlRegister, ctrl_reg)

        ctrl_reg = struct.pack('>L', 0x000)  # release reset
        ctrl_reg += struct.pack('>L', 0x300)  # register mask

        self.spw.cmd(SpwCmdGrp.System, SystemCmds.SetControlRegister, ctrl_reg)

    def config(self, filename, rfpga, scrubbing=True):
        parameters = struct.pack('>B', rfpga)
        parameters += 'rfpga.bit' + '\0'

        self.spw.events.Rfpga1Configured.clear()
        self.spw.events.Rfpga2Configured.clear()

        self.rfpga_power(True)
        # ctrl_reg = struct.pack('>L', 0x80)  # register value
        # ctrl_reg += struct.pack('>L', 0x80) # register mask

        self.spw.upload_file(filename, 'rfpga.bit')

        if scrubbing:
            self.spw.cmd(SpwCmdGrp.Jtag, JtagCmds.Config, parameters)
        else:
            self.spw.cmd(SpwCmdGrp.Jtag, JtagCmds.ConfigNoScrub, parameters)

        if rfpga == 1:
            self.spw.events.Rfpga1Configured.wait(20)
        elif rfpga == 2:
            self.spw.events.Rfpga2Configured.wait(20)

        self.ramfs.delete('rfpga.bit')

        print('Configuration done...')
