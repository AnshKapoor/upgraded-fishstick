import threading


class DataHandler(threading.Thread):
    def __init__(self, receiveQueue, sendQueue):
        super(DataHandler, self).__init__()
        self.receiveQueue = receiveQueue
        self.sendQueue = sendQueue
