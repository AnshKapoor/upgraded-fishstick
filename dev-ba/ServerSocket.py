import socket
import threading
import json
import time
from SpacewireConnection import Spacewire


class Server(threading.Thread):
    """
    Socket type server
    :param str host: IPV4 address of host system
    :param int port: port of host system
    """
    def __init__(self, host='127.0.0.1', port=5555):
        super(Server, self).__init__()
        self.host = host
        self.port = port
        self.clients = []
        self.client_handler = None
        self.config_list = None
        self.connections = []
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def run(self):
        self.server.bind((self.host, self.port))
        self.server.listen()
        print(f"Server listening on {self.host}:{self.port}")

        self.loadConfig()
        self.createConnections()
        self.searchForConnections()

    def loadConfig(self, filename="config.json"):
        """
        loads config file
        :param str filename: filename of json configuration file, needs to be in the same directory
        """
        with open(filename) as user_file:
            file_contents = user_file.read()
        self.config_list = json.loads(file_contents)
        
    def createConnections(self):
        """
        create instances of connection classes according to loaded configuration,
        they themselves start the socket clients
        """
        for i in range(len(self.config_list)):
            match self.config_list[i].get("type"):
                case "spwBrickMK4":
                    _ = Spacewire(self.config_list[i])
                    self.connections.append(_)

    def searchForConnections(self):
        try:
            while True:
                client_socket, addr = self.server.accept()
                print(f"Connection established with {addr}")
                self.client_handler = threading.Thread(target=self.clientHandler, args=(client_socket, addr))
                self.client_handler.start()
        except:
            print("An error occurred")
        finally:
            self.server.close()
            for client in self.clients:
                client.close()

    def clientHandler(self, clientSocket, addr):
        """method for handling client connections"""
        self.clients.append(clientSocket)
        try:
            while True:
                message = clientSocket.recv(1024).decode('utf-8')
                if not message:
                    break
                print(f"Server received: {message} from client on port {addr[1]}")
                print("--------------------------------------")
                # self.send(clientSocket, "ack from server")
                # TODO decode message, maybe sort by connection type, move to DB or extensions
        except ConnectionResetError:
            pass
        finally:
            self.clients.remove(clientSocket)
            clientSocket.close()

    def send(self, clientSocket, message):
        clientSocket.send(message.encode('utf8'))
