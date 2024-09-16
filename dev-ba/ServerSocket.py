import queue
import socket
import threading
import struct
import time

from enums import Ptype
from SpacewireConnection import Spacewire


class Server(threading.Thread):
    """
    TCP type Socket server
    :param str host: IPV4 address of host system
    :param int port: port of host system
    """
    def __init__(self, host='127.0.0.1', port=5555):
        super(Server, self).__init__()
        self.host = host
        self.port = port

        self.receiveQueue = queue.Queue()
        self.sendQueue = queue.Queue()

        self.cmdReceiveQueue = queue.Queue()
        self.cmdSendQueue = queue.Queue()

        self.reopen = True
        self.active = True
        self.clientSocket = None
        self.receiveThread = None
        self.sendThread = None
        self.addr = ""
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.spw = Spacewire()

    def run(self):
        self.server.bind((self.host, self.port))
        # maximum of one connection: 1
        self.server.listen(1)
        print(f"Server listening on {self.host}:{self.port}")
        self.searchForConnections()

    def createHelloPacket(self):
        payloadHello = self.spw.Hello()
        # type of packet, payload
        self.cmdSendQueue.put([Ptype.HELLO.value, payloadHello])
        print("Hello packet sent")

    def sortPackets(self, payloadType, payload):
        match payloadType:
            case Ptype.DATA.value:
                print(f"{payloadType=} {payload=}")
            case _:
                print("invalid Payload type")

    def searchForConnections(self):
        """..."""
        print("searching for new connection")
        self.clientSocket, self.addr = self.server.accept()
        print(f"Connection established with {self.addr}")
        print("-------------------------------------------------------------")
        self.createHelloPacket()

        self.active = True

        self.clientSocket.settimeout(0.001)

        self.receiveThread = threading.Thread(target=self.receiveMessage, args=()).start()
        self.sendThread = threading.Thread(target=self.sendMessage, args=()).start()

    def closeConnectionToClient(self):
        """..."""
        self.active = False
        self.clientSocket.close()
        if self.reopen:
            self.searchForConnections()

    def receiveMessage(self):
        """receive thread for receiving socket messages from client(core class)"""
        newPacket = True
        startOfPacket = 0
        dataBuffer = b''
        dataBufferLength = 0
        HEADERSIZE = 12

        while self.active:
            try:
                receivedData = self.clientSocket.recv(128)
                if not receivedData:
                    continue
                dataBuffer += receivedData
                dataBufferLength = len(dataBuffer)
            except socket.timeout:
                continue
            except ConnectionResetError:
                break

            print("dataBuffer: " + str(dataBuffer))
            print("dataBuffer length: " + str(dataBufferLength))

            if newPacket:
                if dataBufferLength >= HEADERSIZE:
                    while True:
                        # Check for sync pattern
                        if dataBuffer[startOfPacket:startOfPacket + 5] == b'\xc0\x1d\xc0\xff\xee':
                            print("Packet Sync pattern found!")
                            payloadLength = int.from_bytes(dataBuffer[startOfPacket + 6:startOfPacket + 9], 'big')
                            print(f"{payloadLength=}")
                            protocolVersion = int.from_bytes(dataBuffer[startOfPacket + 5:startOfPacket + 6], 'big')
                            print(f"{protocolVersion=}")
                            payloadType = int.from_bytes(dataBuffer[startOfPacket + 9:startOfPacket + 10], 'big')
                            print(f"payloadType={Ptype(payloadType).name}")

                            if dataBufferLength == startOfPacket + HEADERSIZE:
                                dataBuffer = b''
                                dataBufferLength = 0
                            else:
                                dataBuffer = dataBuffer[startOfPacket + HEADERSIZE:]
                                dataBufferLength = len(dataBuffer)
                            startOfPacket = 0

                            if dataBufferLength >= payloadLength:
                                payload = dataBuffer[:payloadLength]

                                print("Full payload received: " + str(payload))
                                self.sortPackets(payloadType, payload)
                                dataBuffer = dataBuffer[payloadLength:]
                                dataBufferLength = len(dataBuffer)
                                print("dataBuffer after payload cut: " + str(dataBuffer))
                                print("-----------------------")

                                newPacket = True
                            else:
                                newPacket = False
                            break
                        else:
                            print("Packet Sync pattern NOT found!")

                            startOfPacket += 1
                            # Check for dataBufferLength is bigger than HEADERSIZE + startOfPacket
                            if dataBufferLength < HEADERSIZE + startOfPacket:
                                break
                else:
                    print("Packet header not completely received, waiting for more data...")
            else:
                if dataBufferLength >= payloadLength:
                    payload = dataBuffer[:payloadLength]

                    print("Full payload received: " + str(payload))
                    self.sortPackets(payloadType, payload)

                    dataBuffer = dataBuffer[payloadLength:]
                    dataBufferLength = len(dataBuffer)
                    print("dataBuffer after payload cut: " + str(dataBuffer))

                    newPacket = True
                else:
                    print("Payload not completely received, waiting for more data...")

        self.active = False
        print("server receive thread gone")

    def sendMessage(self):
        """send thread for sending messages from server to client (core class)"""
        while self.active:
            # cmd queue
            try:
                # Socket server sending thread looking for packets received over spw on every available channel
                payload = self.cmdSendQueue.get(block=False)
                self.cmdSendQueue.task_done()
                # Sync pattern (5 bytes chars)
                header = b'\xc0\x1d\xc0\xff\xee'
                # protocol version (1 Byte uint -> 0-255)
                header += b'\x00'
                # length payload (uint -> 0-16.777.216 bytes payload)
                header += len(payload[1]).to_bytes(3, 'big')
                # type of payload (1 byte enum)
                header += int(payload[0]).to_bytes(1, 'big')
                # reserved (2 byte)
                header += b'\x00\x00'

                if not isinstance(payload[1], bytes):
                    msg = header + bytes(str(payload[1]), "utf-8")
                else:
                    msg = header + payload[1]

                self.clientSocket.send(msg)
            except queue.Empty:
                continue
            except ConnectionResetError:
                break

            # data queues
            for ch in self.spw.channels:
                try:
                    # Socket server sending thread looking for packets received over spw on every available channel
                    payload = ch.receiveQueue.get(block=False)
                    self.sendQueue.task_done()
                    # Sync pattern (5 bytes chars)
                    header = b'\xc0\x1d\xc0\xff\xee'
                    # protocol version (1 Byte uint -> 0-255)
                    header += b'\x00'
                    # length payload (uint -> 0-16.777.216 bytes payload)
                    header += len(payload[1]).to_bytes(3, 'big')
                    # type of payload (1 byte enum)
                    header += int(payload[0]).to_bytes(1, 'big')
                    # reserved (2 byte)
                    header += b'\x00\x00'

                    if not isinstance(payload[1], bytes):
                        msg = header + bytes(str(payload[1]), "utf-8")
                    else:
                        msg = header + payload[1]

                    self.clientSocket.send(msg)
                except queue.Empty:
                    continue
                except ConnectionResetError:
                    break

        self.active = False
        print("server send thread gone")


if __name__ == "__main__":
    server = Server()
    server.start()
