import queue
import strictyaml
import path
import time

from ClientSocket import Client
from DataHandlerCore import DataHandler
from enums import Ptype


class Core:
    def __init__(self):
        self.parsedConfig = {}
        self.clients = []
        self.dataHandler = DataHandler()
        self.cmdSendQueue = queue.Queue()
        self.cmdReceiveQueue = queue.Queue()
        self.main()

    def main(self):
        self.loadConfig()
        self.createClients()
        self.dataHandler.start()

    def createClients(self):
        """..."""
        for ID, conn in enumerate(self.parsedConfig["connections"]["spacewire"]):
            connType = self.parsedConfig["connections"]["spacewire"][conn]["connectionType"]
            match connType:
                case "Spacewire":
                    host = self.parsedConfig["connections"]["spacewire"][conn]["host"]
                    port = self.parsedConfig["connections"]["spacewire"][conn]["port"]
                    receiveQueue = queue.Queue()
                    sendQueue = queue.Queue()

                    print(host, port, ID)

                    client = Client(self.dataHandler, receiveQueue, sendQueue, self.cmdReceiveQueue, self.cmdSendQueue,
                                    host, port, ID)
                    client.start()
                    self.clients.append(client)
                    print(self.clients[ID].port)
                case _:
                    print(f"{conn} not supported yet.")

    def loadConfig(self, inputFile="config.yaml"):
        """
        loads config file using strictyaml
        :param str inputFile: filename of yaml configuration file, needs to be in the same directory
        """
        schema = strictyaml.Map({
            "connections": strictyaml.Map({
                "spacewire": strictyaml.MapCombined({}, strictyaml.Str(), strictyaml.Map({
                    "host": strictyaml.Str(),
                    "port": strictyaml.Int(),
                    "connectionType": strictyaml.Str()
                }))
            })
        })
        self.parsedConfig = strictyaml.load(path.Path(inputFile).read_text(), schema).data

    def close(self):
        for cl in self.clients:
            cl.close()


if __name__ == "__main__":
    c = Core()

    while True:
        time.sleep(0.1)

        ID = input("choose ID")
        channel = input("choose channel")
        size = input("size payload")
        payload = channel.encode('utf-8') + bytearray(int(size))
        c.dataHandler.toSendQueue(int(ID), Ptype.DATA.value, payload)

        # id = input("choose ID")
        # c.dataHandler.toSendQueue(int(id), Ptype.BYE.value, b'\x00')

        # n = input()
        # if n == "exit":
        #     break
        # if n == "t1":
        #     h = b'\x01\xaa\xbb\xcc\xdd\xee'
        #     c.dataHandler.toSendQueue(0, Ptype.DATA.value, h)
        # elif n == "t2":
        #     h = b'\x02\xaa\xbb\xcc\xdd\xee'
        #     c.dataHandler.toSendQueue(0, Ptype.DATA.value, h)
        # elif n == "bye":
        #     c.dataHandler.toSendQueue(0, Ptype.BYE.value, b'\x00')
        #     time.sleep(1)
        #     c.close()
        #     break
        # elif n == "big":
        #     _ = b'\x99'
        #     payload = bytearray(100)
        #     c.dataHandler.toSendQueue(0, Ptype.DATA.value, _ + payload)
