import socket
import struct
import threading

try:
    from ..hardware_modules.spacewire import ISpaceWireBridge
except (ValueError, ImportError):
    from hardware_modules.spacewire import ISpaceWireBridge


class SpaceWireBridgeShimafuji(ISpaceWireBridge):
    def __init__(self, tcp_ip='127.0.0.1', tcp_port=10029):
        self.tcp_ip = tcp_ip
        self.tcp_port = tcp_port
        self.conn_open = False
        self.socket = None

        self.lock = threading.Lock()
        self.error_printer = print

    def __del__(self):
        self.close()

    def set_rt_entry(self, address, routing):
        # Calculate memory address on bridge
        bridge_address = 0x80 + 4 * (address - 0x20)
        # Write entry
        self.rmap_write(bridge_address, struct.pack('<I', routing))

    @property
    def is_open(self):
        return self.conn_open

    def open(self):
        self.conn_open = True

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.tcp_ip, self.tcp_port))
        except Exception as e:
            self.error_printer(str(e))
            self.conn_open = False

        # Optional speed settings
        # self.rmap_write(0x004, struct.pack('<I', 0x31050000))

        # Misc routing
        self.set_rt_entry(0x46, 0x40)
        self.set_rt_entry(0x20, 0x20)

        # DPU -> EGSE: Software to port 06
        self.set_rt_entry(0x35, 0x40)
        # DPU -> EGSE: Bootloader to port 06
        self.set_rt_entry(0x49, 0x40)
        # EGSE -> DPU: Bootloader and Software to port 01
        self.set_rt_entry(0x45, 0x02)

    def close(self):
        if self.conn_open:
            self.socket.close()

    def send(self, send_data: bytes, dest_addr: int = None):
        if not self.conn_open:
            return

        payload = b'\x00\x00\x00\x00\x00\x00\x00\x00'

        if dest_addr is None:
            length = len(send_data)
            payload += struct.pack('>I', length)
        else:
            length = len(send_data) + 1
            payload += struct.pack('>I', length)
            payload += struct.pack('>B', dest_addr)

        payload += send_data

        self.socket.send(payload)

    def receive(self) -> bytes:
        if not self.conn_open:
            return bytes()

        recv = self.socket.recv

        header = recv(12)
        while len(header) < 12:
            header += recv(12 - len(header))
        length = struct.unpack('>L', header[8:12])[0] & 0x00ffffff
        message = bytes()

        while len(message) < length:
            message += recv(length - len(message))

        # self.error_printer(len(message))
        return message

    def rmap_write(self, addr, sdata):
        import rmap_crc8
        length = len(sdata)
        header = '\xfe'  # destination
        header += '\x01'  # protocol id
        header += '\x71'  # write
        header += '\x02'  # destination key
        header += '\x00\x00\x00\x06'  # reply address
        header += '\x06'  # initiator logical addr.
        header += '\x00\x00'  # transaction id
        header += '\x00'  # external address
        header += struct.pack('>I', addr)  # rmap address
        header += struct.pack('>I', length & 0xffffff)[1:]  # length

        hash_ = rmap_crc8.crc8()
        hash_.update(header)
        header += hash_.digest()  # crc

        payload = header
        payload += sdata

        hash_data = rmap_crc8.crc8()
        hash_data.update(sdata)
        payload += hash_data.digest()

        self.send(payload, 0x00)
        self.receive()
