import queue
import threading
import strictyaml
import path
import time

from .ClientSocket import Client
from .DataHandlerCore import DataHandler
from gspynext.common.enums import Ptype
from gspynext.common.enums import Timeouts


class Core:
    """
    Core class for managing all Clients, Datahandler and the whole creation and startup procedure.
    All actions are based on the config.yaml file in the same directory.
    """
    def __init__(self):
        self.parsedConfig = {}
        self.clients = []
        self.dataHandler = DataHandler(self)
        self.timeoutSek = Timeouts.TimeoutSek
        self.main()
        self.active = True

    def main(self):
        """startup procedure for the core class"""
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
                                print("configuration successfully completed\n")
                            elif item[1] == b'\x00':
                                print("configuration failed\n")

                        case Ptype.STATUS.value:
                            if item[1] == b'\x00':
                                print("no device connected\n")
                            else:
                                print(f"{item[1]}\n")

                        case Ptype.RESET.value:
                            if item[1] == b'\x01':
                                print("device successfully reset\n")
                            elif item[1] == b'\x00':
                                print("reset failed\n")

                        case Ptype.BYE.value:
                            print("bye packet received, shutting down\n")
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
        """shuts down the core itself, its Datahandler and Clients"""
        for cl in self.clients:
            cl.close()
        self.dataHandler.close()
        self.active = False


# if __name__ == "__main__":
#     """format: [ID, ptype, payload]"""
#     c = Core()

#     time.sleep(1)

#     # for i in range(10):
#     #     payload = b'\x01'
#     #     payload += str(i).encode("utf-8")
#     #     #payload += bytes(2000)
#     #     c.dataHandler.sendQueue.put([0, Ptype.DATA.value, payload])

#     # test of all available packet types
#     time.sleep(2)
#     c.dataHandler.sendQueue.put([0, Ptype.DATA.value, b'\x01\x00\xff'])
#     print("sent \\x01\\x00\\xff, with 1 being the send channel")
#     time.sleep(2)
#     c.dataHandler.sendQueue.put([0, Ptype.CONFIG.value, b'\x01\x64'])
#     time.sleep(2)
#     c.dataHandler.sendQueue.put([0, Ptype.RESET.value, b'\x00'])
#     time.sleep(2)
#     c.dataHandler.sendQueue.put([0, Ptype.STATUS.value, b'\x00'])
#     time.sleep(2)
#     c.dataHandler.sendQueue.put([0, Ptype.BYE.value, b'\x00'])
