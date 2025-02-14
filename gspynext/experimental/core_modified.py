import queue
import threading
import time

import path
import strictyaml

from ClientSocket_modified import Client
from DataHandlerCore import DataHandler
from enums import Ptype
from enums import Timeouts


class Core:
    """Modified version of the Core class for testing with one queue only, with i.e. fixed HELLO packet."""
    def __init__(self):
        self.parsedConfig = {}
        self.clients = []
        self.dataHandler = DataHandler(self)
        self.timeoutSek = Timeouts.TimeoutSek
        self.active = True
        self.main()

    def main(self):
        self.loadConfig()
        self.dataHandler.start()
        self.createClients()
        threading.Thread(target=self.cmdManagingThread, args=()).start()

    def cmdManagingThread(self):
        """main thread of the core for managing all incoming cmd packets"""
        while self.active:
            for cl in self.clients:
                try:
                    item = cl.cmdReceiveQueue.get(block=True, timeout=self.timeoutSek)
                    # match payloadType
                    match item[0]:
                        case Ptype.HELLO.value:
                            ID = cl.ID
                            payload = item[1]
                            # first 4 bytes are the length of following data
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
                            if item[1] == b'\x01':
                                print("configuration successfully completed")
                            elif item[1] == b'\x00':
                                print("configuration failed")

                        case Ptype.STATUS.value:
                            if item[1] == b'\x00':
                                print("no device connected")
                            else:
                                print(item[1])

                        case Ptype.RESET.value:
                            if item[1] == b'\x01':
                                print("device successfully reset")
                            elif item[1] == b'\x00':
                                print("reset failed")

                        case Ptype.BYE.value:
                            print("bye packet received, shutting down")
                            self.close()
                            break

                        case _:
                            print("invalid packet format")
                except queue.Empty:
                    continue
        print("core main gone")

    def createClients(self):
        """creates client class instances according lo loaded configuration file"""
        for ID, conn in enumerate(self.parsedConfig["connections"]["spacewire"]):
            host = self.parsedConfig["connections"]["spacewire"][conn]["host"]
            port = self.parsedConfig["connections"]["spacewire"][conn]["port"]

            client = Client(host, port, ID)
            client.start()
            self.clients.append(client)

            # workaround for test with only one que active
            self.clients[0].hwDevice = "BrickMk4"
            self.clients[0].serialNumber = "123"
            self.clients[0].hwInterfaceType = 2
            self.clients[0].numChannels = 2

            self.dataHandler.updateClients(self.clients)

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
        self.dataHandler.close()
        self.active = False


if __name__ == "__main__":
    """format: [ID, ptype, payload]"""
    c = Core()
    time.sleep(0.5)

    #while True:
    for i in range(2):
        channel = 2
        payload = channel.to_bytes(1, 'big')
        payload += str(i).encode('utf-8')
        print(payload)
        c.dataHandler.sendQueue.put([0, Ptype.DATA.value, payload])

    # time.sleep(1)
    # c.dataHandler.sendQueue.put([0, Ptype.DATA.value, b'\x01\x00\xff'])
    # time.sleep(1)
    # c.dataHandler.sendQueue.put([0, Ptype.CONFIG.value, b'\x01\x64'])
    # time.sleep(1)
    # c.dataHandler.sendQueue.put([0, Ptype.RESET.value, b'\x00'])
    # time.sleep(1)
    # c.dataHandler.sendQueue.put([0, Ptype.STATUS.value, b'\x00'])
    # time.sleep(1)
    # c.dataHandler.sendQueue.put([0, Ptype.BYE.value, b'\x00'])
