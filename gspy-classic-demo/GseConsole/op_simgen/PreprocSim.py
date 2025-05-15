import struct
import os, sys

currentdir = os.path.dirname(os.path.abspath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
import sophilib

class PreprocSim():

    def __init__(self, filename=None, packet_size=256, preproc_path=[]):
        self.preproc_path = preproc_path
        self.preproc_baseid = 0x80
        self.preproc_baseport = 2
        
        self.sim = sophilib.Simulation(filename, packet_size)
        self.sim.clear()

        self.sim.wait(1800, 'us')

    def reg_write32(self, hw_id, reg, data, path=[]):
        val_lower = data & 0xffff
        val_upper = data >> 16
        
        self.sim.reg_write(hw_id, reg, val_lower, path)
        self.sim.reg_write(hw_id, reg + 1, val_upper, path)

    def store(self, data, addr):
        path = self.preproc_path + [1]
        
        # start address
        self.reg_write32(0xd6, 9, addr, path)

        # length
        n, last_part = divmod(len(data), 8)
        if last_part != 0:
            return
        
        self.reg_write32(0xd6, 11, n, path)

        # start transfer by positive edge
        self.sim.reg_write(0xd6, 13, 0, path)
        self.sim.reg_write(0xd6, 13, 1, path)

        # stream data
        self.sim.write(0xd6, data, path)

    def load(self, addr, length):
        path = self.preproc_path + [1]
        
        # start address
        self.reg_write32(0xd6, 4, addr, path)

        # length
        self.reg_write32(0xd6, 6, length, path)

        # start transfer by positive edge
        self.sim.reg_write(0xd6, 8, 0, path)
        self.sim.reg_write(0xd6, 8, 1, path)

    def div(self, addr_a, addr_b, addr_c, length):
        path = self.preproc_path + [self.preproc_baseport + 3]
        hwid = self.preproc_baseid + 3
        
        # read address 1
        self.reg_write32(hwid, 4, addr_a, path)

        # read address 2
        self.reg_write32(hwid, 6, addr_b, path)

        # write address
        self.reg_write32(hwid, 8, addr_c, path)

        # length
        self.reg_write32(hwid, 10, length, path)

        # start execution by positive edge
        self.sim.reg_write(hwid, 16, 0, path)
        self.sim.reg_write(hwid, 16, 1, path)
