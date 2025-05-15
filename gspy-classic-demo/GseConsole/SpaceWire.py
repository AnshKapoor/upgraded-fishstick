# import socket
# import cmd
# import os
import time
# import sys
# import struct
# import thread
# import threading

from Telecommand import *
# from CCSDS import *
from Boot import *
from Events import *


class BColors:
    def __init__(self):
        pass

    info = '\033[0m'
    warning = '\033[38;5;3m'
    success = '\033[38;5;2m'
    error = '\033[38;5;1m'
    endc = '\033[0m'


class SpaceWire(object):
    def __init__(self, spw_raw,
                 spw_dest_addr=4,
                 spw_packet_size=4096,
                 ipython=False):

        self.spw_raw = spw_raw
        self.spw_raw.open()
        self.spw_packet_size = spw_packet_size
        self.spw_dest_addr = spw_dest_addr
        self.ipython = ipython

        self.downfile_default = 'download.raw'
        self.downfile = self.downfile_default
        self.downdata = ''
        self.prev_sequence = 0
        self.download_complete = threading.Event()
        self.boot = Boot(self)
        thread.start_new_thread(self.receive_thread, ())

        self.events = SpwEvents()

    def __del__(self):
        self.spw_raw.close()

    def send(self, sdata):
        self.spw_raw.send(sdata, self.spw_dest_addr)

    def cmd(self, code, subcode, data=''):
        hdr = 0xbb
        sdata = struct.pack('>B', hdr)
        sdata += '\x00'
        sdata += struct.pack('>B', code)
        sdata += struct.pack('>B', subcode)
        sdata += '\x00'
        sdata += '\x00'
        sdata += data

        self.send(sdata)

    def upload_file(self, filename_gse, filename_dpu):
        hdr = 0xcc

        size = os.path.getsize(filename_gse)
        sdata = struct.pack('>I', size)
        sdata += filename_dpu.encode('utf-8')
        sdata += '\x00'
        self.cmd(SpwCmdGrp.RamFs,
                 RamFsCmds.DeleteOpen, sdata)

        file_ = open(filename_gse, 'rb')
        offset = 0

        n, last_part = divmod(size, self.spw_packet_size)

        for i in range(0, n, 1):
            memload = struct.pack('>B', hdr)
            memload += '\x00'
            memload += struct.pack('>H', self.spw_packet_size)
            memload += struct.pack('>I', offset)
            memload += file_.read(self.spw_packet_size)
            self.send(memload)
            offset += self.spw_packet_size
            time.sleep(0.01)

        if last_part > 0:
            memload = struct.pack('>B', hdr)
            memload += '\x00'
            memload += struct.pack('>H', last_part)
            memload += struct.pack('>I', offset)
            memload += file_.read(last_part)
            self.send(memload)

        file_.close()

        self.cmd(SpwCmdGrp.RamFs,
                 RamFsCmds.Close)

    def upload_data(self, filename_dpu, data):
        hdr = 0xcc

        # convert to string array
        rawdata = memoryview(data).tobytes()

        size = len(rawdata)
        sdata = struct.pack('>I', size)
        sdata += filename_dpu.encode('utf-8')
        sdata += '\x00'
        self.cmd(SpwCmdGrp.RamFs,
                 RamFsCmds.DeleteOpen, sdata)

        n, last_part = divmod(size, self.spw_packet_size)
        offset = 0

        for i in range(0, n, 1):
            memload = struct.pack('>B', hdr)
            memload += '\x00'
            memload += struct.pack('>H', self.spw_packet_size)
            memload += struct.pack('>I', offset)
            memload += rawdata[offset:offset + self.spw_packet_size]
            self.send(memload)
            offset += self.spw_packet_size
            # time.sleep(0.01)

        if last_part > 0:
            memload = struct.pack('>B', hdr)
            memload += '\x00'
            memload += struct.pack('>H', last_part)
            memload += struct.pack('>I', offset)
            memload += rawdata[offset:]
            self.send(memload)

        self.cmd(SpwCmdGrp.RamFs,
                 RamFsCmds.Close)

    def download_file(self, filename_dpu, filename_gse=''):
        self.downfile = filename_gse

        self.download_complete.clear()

        self.cmd(SpwCmdGrp.RamFs, RamFsCmds.DownloadToGround, ' ' + filename_dpu + '\x00')
        self.download_complete.wait()
        return self.downdata

    def print_handler(self, s, fmt='i'):
        outmsg = ''

        if fmt == 'i':
            outmsg = BColors.info  # + '[i] '
        elif fmt == 'w':
            outmsg = BColors.warning  # + '[w] '
        elif fmt == 's':
            outmsg = BColors.success  # + '[s] '
        elif fmt == 'e':
            outmsg = BColors.error  # + '[e] '

        outmsg += s + BColors.endc
        if not self.ipython:
            sys.stdout.write('\r')
        sys.stdout.write(outmsg)

        if not self.ipython:
            sys.stdout.write(':> ')
        sys.stdout.flush()

    def receive_thread(self):
        message = ''

        receive = self.spw_raw.receive

        while True:
            self.spw_raw.lock.acquire()
            message += receive()

            # print(str(hex(ord(message[0]))))
            # Boot event?
            if message[0] == '\x49':
                message = self.boot.decode(message)

            # RMAP reply?
            elif message[0] == '\x46':
                # print('RMAP reply')
                message = ''

            elif message[0] == '\x35':
                message = self.tm_decode(message[1:])

            else:
                print('Undefined sender!')
                print(str(hex(ord(message[0]))))
                print(len(message))
                message = ''
                self.download_complete.set()

            self.spw_raw.lock.release()

    def tm_decode(self, message):
        receive = self.spw_raw.receive

        # Housekeeping?
        if message[0] == '\xaa':
            while len(message) < 148:
                message += receive()

                # print 'Received HK packet #' + str(ord(message[1]))
                # print str(ord(message[0]))
                # print str(ord(message[1]))
                # print str(ord(message[2]))
                # print str(ord(message[3]))
            message = message[148:]

        # Notification?
        elif message[0] == '\x66':
            while len(message) < 8:
                message += receive()

            # noinspection PyUnusedLocal
            sequence = struct.unpack('>H', message[2:4])[0]
            # noinspection PyUnusedLocal
            seq_total = struct.unpack('>H', message[4:6])[0]
            length = struct.unpack('>H', message[6:8])[0]

            while len(message) < length + 8:
                message += receive()

            self.print_handler(message[15:length + 8], message[8])
            message = message[length + 8:]

        # Event?
        elif message[0] == '\x77':
            while len(message) < 8:
                message += receive()

            # noinspection PyUnusedLocal
            sequence = struct.unpack('>H', message[2:4])[0]
            # noinspection PyUnusedLocal
            seq_total = struct.unpack('>H', message[4:6])[0]
            length = struct.unpack('>H', message[6:8])[0]

            while len(message) < (length + 8):
                message += receive()

            self.events.set_event(ord(message[8]))
            # self.print_handler('Event triggered!', 's')
            # self.print_handler(message[15:length+8], message[8])
            message = message[length + 8:]

        # File download?
        elif message[0] == '\x33':
            while len(message) < 8:
                message += receive()

            sequence = struct.unpack('>H', message[2:4])[0]
            seq_total = struct.unpack('>H', message[4:6])[0]
            length = struct.unpack('>H', message[6:8])[0]

            while len(message) < 4096:
                message += receive()

            if self.downfile == '':
                if sequence == 0:
                    self.downdata = message[8:length + 8]
                else:
                    self.downdata += message[8:length + 8]
                    if sequence != self.prev_sequence + 1:
                        print('Missing packet!')
            else:
                if sequence == 0:
                    file_ = open(self.downfile, 'wb')
                else:
                    file_ = open(self.downfile, 'ab')
                file_.write(message[8:length + 8])
                file_.close()
            # print 'sequence: ' + str(sequence) + ' of: ' + str(seq_total)
            # print 'length: ' + str(length)
            # print 'array length:' + str(len(message))
            message = message[4096:]
            # print(len(message))

            if sequence == (seq_total - 1):
                self.downfile = self.downfile_default
                self.download_complete.set()
                print('done...')
            self.prev_sequence = sequence

        else:
            # for i in range(len(message)-4):
            #        print(str(ord(message[i+4])))
            # print(message)
            message = ''
            print('Undefined packet!')
            self.download_complete.set()

        return message
