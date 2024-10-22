import socket
import threading
import queue
import time

from enums import Ptype
from enums import Timeouts


class Client(threading.Thread):
    """socket type client"""
    def __init__(self, host, port, ID):
        super(Client, self).__init__()
        self.receiveThread = None
        self.sendThread = None

        self.sendQueue = queue.Queue()
        self.receiveQueue = queue.Queue()
        self.cmdReceiveQueue = queue.Queue()
        self.cmdSendQueue = queue.Queue()

        self.host = host
        self.port = port
        self.ID = ID
        self.active = True

        self.hwDevice = None
        self.serialNumber = None
        self.hwInterfaceType = None
        self.numChannels = None

        self.timeoutSek = Timeouts.TimeoutSek

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def run(self):
        self.client.connect((self.host, self.port))
        self.client.settimeout(self.timeoutSek)

        self.receiveThread = threading.Thread(target=self.receiveMessage, args=())
        self.receiveThread.start()

        self.sendThread = threading.Thread(target=self.sendMessage, args=())
        self.sendThread.start()

    def close(self):
        self.active = False
        time.sleep(0.1)
        self.client.close()

    def main(self):
        pass

    def receiveMessage(self):
        """receive thread for socket communication, receiving from server, storing in queue to be sent via spw"""
        newPacket = True
        startOfPacket = 0
        dataBuffer = b''
        dataBufferLength = 0
        HEADERSIZE = 12

        while self.active:
            try:
                receivedData = self.client.recv(4096)
                if not receivedData:
                    continue
                dataBuffer += receivedData
                dataBufferLength = len(dataBuffer)
            except socket.timeout:
                continue
            except ConnectionResetError:
                self.cmdReceiveQueue.put([Ptype.BYE.value, b'\x00'])
                break

            if newPacket:
                if dataBufferLength >= HEADERSIZE:
                    while True:
                        # Check for sync pattern
                        if dataBuffer[startOfPacket:startOfPacket + 5] == b'\xc0\x1d\xc0\xff\xee':
                            payloadLength = int.from_bytes(dataBuffer[startOfPacket + 6:startOfPacket + 9], 'big')
                            protocolVersion = int.from_bytes(dataBuffer[startOfPacket + 5:startOfPacket + 6], 'big')
                            payloadType = int.from_bytes(dataBuffer[startOfPacket + 9:startOfPacket + 10], 'big')

                            if dataBufferLength == startOfPacket + HEADERSIZE:
                                dataBuffer = b''
                                dataBufferLength = 0
                            else:
                                dataBuffer = dataBuffer[startOfPacket + HEADERSIZE:]
                                dataBufferLength = len(dataBuffer)
                            startOfPacket = 0

                            if dataBufferLength >= payloadLength:
                                payload = dataBuffer[:payloadLength]
                                self.sortPackets(payloadType, payload)
                                dataBuffer = dataBuffer[payloadLength:]
                                dataBufferLength = len(dataBuffer)
                                newPacket = True
                            else:
                                newPacket = False
                            break
                        else:
                            #print("Packet Sync pattern NOT found!")
                            startOfPacket += 1
                            # Check for dataBufferLength is bigger than HEADERSIZE + startOfPacket
                            if dataBufferLength < HEADERSIZE + startOfPacket:
                                break
            else:
                if dataBufferLength >= payloadLength:
                    payload = dataBuffer[:payloadLength]
                    self.sortPackets(payloadType, payload)
                    dataBuffer = dataBuffer[payloadLength:]
                    dataBufferLength = len(dataBuffer)
                    newPacket = True

        self.active = False
        print("client receive thread gone")

    def sortPackets(self, payloadType, payload):
        """..."""
        acceptableCmdTypes = [Ptype.HELLO.value, Ptype.STATUS.value, Ptype.RESET.value, Ptype.CONFIG.value,
                              Ptype.BYE.value]

        if payloadType == Ptype.DATA.value:
            print(f"{time.perf_counter_ns()} in recv client sort packets")
            self.receiveQueue.put(payload)
        elif payloadType in acceptableCmdTypes:
            self.cmdReceiveQueue.put([payloadType, payload])
        else:
            print("invalid Payload type")

    def sendMessage(self):
        """send thread for socket communication, sending from client to server"""
        while self.active:
            try:
                payload = self.sendQueue.get(block=True, timeout=self.timeoutSek)
                print(f"{time.perf_counter_ns()} client send after queue get")
                self.sendQueue.task_done()
                # Sync pattern (5 bytes chars)
                header = b'\xc0\x1d\xc0\xff\xee'
                # protocol version (1 Byte uint -> 0-255)
                header += b'\x00'
                # length payload (uint -> 0-16.777.216 bytes payload)
                header += len(payload[1]).to_bytes(3, 'big')
                # type of payload (1 byte enum)
                header += payload[0].to_bytes(1, 'big')
                # reserved (2 byte)
                header += b'\x00\x00'

                if not isinstance(payload[1], bytes):
                    msg = header + bytes(str(payload[1]), "utf-8")
                else:
                    msg = header + payload[1]
                self.client.send(msg)
                print(f"{time.perf_counter_ns()} client send after send")
            except queue.Empty:
                pass
            except ConnectionResetError:
                break

            try:
                payload = self.cmdSendQueue.get(block=True, timeout=self.timeoutSek)
                self.cmdSendQueue.task_done()
                # Sync pattern (5 bytes chars)
                header = b'\xc0\x1d\xc0\xff\xee'
                # protocol version (1 Byte uint -> 0-255)
                header += b'\x00'
                # length payload (uint -> 0-16.777.216 bytes payload)
                header += len(payload[1]).to_bytes(3, 'big')
                # type of payload (1 byte enum)
                header += payload[0].to_bytes(1, 'big')
                # reserved (2 byte)
                header += b'\x00\x00'

                if not isinstance(payload[1], bytes):
                    msg = header + bytes(str(payload[1]), "utf-8")
                else:
                    msg = header + payload[1]
                self.client.send(msg)
            except queue.Empty:
                pass
            except ConnectionResetError:
                break

        self.active = False
        print("client send thread gone")
