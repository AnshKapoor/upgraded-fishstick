import threading


class DataHandler(threading.Thread):
    def __init__(self):
        super(DataHandler, self).__init__()
        self.clients = []

    def run(self):
        # TODO start threads for queues
        pass

    def updateClients(self, client):
        self.clients.append(client)
        self.showClients()

    def showClients(self):
        for c in self.clients:
            print(f"\nDevice: {c.hwDevice} on interface type {c.hwInterfaceType} with {c.numChannels} channels "
                  f"as ID:{c.ID}")

    def sendThread(self):
        # TODO sort packets to data or cmd queue
        pass

    def receiveThread(self):
        # TODO check for packets in data or cmd queue
        # TODO further distribute packets to extensions and/or DB
        pass

    def toSendQueue(self, ID, ptype, payload):
        # Function to call from i.e. extensions to send messages
        self.clients[ID].sendQueue.put([ptype, payload])
