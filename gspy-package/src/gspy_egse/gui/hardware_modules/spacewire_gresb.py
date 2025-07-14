import socket
import struct
import threading
from typing import *

from gspy_egse.gui.hardware_modules.spacewire import ISpaceWireBridge

class SpaceWireBridgeGresb(ISpaceWireBridge):
    def __init__(self, tcp_ip='127.0.0.1', tcp_port=3000):
        self.tcp_ip = tcp_ip
        self.tcp_port = tcp_port
        self.tx_open = False
        self.rx_open = False
        self.tx_s = None  # type: socket.socket
        self.rx_s = None  # type: socket.socket
        self.timeout = 5.0

        self.lock = threading.Lock()
        self.error_printer = print

    def __del__(self):
        self.close()

    @property
    def is_open(self):
        return self.tx_open and self.rx_open

    def open(self):
        self.tx_open = True
        self.rx_open = True

        try:
            self.tx_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tx_s.settimeout(self.timeout)
            self.tx_s.connect((self.tcp_ip, self.tcp_port))
        except Exception as e:
            self.error_printer(e)
            self.tx_open = False

        try:
            self.rx_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.rx_s.settimeout(self.timeout)
            self.rx_s.connect((self.tcp_ip, self.tcp_port + 1))
        except Exception as e:
            self.error_printer(e)
            self.rx_open = False

    def close(self):
        if self.tx_open:
            self.tx_s.close()
        if self.rx_open:
            self.rx_s.close()

    def send(self, send_data: bytes, dest_addr: int = None):
        if not self.tx_open:
            return

        if dest_addr is None:
            length = len(send_data)
            payload = struct.pack('>I', length)
        else:
            length = len(send_data) + 1
            payload = struct.pack('>I', length)
            payload += struct.pack('>B', dest_addr)

        payload += send_data
        self.tx_s.send(payload)

    def receive(self) -> Optional[bytes]:
        """
        Get one package from the dpu

        :return: The received packet, if one could be received, otherwise None
        """
        if not self.rx_open:
            return bytes()

        recv = self.rx_s.recv

        try:
            header = recv(4)
            while len(header) < 4:
                header += recv(4 - len(header))

            message = bytes()
            length = struct.unpack('>L', header[0:4])[0] & 0x00ffffff
            while len(message) < length:
                message += recv(length - len(message))
        except socket.timeout:
            self.error_printer("Timeout")
            return

        # self.error_printer(length)

        return message
