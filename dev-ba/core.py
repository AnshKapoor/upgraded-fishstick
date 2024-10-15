import queue
import threading
import strictyaml
import path
import time

from ClientSocket import Client
from DataHandlerCore import DataHandler
from enums import Ptype
from enums import Timeouts


class Core:
    def __init__(self):
        self.parsedConfig = {}
        self.clients = []
        self.dataHandler = DataHandler()
        self.timeoutSek = Timeouts.TimeoutSek
        self.main()
        self.active = True

    def main(self):
        self.loadConfig()
        self.dataHandler.start()
        self.createClients()
        self.active = True
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
                            print("status packet received")
                            print(item[1])

                        case Ptype.RESET.value:
                            if item[1] == b'\x01':
                                print("device successfully reset")
                            elif item[1] == b'\x00':
                                print("reset failed")

                        case Ptype.BYE.value:
                            print("bye")
                            self.close()
                            self.active = False
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


if __name__ == "__main__":
    """format: [ID, ptype, payload]"""
    c = Core()

    time.sleep(1)
    c.dataHandler.sendQueue.put([0, Ptype.BYE.value, b'\x00'])

    # c.dataHandler.sendQueue.put([0, Ptype.BYE.value, b'x\00'])
    # while True:
    #     c.dataHandler.sendQueue.put([0, Ptype.DATA.value, b'\x01\x00\xff'])
    #     time.sleep(2)

    # while True:
    #     time.sleep(1)

        # id = input("choose ID: ")
        # channel = input("choose channel: ")
        # size = input("size payload: ")
        # payload = int(channel).to_bytes(1, 'big') + bytearray(int(size))
        # c.dataHandler.toSendQueue(int(id), Ptype.DATA.value, payload)

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
