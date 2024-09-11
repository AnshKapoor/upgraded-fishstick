import threading


class DataHandler(threading.Thread):
    def __init__(self, receiveQueue, sendQueue):
        super(DataHandler, self).__init__()
        self.receiveQueue = receiveQueue
        self.sendQueue = sendQueue

    def sendThread(self):
        # TODO sort packets to data or cmd queue
        pass

    def receiveThread(self):
        # TODO check for packets in data or cmd queue
        # TODO further distribute packets to extensions and/or DB
        pass

    def toSendQueue(self, ptype, destination, payload):
        # Function to call from i.e. extensions to send messages
        pass
