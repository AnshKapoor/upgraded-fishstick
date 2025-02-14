import struct
import os
from string import Template

class Simulation():

    def __init__(self, filename=None, packet_size=256):
        self.filename = filename
        self.packet_size = packet_size

        self.stmp_wait = 'wait %d %s'
        self.stmp_data = 'data %04x'
        self.stmp_ceop = 'ceop'

    def append_string(self, str):
        '''Append string to output file'''
        if self.filename is None:
            print(str)
        else:
            file = open(self.filename, 'a')
            file.write(str + '\n')
            file.close()

    def append_header(self, hw_id, cmd, path=[]):
        '''Append SoCWire packet header'''
        for i in path:
            self.append_string(self.stmp_data % (0xffff & i))

        ident = (hw_id << 4) | 0x03
        self.append_string(self.stmp_data % (0xffff & ident))
        self.append_string(self.stmp_data % (0x0c02))
        self.append_string(self.stmp_data % (0xffff & cmd))

    def clear(self):
        '''Clear existing simulation file'''
        if self.filename is None:
            return
        
        if os.path.isfile(self.filename):
            os.remove(self.filename)

    def wait(self, time, unit='us'):
        '''Append wait command'''
        self.append_string(self.stmp_wait % (time, unit))

    def reg_write(self, hw_id, reg, data, path=[]):
        '''Write SoCWire register'''
        self.append_header(hw_id, 0x20, path)
        self.append_string(self.stmp_data % (0xffff & reg))
        self.append_string(self.stmp_data % (0xffff & data))
        self.append_string(self.stmp_ceop)

        # wait 10 us
        self.wait(10, 'us')

    def write(self, hw_id, data, path=[]):
        '''Stream SoCWire data'''
        self.append_header(hw_id, 0x50, path)

        if len(data) % 2 != 0:
            return

        length = len(data)/2

        n, last_part = divmod(length, self.packet_size)

        print(n)
        print(last_part)
        
        for i in range(n):
            offset = 2 * i * self.packet_size
            for j in range(256):
                word = struct.unpack('>H', data[offset+2*j:offset+2*j+2])[0]
                self.append_string(self.stmp_data % (word))

        offset = 2 * n * self.packet_size
        for j in range(last_part):
            word = struct.unpack('>H', data[offset+2*j:offset+2*j+2])[0]
            self.append_string(self.stmp_data % (word))
            
        self.append_string(self.stmp_ceop)

    
