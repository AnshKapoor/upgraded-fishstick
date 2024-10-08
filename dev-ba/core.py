import queue
import threading

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
        self.timeoutSek = 0.000000001
        self.main()

    def main(self):
        self.loadConfig()
        self.dataHandler.start()
        self.createClients()
        threading.Thread(target=self.cmdManagingThread, args=()).start()

    def cmdManagingThread(self):
        """main thread of the core for managing all incoming cmd packets"""
        while True:
            for cl in self.clients:
                try:
                    item = cl.cmdReceiveQueue.get(block=True, timeout=self.timeoutSek)
                    # match payloadType
                    match item[2]:
                        case Ptype.HELLO.value:
                            ID = item[0]
                            port = item[1]
                            payload = item[3]
                            # get length
                            l = payload[0:4]
                            # cut off length bytes
                            payload = payload[4:]

                            tmp = []
                            for i in range(4):
                                # get data according to length
                                tmp.append(payload[0:l[i]])
                                payload = payload[l[i]:]

                            self.clients[ID].hwDevice = tmp[0]
                            self.clients[ID].serialNumber = tmp[1]
                            self.clients[ID].hwInterfaceType = tmp[2]
                            self.clients[ID].numChannels = tmp[3]

                            self.dataHandler.updateClients(self.clients)

                        case Ptype.CONFIG.value:
                            print("config packet received")
                        case Ptype.STATUS.value:
                            print("status packet received")
                        case Ptype.BYE.value:
                            print("bye")
                        case _:
                            print("invalid packet format")
                except queue.Empty:
                    continue
                except ConnectionResetError:
                    break

    def createClients(self):
        """..."""
        for ID, conn in enumerate(self.parsedConfig["connections"]["spacewire"]):
            host = self.parsedConfig["connections"]["spacewire"][conn]["host"]
            port = self.parsedConfig["connections"]["spacewire"][conn]["port"]

            client = Client(host, port, ID)
            client.start()
            self.clients.append(client)

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
        time.sleep(1)
        id = input("choose ID: ")
        channel = input("choose channel: ")
        size = input("size payload: ")
        payload = int(channel).to_bytes(1, 'big') + bytearray(int(size))
        c.dataHandler.toSendQueue(int(id), Ptype.DATA.value, payload)

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
