# import socket
# import cmd
# import os
import time
# import sys
import struct
import logging
# import thread
import threading  # from Telecommand import *
# from CCSDS import *
# from Boot import *
# from Events import *
from contextlib import suppress
from typing import *

from gspy_egse.gui.utils.misc import WrappedMessageHandler, Extendable, call_async
from gspy_egse.gui.hardware_modules.spacewire_events import SpwEvents
from ..utils.externalRecorder import external_recorder, ExternalEvent

logger = logging.getLogger(__name__)

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
        self._external_handler_registered = False
        self._register_external_recorder_handler()


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
        if getattr(self, "_external_handler_registered", False):
            external_recorder.unregister_handler("space-wire", self._handle_external_replay_event)
            self._external_handler_registered = False
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

        if external_recorder.is_replaying:
            logger.info("Skipping SpaceWire send during replay.")
            try:
                preview = ' '.join(f'{byte:02X}' for byte in (sdata[:16] if isinstance(sdata, list) else list(sdata)[:16]))
                if isinstance(sdata, list) and len(sdata) > 16:
                    preview += ' ...'
                self.message_handler.info(f"[Replay] TX {preview or '<empty>'} (suppressed)")
            except Exception:
                pass
            return
        self.spw_raw.send(sdata, self.spw_dest_addr)
        # record outgoing message
        external_recorder.record(
            ExternalEvent(time.time(), "out", "space-wire", list(sdata))
        )

        # record outgoing message
        external_recorder.record(
            ExternalEvent(time.time(), "out", "spacewire", list(sdata))
        )

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
        if message:
            external_recorder.record(
                ExternalEvent(time.time(), "in", "space-wire", list(message))
            )
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

    def _register_external_recorder_handler(self) -> None:
        if not getattr(self, "_external_handler_registered", False):
            external_recorder.register_handler("space-wire", self._handle_external_replay_event)
            self._external_handler_registered = True

    def _handle_external_replay_event(self, event: ExternalEvent) -> None:
        if event.kind != "space-wire" or not external_recorder.is_replaying:
            return
        if event.direction == "out":
            payload = self._payload_to_list(event.payload)
            if payload is None:
                logger.warning("Unable to replay space-wire 'out' event: %r", event.payload)
                return
            call_async(self._send_replay_payload, (payload,))
        else:
            message = self._payload_to_bytes(event.payload)
            if message is None:
                logger.warning("Unable to replay space-wire 'in' event: %r", event.payload)
                return
            call_async(self._deliver_processed_receive, (message,))

    def _deliver_processed_receive(self, payload: bytes) -> None:
        try:
            message = payload
            delivered = False
            for listener in list(self.listeners_decode):
                try:
                    result = listener(message)
                    if result is not None:
                        message = result
                        delivered = True
                except Exception:
                    logger.exception("SpaceWire replay listener failed")
            if not delivered:
                try:
                    self.message_handler.info(f"[Replay] RX {message.hex()}")
                except Exception:
                    pass
            logger.info("Replayed SpaceWire receive (%d bytes)", len(message))
        except Exception:
            logger.exception("Failed to replay SpaceWire receive")

    @staticmethod
    def _payload_to_list(payload: Any) -> Optional[List[int]]:
        if isinstance(payload, list):
            try:
                return [int(v) & 0xFF for v in payload]
            except (TypeError, ValueError):
                return None
        if isinstance(payload, (bytes, bytearray)):
            return list(payload)
        return None

    @staticmethod
    def _payload_to_bytes(payload: Any) -> Optional[bytes]:
        if isinstance(payload, bytes):
            return payload
        if isinstance(payload, bytearray):
            return bytes(payload)
        if isinstance(payload, list):
            try:
                return bytes([int(v) & 0xFF for v in payload])
            except (TypeError, ValueError):
                return None
        if isinstance(payload, str):
            return payload.encode('utf-8')
        return None

    def _send_replay_payload(self, payload: List[int]) -> None:
        if self.spw_raw is None:
            return
        if external_recorder.is_replaying:
            try:
                preview = ' '.join(f'{byte:02X}' for byte in payload[:16])
                if len(payload) > 16:
                    preview += ' ...'
                self.message_handler.info(f"[Replay] TX {preview or '<empty>'}")
            except Exception:
                pass
            logger.info("Simulated SpaceWire send (%d bytes)", len(payload))
            return
        try:
            self.spw_raw.send(payload, self.spw_dest_addr)
            logger.info("Replayed SpaceWire send (%d bytes)", len(payload))
        except Exception:
            logger.exception("Failed to replay SpaceWire send")

    def call_receive_thread_async(self):
        call_async(self.receive_thread)
