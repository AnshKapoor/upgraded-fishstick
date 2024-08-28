import queue
import time
import random
import strictyaml
import path

from ClientSocket import Client
from DataHandlerCore import DataHandler


class Core:
    def __init__(self):
        self.parsedConfig = {}
        self.clients = []
        self.client = None

        self.receiveQueue = queue.Queue()
        self.sendQueue = queue.Queue()

        self.dataHandler = DataHandler(self.receiveQueue, self.sendQueue)
        self.dataHandler.start()

        self.loadConfig()
        self.createClients()

    def createClients(self):
        for conn in self.parsedConfig["connections"]["spacewire"]:
            match conn:
                case "brickmk4":
                    self.client = Client(self.receiveQueue, self.sendQueue)
                    self.client.start()
                    self.clients.append(self.client)
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
                    strictyaml.Optional("sendChannel"): strictyaml.Int(),
                    strictyaml.Optional("receiveChannel"): strictyaml.Int()
                })),
                "SPI": strictyaml.Map({
                    "port": strictyaml.Str(),
                    "baudrate": strictyaml.Int(),
                    "timeout": strictyaml.Int()
                }),
                "powersupply": strictyaml.Map({
                    "channel": strictyaml.Int(),
                    "polling": strictyaml.Bool(),
                    "polling_intervall": strictyaml.Int(),
                    "port": strictyaml.Str(),
                    "baudrate": strictyaml.Int()
                })
            })
        })
        self.parsedConfig = strictyaml.load(path.Path(inputFile).read_text(), schema).data


if __name__ == "__main__":
    c = Core()
    # for j in range(5):
    #     l = [random.randrange(10) for i in range(16 - 2 * j)]
    #     c.sendQueue.put(l)

    while True:
        time.sleep(1)
        n = input("message: ")
        nListInt = list(map(int, n.split(" ")))
        c.sendQueue.put(nListInt)
        if n == "255":
            c.client.endConnection()
            break
