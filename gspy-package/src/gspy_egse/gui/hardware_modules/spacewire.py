# import socket
# import cmd
# import os
import time
# import sys
import struct
# import thread
import threading  # from Telecommand import *
# from CCSDS import *
# from Boot import *
# from Events import *
from contextlib import suppress
from typing import *

from gspy_egse.gui.utils.misc import WrappedMessageHandler, Extendable, call_async
from gspy_egse.gui.hardware_modules.spacewire_events import SpwEvents

class ISpaceWireBridge:
    def open(self): raise NotImplementedError

    @property
    def is_open(self) -> bool: raise NotImplementedError

    def send(self, send_data: list[int], dest_addr: int = None): raise NotImplementedError

    def receive(self) -> bytes: raise NotImplementedError


class SpaceWire(Extendable):
    def __init__(self, spw_raw: ISpaceWireBridge, *args, spw_dest_addr=4, spw_packet_size=4096, clear_header=True,
                 message_handler=None, **kwargs):
        """
        SpaceWire object, used to communicate with a device connected to a SpareWire Bridge

        :param spw_raw: The spacewire bridge object used for connection
        :param spw_dest_addr:
        :param spw_packet_size:
        :param clear_header:
        :param message_handler:
        """
        super().__init__(*args, **kwargs)
        self.spw_raw = spw_raw
        self.clear_header = clear_header
        self.spw_raw.message_handler = WrappedMessageHandler(message_handler, "SpaceWireBridge")
        self.spw_raw.error_printer = self.spw_raw.message_handler.error
        self.spw_raw.open()
        self.spw_packet_size = spw_packet_size
        self.spw_dest_addr = spw_dest_addr
        self.message_handler = WrappedMessageHandler(message_handler, "SpaceWire")
        self.ipython = False
        self.cmd_substitutions = {}

        # self.boot = Boot(self)
        self.thread_lock = threading.Lock()  # type: threading.Lock
        self.do_receive = True
        if not self.spw_raw.dummy:
            call_async(self.receive_thread)

        self.events = SpwEvents()
        self.listeners_raw = []
        self.listeners_decode = []

    def set_spw_raw_synchronous(self, spw_raw):
        self.do_receive = False
        with self.thread_lock:
            pass

        message_handler = self.spw_raw.message_handler
        self.spw_raw.close()
        self.spw_raw = spw_raw
        self.spw_raw.message_handler = message_handler
        self.spw_raw.error_printer = self.spw_raw.message_handler.error
        self.spw_raw.open()

        self.do_receive = True
        call_async(self.receive_thread)

    def set_spw_raw(self, spw_raw):
        call_async(self.set_spw_raw_synchronous, spw_raw)

    def set_spw_dest_addr(self, spw_dest_addr):
        self.spw_dest_addr = spw_dest_addr

    def set_spw_packet_size(self, spw_packet_size):
        self.spw_packet_size = spw_packet_size

    def add_raw_listener(self, listener):
        self.listeners_raw.append(listener)

    def add_decode_listener(self, listener):
        self.listeners_decode.append(listener)

    def close(self):
        self.do_receive = False
        with self.thread_lock:
            pass
        self.spw_raw.close()

    def __del__(self):
        self.close()

    def send(self, sdata):

        print(f"SpaceWire send bytes: {sdata}")

        if isinstance(sdata, bytes):
            sdata = list(sdata)

        print(f"SpaceWire send list: {sdata}")

        if self.spw_dest_addr is not None and isinstance(self.spw_dest_addr, list) is False:
            self.spw_dest_addr = [self.spw_dest_addr]

        self.spw_raw.send(sdata, self.spw_dest_addr)

    def _cmd_substitute(self, code, sub_code=None) -> (int, int):
        if sub_code is None:
            return self.cmd_substitutions.get(code, (code, None))

        return self.cmd_substitutions.get((code << 8) | sub_code, (code, sub_code))

    def cmd_substitute(self, code, sub_code=None, substitute=None, sub_substitute=None):
        substitute = code if substitute is None else substitute

        if sub_code is None:
            self.cmd_substitutions[code] = (substitute, sub_substitute)
        else:
            self.cmd_substitutions[(code << 8) | sub_code] = (substitute, sub_substitute)

    def cmd(self, code, sub_code=None, data: Union[str, bytes] = ''):
        code, sub_code = self._cmd_substitute(code, sub_code)
        hdr = 0xbb
        sdata = struct.pack('>B', hdr)
        sdata += b'\x00'
        if sub_code is None:
            sdata += struct.pack('>H', code)
        else:
            sdata += struct.pack('>B', code)
            sdata += struct.pack('>B', sub_code)
        sdata += b'\x00'
        sdata += b'\x00'
        sdata += data.encode('utf-8') if isinstance(data, str) else data

        self.send(sdata)

    def to_print_handler(self, s, fmt='i'):
        f = self.message_handler.info  # default: Info

        if fmt == 'i':
            f = self.message_handler.info  # outmsg = BColors.info  # + '[i] '
        elif fmt == 'w':
            f = self.message_handler.warning  # outmsg = BColors.warning  # + '[w] '
        elif fmt == 's':
            f = self.message_handler.success  # outmsg = BColors.success  # + '[s] '
        elif fmt == 'e':
            f = self.message_handler.error  # outmsg = BColors.error  # + '[e] '

        f(s)

    def try_raw_listeners(self, message):
        for listener in self.listeners_raw:
            m = listener(message)
            if m is not None:
                return m
        self.message_handler.error('Undefined sender!')
        self.message_handler.error(hex(message[0]))
        self.message_handler.error(len(message))
        return bytes()

    def receive_thread(self):
        """
        with self.thread_lock:
        This mechanism ensures that only one part of the code (one thread)
        can access the critical section protected by the lock at any given time.
        Other threads trying to access the same section will be blocked until
        the lock is released by the thread that currently holds it.
        """

        if self.thread_lock.locked():
            print(f"receive_thread locked status on\n")
            return
        with self.thread_lock:
            message = bytes()
            receive = self.spw_raw.receive

            # sub thread receive_thread is always running, it is in waiting to receive something
            # when function is inside the while loop, thread_lock is always occupied
            # until do_receive is changed to false
            while self.do_receive:
                if not self.spw_raw.is_open:
                    time.sleep(.01)
                    continue
                with self.spw_raw.lock:
                    r = receive()
                    if r is None:
                        continue
                    message += r

                    message = self.message_received(message)
                    message = bytes() if message is None else message

    def message_received(self, message):
        if self.clear_header:
            m = self.message_decode(message)
            if m is None:
                message = self.try_raw_listeners(message)
            else:
                message = m

        # RMAP reply?
        elif message[0] == 0x46:
            # print('RMAP reply')
            message = bytes()

        elif message[0] == 0x35:
            message = self.message_decode(message[1:])

        else:
            message = self.try_raw_listeners(message)
            # self.download_complete.set()
        return message

    def message_decode(self, message):
        receive = self.spw_raw.receive

        # Notification?
        if message[0] == 0x66:
            print(f"message[0] == 0x66 Notification")
            while len(message) < 8:
                message += receive()

            # noinspection PyUnusedLocal
            sequence = struct.unpack('>H', message[2:4])[0]
            # noinspection PyUnusedLocal
            seq_total = struct.unpack('>H', message[4:6])[0]
            length = struct.unpack('>H', message[6:8])[0]

            while len(message) < length + 8:
                message += receive()

            self.to_print_handler(message[15:length + 8], message[8])
            message = message[length + 8:]

        # Event?
        elif message[0] == 0x77:
            print(f"message[0] == 0x77 Event")
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
        else:
            for listener in self.listeners_decode:
                m = listener(message)
                if m is not None:
                    return m
            # for i in range(len(message)-4):
            #        print(str(ord(message[i+4])))
            # print(message)
            if self.clear_header:
                return
            message = bytes()
            self.message_handler.error('Undefined packet!')

        return message

    def call_receive_thread_async(self):
        call_async(self.receive_thread)
