import queue
import threading
import time
from enums import Ptype
from enums import Timeouts


class DataHandler(threading.Thread):
    def __init__(self, core):
        super(DataHandler, self).__init__()
        self.clients = []
        self.clientQueue = queue.Queue()
        self.timeoutSek = Timeouts.TimeoutSek
        self.lock = threading.Lock()
        self.active = True
        self.core = core

        self.receiveThread = None
        self.sendThread = None

        self.sendQueue = queue.Queue()
        self.receiveQueue = queue.Queue()

    def run(self):
        self.receiveThread = threading.Thread(target=self.receiveMessage, args=()).start()
        self.sendThread = threading.Thread(target=self.sendMessage, args=()).start()
        threading.Thread(target=self.dropPackets, args=()).start()

    def close(self):
        self.active = False

    def receiveMessage(self):
        """..."""
        while self.active:
            for cl in self.clients:
                try:
                    payload = cl.receiveQueue.get(block=True, timeout=self.timeoutSek)
                    cl.receiveQueue.task_done()
                    timestamp = self.createTimestamp()
                    self.receiveQueue.put([cl.ID, Ptype.DATA.value, timestamp, payload])
                except queue.Empty:
                    pass
        print("dh receive gone")

    def sendMessage(self):
        """
        Forwards a message to be sent from its sendQueue to the sendQueue of the corresponding client, messages need to
        be provided as follows: [Client ID(int), Ptype(enum), payload(bytes)]
        """
        while self.active:
            try:
                item = self.sendQueue.get(block=True, timeout=self.timeoutSek)
                self.sendQueue.task_done()
                ID = item[0]
                ptype = item[1]
                payload = item[2]
                match ptype:
                    case Ptype.DATA.value:
                        self.clients[ID].sendQueue.put([ptype, payload])
                    # special case when shutting down the server, this way the client is also shut down
                    case Ptype.BYE.value:
                        print("shutting down...")
                        self.clients[ID].cmdSendQueue.put([ptype, payload])
                        time.sleep(0.1)
                        self.core.close()
                    case _:
                        self.clients[ID].cmdSendQueue.put([ptype, payload])
            except queue.Empty:
                pass
        print("dh send gone")

    def dropPackets(self):
        """for now just drops all received packets, acts like an alibi extension"""
        while self.active:
            try:
                item = self.receiveQueue.get(block=True, timeout=self.timeoutSek)
                self.receiveQueue.task_done()
                print(f"packet received {item}")
            except queue.Empty:
                pass
        print("dh drop gone")

    def createTimestamp(self):
        """
        creates a timestamp of the current time as a bytearray to be saved with the packets to keep them in order.
        It can be made human-readable with:
        baInt = int.from_bytes(baTime)
        dt = datetime.fromtimestamp(baInt / 1000000000)
        """
        return bytearray(int(time.time_ns()).to_bytes(8, 'big'))

    def updateClients(self, clients):
        """
        Updates it´s own list of clients with a new one provided by the core class, called after processing of a newly
        received hello packet
        :param clients: list of client class objects created according to loaded config file
        """
        with self.lock:
            self.clients = clients
            self.showClients()

    def showClients(self):
        """prints out all connected server with information about them to the user"""
        for c in self.clients:
            print(f"\nDevice: {c.hwDevice} on interface type {c.hwInterfaceType} with {c.numChannels} channels "
                  f"as ID:{c.ID} on {c.port}")
