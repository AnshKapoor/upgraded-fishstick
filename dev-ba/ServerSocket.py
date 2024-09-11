import queue
import socket
import threading
import struct
from datetime import datetime
import pickle


class Server(threading.Thread):
    """
    TCP type Socket server
    :param sendQueue:
    :param receiveQueue:
    :param str host: IPV4 address of host system
    :param int port: port of host system
    """
    def __init__(self, sendQueue, receiveQueue, cmdSendQueue, cmdReceiveQueue, host='127.0.0.1', port=5555):
        super(Server, self).__init__()
        self.host = host
        self.port = port

        self.sendQueue = sendQueue
        self.receiveQueue = receiveQueue
        self.cmdSendQueue = cmdSendQueue
        self.cmdReceiveQueue = cmdReceiveQueue

        self.reopen = True
        self.active = True
        self.clientSocket = None
        self.receiveThread = None
        self.sendThread = None
        self.addr = ""
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def run(self):
        self.server.bind((self.host, self.port))
        # maximum of one connection: 1
        self.server.listen(1)
        print(f"Server listening on {self.host}:{self.port}")

        self.searchForConnections()

    def searchForConnections(self):
        """..."""
        print("searching for new connection")
        self.clientSocket, self.addr = self.server.accept()
        print(f"Connection established with {self.addr}")

        self.active = True

        self.clientSocket.settimeout(0.001)

        self.receiveThread = threading.Thread(target=self.receiveMessage, args=()).start()
        self.sendThread = threading.Thread(target=self.sendMessage(), args=()).start()

        while self.active:
            pass
        self.closeConnectionToClient()

    def closeConnectionToClient(self):
        """..."""
        self.active = False
        self.clientSocket.close()
        if self.reopen:
            self.searchForConnections()

    def receiveMessage(self):
        """receive thread for receiving socket messages from client(core class)"""
        while self.active:
            try:
                # 2 Byte length prefix ( maximum message length 65535)
                length_data = self.clientSocket.recv(2)
                # client closed connection, message received is b''
                if not length_data:
                    print("connection closed by client")
                    self.reopen = False
                    break
                length = struct.unpack('!h', length_data)[0]
                message = self.clientSocket.recv(length)
                data = pickle.loads(message)
                match data.ptype:
                    case 1:
                        self.receiveQueue.put(data)
                    case 2:
                        self.cmdReceiveQueue.put(data)
                    case _:
                        print("invlaid packet format")

                print(f"Server received: {data.payload} from client on port {self.addr[1]}")
                print(vars(data))

                print("------------------------------------------------------------------------------------")
            except socket.timeout:
                continue
            except ConnectionResetError:
                print("connection reset")
                break
            except struct.error:
                print("struct error")
                break
        self.active = False
        print("server receive thread gone")

    def sendMessage(self):
        """send thread for sending messages from server to client (core class)"""
        while self.active:
            # check data queue for packets
            try:
                item = self.sendQueue.get(block=False)
                self.sendQueue.task_done()
                # 2-byte length prefix
                length = struct.pack('!h', len(item))
                self.clientSocket.send(length)
                self.clientSocket.send(bytes(item))
                print(f"{item} in Socket server send")
            except queue.Empty:
                pass
            except ConnectionResetError:
                break

            # check cmd queue for packets
            try:
                item = self.cmdSendQueue.get(block=False)
                self.sendQueue.task_done()
                length = struct.pack('!h', len(item))  # 2-byte length prefix
                self.clientSocket.send(length)
                self.clientSocket.send(bytes(item))
                print(f"{item} in Socket server send")
            except queue.Empty:
                pass
            except ConnectionResetError:
                break

        self.active = False
        print("server send thread gone")
