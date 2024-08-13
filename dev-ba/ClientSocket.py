import socket
import threading


class Client(threading.Thread):
    """socket type client, for now matching requirements for spwbrickmk4"""
    def __init__(self, serverToClient, clientToServer, host='127.0.0.1', port=5555):
        super(Client, self).__init__()
        self.receiveThread = None
        self.sendThread = None
        self.clientToServerQueue = clientToServer
        self.serverToClientQueue = serverToClient
        self.host = host
        self.port = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def run(self):
        self.client.connect((self.host, self.port))
        self.receiveThread = threading.Thread(target=self.receiveMessages, args=()).start()
        self.sendThread = threading.Thread(target=self.sendMessage(), args=()).start()

    def receiveMessages(self):
        """receive thread for socket communication, receiving from server, storing in queue to be sent via spw"""
        while True:
            try:
                message = self.client.recv(1024).decode('utf-8')
                if not message:
                    break
                print(f"{message} received on socket client")
                self.serverToClientQueue.put(message)
            except:
                break

    def sendMessage(self):
        """send thread for socket communication, sending from client to server"""
        while True:
            item = self.clientToServerQueue.get(block=True, timeout=None)
            self.clientToServerQueue.task_done()
            self.client.send(str(item).encode('utf-8'))
            print(f"{item} in send thread socket client")
