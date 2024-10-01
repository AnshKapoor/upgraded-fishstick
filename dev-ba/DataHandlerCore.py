import queue
import threading
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

    def updateClients(self, clients):
        with self.lock:
            self.clients = clients
            # only show clients, when all are available
            for c in self.clients:
                if c.hwDevice is None:
                    print("not all hello packets have been processed...")
                    return
            self.showClients()

    def showClients(self):
        for c in self.clients:
            print(f"\nDevice: {c.hwDevice} on interface type {c.hwInterfaceType} with {c.numChannels} channels "
                  f"as ID:{c.ID} on {c.port}")

    def sendThread(self):
        # TODO sort packets to data or cmd queue
        pass

    def receiveThread(self):
        # TODO check for packets in data or cmd queue
        # TODO further distribute packets to extensions and/or DB
        pass

    def toSendQueue(self, ID, ptype, payload):
        # Function to call from i.e. extensions to send messages
        match ptype:
            case Ptype.DATA.value:
                self.clients[ID].sendQueue.put([ptype, payload])
            case _:
                self.clients[ID].cmdSendQueue.put([ptype, payload])
