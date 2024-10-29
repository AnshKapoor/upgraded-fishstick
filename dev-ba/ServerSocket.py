import queue
import socket
import threading
import time

from enums import Ptype
from enums import Timeouts
from SpacewireConnection import Spacewire


class Server:
    """
    TCP type Socket server, most stable and main result of the thesis.
    :param str host: IPV4 address of host system
    :param int port: port of host system
    """
    def __init__(self, host='127.0.0.1', port=4444):
        self.host = host
        self.port = port

        self.cmdReceiveQueue = queue.Queue()
        self.cmdSendQueue = queue.Queue()

        self.timeoutSocket = Timeouts.TimeoutSocketSek
        self.timeoutQueues = Timeouts.TimeoutSek

        self.reopen = True
        self.active = True
        self.clientSocket = None

        self.receiveThread = None
        self.sendThread = None
        self.cmdThread = None

        self.addr = ""
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.spw = None
        self.run()

    def run(self):
        self.server.bind((self.host, self.port))
        # maximum of one connection: 1
        self.server.listen(1)
        print(f"Server listening on {self.host}:{self.port}")
        self.searchForConnections()

    def main(self):
        """ handles cmd packets"""
        while self.active:
            try:
                item = self.cmdReceiveQueue.get(block=True, timeout=self.timeoutQueues)
                payloadType = item[0]
                payload = item[1]

                match payloadType:
                    case Ptype.DATA.value:
                        sendChannel = payload[0]
                        payload = payload[1:]
                        # -1 for 0 being the config port and not listed in the spw.channels, so channel 1 is at [0]
                        self.spw.channels[sendChannel - 1].sendQueue.put(payload)
                    case Ptype.BYE.value:
                        self.close()
                    case Ptype.CONFIG.value:
                        self.cmdSendQueue.put([Ptype.CONFIG.value, self.spw.configureProperties(payload)])
                    case Ptype.RESET.value:
                        self.cmdSendQueue.put([Ptype.RESET.value, self.spw.resetHw()])
                    case Ptype.STATUS.value:
                        self.cmdSendQueue.put([Ptype.STATUS.value, self.spw.getStatus()])
                    case _:
                        print("invalid Payload type")
            except queue.Empty:
                pass

    def searchForConnections(self):
        """
        accepts incoming tcp socket connection, creates hello packet, puts it to send queue and starts tcp socket
        receive and send threads
        """
        print("searching for connection")
        self.clientSocket, self.addr = self.server.accept()
        print(f"Connection established with {self.addr}")
        print("-------------------------------------------------------------")
        self.clientSocket.settimeout(self.timeoutSocket)

        self.createHelloPacket()

        self.receiveThread = threading.Thread(target=self.receiveMessage, args=()).start()
        self.sendThread = threading.Thread(target=self.sendMessage, args=()).start()
        self.cmdThread = threading.Thread(target=self.main, args=()).start()

    def createHelloPacket(self):
        """..."""
        self.spw = Spacewire()
        payloadHello = self.spw.Hello()

        # normal case
        self.cmdSendQueue.put([Ptype.HELLO.value, payloadHello])

        # workaround for only using one queue
        #msg = bytes(str(Ptype.HELLO.value), 'utf-8') + payloadHello
        #self.clientSocket.send(msg)

        print("Hello packet sent")

    def sortPackets(self, payloadType, payload):
        """..."""
        acceptableCmdTypes = [Ptype.HELLO.value, Ptype.STATUS.value, Ptype.RESET.value, Ptype.CONFIG.value,
                              Ptype.BYE.value]

        if payloadType == Ptype.DATA.value:
            sendChannel = payload[0]
            payload = payload[1:]
            # -1 for 0 being the config port and not listed in the spw.channels, so channel 1 is at [0]
            self.spw.channels[sendChannel - 1].sendQueue.put(payload)
        elif payloadType in acceptableCmdTypes:
            self.cmdReceiveQueue.put([payloadType, payload])
        else:
            print("invalid Payload type")

    def close(self):
        """shuts down the socket server and the spw connection with all its threads"""
        self.active = False
        time.sleep(0.1)
        self.spw.close()
        time.sleep(2)
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
                continue
            except ConnectionResetError:
                break

            if newPacket:
                if dataBufferLength >= HEADERSIZE:
                    while True:
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
                                self.sortPackets(payloadType, payload)
                                dataBuffer = dataBuffer[payloadLength:]
                                dataBufferLength = len(dataBuffer)

                                newPacket = True
                            break
                        else:
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
        print("server receive thread gone")

    def sendMessage(self):
        """send thread for sending messages from server to client (core class)"""
        while self.active:
            # cmd queue
            try:
                # Socket server sending thread looking for packets received over spw on every available channel
                payload = self.cmdSendQueue.get(block=True, timeout=self.timeoutQueues)
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
                pass
            except ConnectionResetError:
                break

            # data queues
            for ch in self.spw.channels:
                try:
                    # Socket server sending thread looking for packets received over spw on every available channel
                    payload = ch.receiveQueue.get(block=True, timeout=self.timeoutQueues)
                    ch.receiveQueue.task_done()
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
