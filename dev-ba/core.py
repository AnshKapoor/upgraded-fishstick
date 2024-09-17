import queue
import strictyaml
import path

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
            match conn:
                case "brickmk4":
                    host = self.parsedConfig["connections"]["spacewire"]["brickmk4"]["host"]
                    port = self.parsedConfig["connections"]["spacewire"]["brickmk4"]["port"]
                    receiveQueue = queue.Queue()
                    sendQueue = queue.Queue()

                    client = Client(self.dataHandler, receiveQueue, sendQueue, self.cmdReceiveQueue, self.cmdSendQueue,
                                    host, port, ID)
                    client.start()
                    self.clients.append(client)
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

    while True:
        n = input()
        h = bytes(n, "utf-8")
        if n == "exit":
            break
        if n == "test":
            h = b'\xc0\x1d\xc0\xff\xee'
        c.dataHandler.toSendQueue(0, Ptype.DATA.value, h)
