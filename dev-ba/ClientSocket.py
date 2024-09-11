import socket
import threading
import queue
import struct
import time
import pickle


class Client(threading.Thread):
    """socket type client, for now matching requirements for spwbrickmk4"""
    def __init__(self, receiveQueue, sendQueue, host='127.0.0.1', port=5555):
        super(Client, self).__init__()
        self.receiveThread = None
        self.sendThread = None
        self.sendQueue = sendQueue
        self.receiveQueue = receiveQueue
        self.host = host
        self.port = port
        self.active = True
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def run(self):
        self.client.connect((self.host, self.port))
        self.client.settimeout(0.001)
        self.receiveThread = threading.Thread(target=self.receiveMessage, args=())
        self.receiveThread.start()
        self.sendThread = threading.Thread(target=self.sendMessage(), args=())
        self.sendThread.start()

    def endConnection(self):
        self.active = False
        time.sleep(0.1)
        self.client.close()

    def receiveMessage(self):
        """receive thread for socket communication, receiving from server, storing in queue to be sent via spw"""
        while self.active:
            try:
                # 2 Byte length prefix ( maximum message length 65535)
                length_data = self.client.recv(2)
                # get length (first list element) as int form byte
                length = struct.unpack('!h', length_data)[0]
                item = self.client.recv(length)
                if not item:
                    continue
                print(f"{item} received on socket client")
                self.receiveQueue.put(item)
            except socket.timeout:
                continue
            except ConnectionResetError:
                break
        print("client receive thread gone")

    def sendMessage(self):
        """send thread for socket communication, sending from client to server"""
        while self.active:
            try:
                item = self.sendQueue.get(block=False)
                self.sendQueue.task_done()
                # 2-byte length prefix
                # length = struct.pack('!h', len(item[0:-1]) + 8)

                # 1 type, 1 origin, 1 destination, 8 timestamp, 2 length payload, x payload, so 13 + x
                # length = bytearray([len(item.payload) + 13])
                # print(f"{length=}")

                dataString = pickle.dumps(item)
                length = struct.pack('!h', len(dataString))
                print(length)
                self.client.send(length)
                self.client.send(dataString)

                print(f"{item.payload} in send thread socket client")
            except queue.Empty:
                continue
            except ConnectionResetError:
                break
        print("client send thread gone")
