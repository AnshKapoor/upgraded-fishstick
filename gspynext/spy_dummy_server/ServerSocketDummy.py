import queue
import socket
import threading
import time

from gspynext.common.enums import Ptype
from gspynext.common.enums import Timeouts


class Server:
    """
    Dummy server, identical to ServerSocket but with no hardware interface, just the two queues.
    Used in test 1 for 'optimal' performance.
    :param str host: IPV4 address of host system
    :param int port: port of host system
    """

    def __init__(self, host='127.0.0.1', port=5555):
        self.host = host
        self.port = port

        self.cmdDummyQueue = queue.Queue()

        self.dataDummyQueue = queue.Queue()

        self.timeoutSocket = Timeouts.TimeoutSocketSek
        self.timeoutQueues = Timeouts.TimeoutSek

        self.reopen = True
        self.active = True
        self.clientSocket = None
        self.receiveThread = None
        self.sendThread = None
        self.addr = ""
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.run()

    def run(self):
        self.server.bind((self.host, self.port))
        # maximum of one connection: 1
        self.server.listen(1)
        print(f"Server listening on {self.host}:{self.port}")
        self.searchForConnections()

        self.createHelloPacket()

        self.active = True

        self.clientSocket.settimeout(self.timeoutSocket)

        self.receiveThread = threading.Thread(target=self.receiveMessage, args=()).start()
        self.sendThread = threading.Thread(target=self.sendMessage, args=()).start()

    def searchForConnections(self):
        """..."""
        print("searching for new connection")
        self.clientSocket, self.addr = self.server.accept()
        print(f"Connection established with {self.addr}")
        print("-------------------------------------------------------------")

    def Hello(self):
        """
        creates the hello packet for the client providing information, in detail hw device, serial number,
        hw interface type and number if channels
        """
        deviceName = "Dummy0"
        serialNumber = "123456789"
        busType = "Spacewire"
        dataChannelList = [1, 2, 3, 4]

        payload = len(str(deviceName)).to_bytes(1, 'big')
        payload += len(str(serialNumber)).to_bytes(1, 'big')
        payload += len(str(busType)).to_bytes(1, 'big')
        payload += len(str(dataChannelList[-1])).to_bytes(1, 'big')

        payload += deviceName.encode("utf-8")
        payload += serialNumber.encode("utf-8")
        payload += str(busType).encode("utf-8")
        payload += str(dataChannelList[-1]).encode("utf-8")

        return payload

    def createHelloPacket(self):
        """..."""
        payloadHello = self.Hello()
        # type of packet, payload
        self.dataDummyQueue.put([Ptype.HELLO.value, payloadHello])
        print("Hello packet sent")

    def sortPackets(self, payloadType, payload):
        """..."""
        acceptableCmdTypes = [Ptype.HELLO.value, Ptype.STATUS.value, Ptype.RESET.value, Ptype.CONFIG.value]

        if payloadType == Ptype.DATA.value:
            self.dataDummyQueue.put([payloadType, payload])
        elif payloadType == Ptype.BYE.value:
            self.close()
        elif payloadType in acceptableCmdTypes:
            self.cmdDummyQueue.put([payloadType, b'\x00'])
        else:
            print("invalid Payload type")

    def close(self):
        """shuts down the socket server and the spw connection with all its threads"""
        self.active = False
        time.sleep(0.1)
        self.clientSocket.close()

    def receiveMessage(self):
        """receive thread for receiving socket messages from client(core class)"""
        newPacket = True
        startOfPacket = 0
        dataBuffer = b''
        dataBufferLength = 0
        HEADERSIZE = 12

        while self.active:
            try:
                receivedData = self.clientSocket.recv(1024)
                if not receivedData:
                    continue
                dataBuffer += receivedData
                dataBufferLength = len(dataBuffer)
            except socket.timeout:
                pass
            except ConnectionResetError:
                break

            if newPacket:
                if dataBufferLength >= HEADERSIZE:
                    while newPacket and dataBufferLength >= HEADERSIZE:
                        # Check for sync pattern
                        if dataBuffer[startOfPacket:startOfPacket + 5] == b'\xc0\x1d\xc0\xff\xee':
                            payloadLength = int.from_bytes(dataBuffer[startOfPacket + 6:startOfPacket + 9], 'big')
                            protocolVersion = int.from_bytes(dataBuffer[startOfPacket + 5:startOfPacket + 6], 'big')
                            payloadType = int.from_bytes(dataBuffer[startOfPacket + 9:startOfPacket + 10], 'big')

                            dataBuffer = dataBuffer[startOfPacket + HEADERSIZE:]
                            dataBufferLength = len(dataBuffer)

                            startOfPacket = 0
                            newPacket = False

                            if dataBufferLength >= payloadLength:
                                payload = dataBuffer[:payloadLength]
                                self.dataDummyQueue.put([payloadType, payload])
                                dataBuffer = dataBuffer[payloadLength:]
                                dataBufferLength = len(dataBuffer)
                                newPacket = True
                            #break
                        else:
                            startOfPacket += 1
                            # Check for dataBufferLength is bigger than HEADERSIZE + startOfPacket
                            if dataBufferLength < HEADERSIZE + startOfPacket:
                                break
            else:
                if dataBufferLength >= payloadLength:
                    payload = dataBuffer[:payloadLength]
                    self.dataDummyQueue.put([payloadType, payload])
                    dataBuffer = dataBuffer[payloadLength:]
                    dataBufferLength = len(dataBuffer)
                    newPacket = True

        self.active = False
        print("server receive thread gone")

    def sendMessage(self):
        """send thread for sending messages from server to client (core class)"""
        while self.active:
            # data queues
            try:
                # Socket server sending thread looking for packets received over spw on every available channel
                payload = self.dataDummyQueue.get(block=True, timeout=self.timeoutQueues)
                self.dataDummyQueue.task_done()
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
                self.time2 = time.perf_counter_ns()
                self.clientSocket.send(msg)

            except queue.Empty:
                pass
            except ConnectionResetError:
                break

            #cmd queue
            try:
                # Socket server sending thread looking for packets received over spw on every available channel
                payload = self.cmdDummyQueue.get(block=True, timeout=self.timeoutQueues)
                self.cmdDummyQueue.task_done()
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
                pass
            except ConnectionResetError:
                break

        self.active = False
        print("server send thread gone")


if __name__ == "__main__":
    server = Server()
