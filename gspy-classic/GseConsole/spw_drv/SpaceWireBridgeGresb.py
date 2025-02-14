import socket
import struct
import thread


class SpaceWireBridgeGresb(object):
    def __init__(self, tcp_ip='127.0.0.1', tcp_port=3000):
        self.tcp_ip = tcp_ip
        self.tcp_port = tcp_port
        self.tx_open = False
        self.rx_open = False
        self.tx_s, self.rx_s = None, None

        self.lock = thread.allocate_lock()

    def __del__(self):
        self.close()

    def open(self):
        self.tx_open = True
        self.rx_open = True

        try:
            self.tx_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tx_s.connect((self.tcp_ip, self.tcp_port))
        except Exception, e:
            print(str(e))
            self.tx_open = False

        try:
            self.rx_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.rx_s.connect((self.tcp_ip, self.tcp_port + 1))
        except Exception, e:
            print(str(e))
            self.rx_open = False

    def close(self):
        if self.tx_open:
            self.tx_s.close()
        if self.rx_open:
            self.rx_s.close()

    def send(self, sdata, dest_addr=None):
        if not self.tx_open:
            return

        if dest_addr is None:
            length = len(sdata)
            payload = struct.pack('>I', length)
        else:
            length = len(sdata) + 1
            payload = struct.pack('>I', length)
            payload += struct.pack('>B', dest_addr)

        payload += sdata
        self.tx_s.send(payload)

    def receive(self):
        if not self.rx_open:
            return ''

        recv = self.rx_s.recv

        header = recv(4)
        while len(header) < 4:
            header += recv(4 - len(header))

        message = ''
        length = struct.unpack('>L', header[0:4])[0] & 0x00ffffff
        while len(message) < length:
            message += recv(length - len(message))

        # print(length)

        return message
