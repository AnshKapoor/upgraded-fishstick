from ..spacewire import *
from .commands import *
from pathlib import Path
import logging
import os
import struct


logger = logging.getLogger(__name__)


class RamFs:
    def __init__(self, spw: SpaceWire, check_for_module=False):
        if not isinstance(spw, SpaceWire):
            spw = spw.hardware  # type: SpaceWire

        if spw.has_extension(self):
            if check_for_module:
                raise ValueError("SpaceWire Object already has %s extension!" % self.__class__.__name__)
            return
        self.spw = spw
        spw.add_extension(self, extend_methods=True)
        spw.add_decode_listener(self._spw_listener_download)

        self.downfile_default = Path('download.raw')
        self.downfile = self.downfile_default
        self.downfile_old = self.downfile_default
        self.downdata = bytes()
        self.prev_sequence = 0
        self.download_complete = threading.Event()

    def _spw_listener_download(self, message):
        receive = self.spw.spw_raw.receive
        
        # File download?
        if message[0] == 0x33:
            while len(message) < 8:
                message += receive()

            sequence = struct.unpack('>H', message[2:4])[0]
            seq_total = struct.unpack('>H', message[4:6])[0]
            length = struct.unpack('>H', message[6:8])[0]

            while len(message) < 4096:
                message += receive()

            if self.downfile is None:
                if sequence == 0:
                    self.downdata = message[8:length + 8]
                else:
                    self.downdata += message[8:length + 8]
                    if sequence != self.prev_sequence + 1:
                        self.spw.message_handler.error('Missing packet!')
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
                self.downfile_old = self.downfile
                self.downfile = self.downfile_default
                self.download_complete.set()
                self.spw.message_handler.info('File download done.')
            self.prev_sequence = sequence
            return message

    def file_list(self, prm=None):
        self.spw.cmd(SpwCmdGrp.RamFs, RamFsCmds.PrintFileList)

        if prm is None:
            pass

    def file_delete(self, filename):
        self.spw.cmd(SpwCmdGrp.RamFs, RamFsCmds.Delete, filename + '\x00')

    def file_upload(self, filename_dpu, filepath_local_or_data, is_data_not_file=False, wait=True, listener=None):
        if wait:
            return self._file_upload(filename_dpu, filepath_local_or_data, is_data_not_file)
        threading.Thread(
            target=self._file_upload, args=(filename_dpu, filepath_local_or_data, is_data_not_file, listener)).start()

    def _file_upload(self, filename_dpu, filepath_local_or_data, is_data_not_file=False, listener=None):
        if is_data_not_file:
            return self.file_upload_data(filename_dpu, filepath_local_or_data)
        hdr = 0xcc

        size = os.path.getsize(filepath_local_or_data)
        sdata = struct.pack('>I', size)
        sdata += filename_dpu.encode('utf-8')
        sdata += b'\x00'
        self.spw.cmd(SpwCmdGrp.RamFs,
                     RamFsCmds.DeleteOpen, sdata)

        file_ = open(filepath_local_or_data, 'rb')
        offset = 0

        n, last_part = divmod(size, self.spw.spw_packet_size)

        for i in range(0, n, 1):
            memload = struct.pack('>B', hdr)
            memload += b'\x00'
            memload += struct.pack('>H', self.spw.spw_packet_size)
            memload += struct.pack('>I', offset)
            memload += file_.read(self.spw.spw_packet_size)
            self.spw.send(memload)
            offset += self.spw.spw_packet_size
            time.sleep(0.01)

        if last_part > 0:
            memload = struct.pack('>B', hdr)
            memload += b'\x00'
            memload += struct.pack('>H', last_part)
            memload += struct.pack('>I', offset)
            memload += file_.read(last_part)
            self.spw.send(memload)

        file_.close()

        self.spw.cmd(SpwCmdGrp.RamFs, RamFsCmds.Close)

        if callable(listener):
            listener()

    def file_upload_data(self, filename_dpu, data):
        hdr = 0xcc

        # convert to string array
        rawdata = memoryview(data).tobytes()

        size = len(rawdata)
        sdata = struct.pack('>I', size)
        sdata += filename_dpu.encode('utf-8')
        sdata += b'\x00'
        self.spw.cmd(SpwCmdGrp.RamFs, RamFsCmds.DeleteOpen, sdata)

        n, last_part = divmod(size, self.spw.spw_packet_size)
        offset = 0

        for i in range(0, n, 1):
            memload = struct.pack('>B', hdr)
            memload += b'\x00'
            memload += struct.pack('>H', self.spw.spw_packet_size)
            memload += struct.pack('>I', offset)
            memload += rawdata[offset:offset + self.spw.spw_packet_size]
            self.spw.send(memload)
            offset += self.spw.spw_packet_size
            # time.sleep(0.01)

        if last_part > 0:
            memload = struct.pack('>B', hdr)
            memload += b'\x00'
            memload += struct.pack('>H', last_part)
            memload += struct.pack('>I', offset)
            memload += rawdata[offset:]
            self.spw.send(memload)

        self.spw.cmd(SpwCmdGrp.RamFs, RamFsCmds.Close)

    # noinspection PyUnreachableCode
    def _call_download_listener(self, listener: callable):
        self.download_complete.wait()
        try:
            try:
                if self.downfile is None:
                    listener(downdata=self.downdata)
                else:
                    listener(downfile=self.downfile_old)
                return
            except TypeError:
                try:
                    listener(self.downdata if self.downfile is None else self.downfile)
                    return
                except TypeError:
                    listener()
        except Exception:
            logger.exception("Failed to call download listener.")

    def file_download(self, filename_dpu, filepath_local=None, wait=False, listener=None):
        self.downfile = filepath_local

        self.download_complete.clear()

        self.spw.cmd(SpwCmdGrp.RamFs, RamFsCmds.DownloadToGround, ' ' + filename_dpu + '\x00')
        if wait:
            self.download_complete.wait()
            return self.downdata
        elif listener is not None:
            threading.Thread(target=self._call_download_listener, args=(listener,)).start()
            return True
