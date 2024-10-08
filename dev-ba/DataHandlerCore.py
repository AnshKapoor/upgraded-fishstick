import queue
import threading
import time
from datetime import datetime
from enums import Ptype


class DataHandler(threading.Thread):
    def __init__(self):
        super(DataHandler, self).__init__()
        self.clients = []
        self.clientQueue = queue.Queue()
        self.timeoutSek = 0.000000001
        self.lock = threading.Lock()

    def run(self):
        # TODO start threads for queues
        pass

    def createTimestamp(self):
        baTime = bytearray(int(time.time_ns()).to_bytes(8, 'big'))
        print(baTime)
        baInt = int.from_bytes(baTime)
        print(baInt)
        dt = datetime.fromtimestamp(baInt / 1000000000)
        print(dt)

    def updateClients(self, clients):
        """
        Updates it´s own list of clients with a new one provided by the core class, called after processing of a newly
        received hello packet
        :param clients: list of client class objects created according to loaded config file
        """
        with self.lock:
            self.clients = clients
            # only show clients, when all are available
            for c in self.clients:
                if c.hwDevice is None:
                    print("not all hello packets have been processed...")
                    return
            self.showClients()

    def showClients(self):
        """prints out all connected server with information about them"""
        for c in self.clients:
            print(f"\nDevice: {c.hwDevice} on interface type {c.hwInterfaceType} with {c.numChannels} channels "
                  f"as ID:{c.ID} on {c.port}")

    def toSendQueue(self, ID, ptype, payload):
        # Function to call from i.e. extensions to send messages
        match ptype:
            case Ptype.DATA.value:
                self.clients[ID].sendQueue.put([ptype, payload])
            case _:
                self.clients[ID].cmdSendQueue.put([ptype, payload])
