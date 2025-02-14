import socket
import os
import time
import sys
import struct

from SpaceWire import *
from Telecommand import SpwCmdGrp
from Telecommand import SystemCmds
import Rmap


class Cmd_Boot():
    def __init__(self, spw):
        self.spw = spw

    def do_boot(self, prm):
        p_list = prm.split()

        if (len(p_list) < 1):
            self.spw.boot.soft_filename = ''
            print('DPU will boot normally')
        else:
            self.spw.boot.soft_filename = p_list[0]
            print('DPU will boot into: ' + p_list[0])

    def help_boot(self):
        print('boot [filename]')
        print('')
        print('Set binary file to boot into during power on of DPU')

    def do_reboot(self, prm):
        rmap = Rmap.Rmap(self.spw.spw_raw, 0x45, 0x49)

        data = 0x00008000  # GR712 reset
        rmap.rmap_write(0x20000004, struct.pack('>L', data))

        # payload = struct.pack('>L', 0x8000)  # control register value
        # payload += struct.pack('>L', 0x8000) # control register mask
        # self.spw.cmd(SpwCmdGrp.System, SystemCmds.SetControlRegister, payload)

    def help_reboot(self):
        print('reboot')
        print('')
        print('Reboot DPU via RMAP')

    def do_rmap_read(self, prm):
        p_list = prm.split()

        if (len(p_list) < 1):
            print('Invalid parameters')
        elif (len(p_list) < 2):
            length = 4
            address = int(p_list[0], 0)
        else:
            length = int(p_list[1], 0)
            address = int(p_list[0], 0)

        rmap = Rmap.Rmap(self.spw.spw_raw, 0x45, 0x49)

        data = rmap.rmap_read(address, length)

        n, last_part = divmod(length, 4)

        for i in range(n):
            print('0x' + data[4 * i:4 * i + 4].encode('hex'))

        if last_part > 0:
            print('0x' + data[4 * n:4 * n + last_part].encode('hex'))

    def do_rmap_write(self, prm):
        p_list = prm.split()

        if (len(p_list) < 2):
            print('Invalid parameters')
        else:
            value = int(p_list[1], 0)
            address = int(p_list[0], 0)

        rmap = Rmap.Rmap(self.spw.spw_raw, 0x45, 0x49)
        rmap.rmap_write(address, struct.pack('>L', value))
