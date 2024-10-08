import queue

from ChannelSPW import ChannelSPW
from util import getFirstDevice


class Spacewire:
    """..."""
    def __init__(self, configuration=None):
        self.config = configuration
        self.active = True
        self.channels = []
        self.dataChannelList = []
        self.busType = None
        self.deviceName = None
        self.serialNumber = None

        self.cmdReceiveQueue = queue.Queue()
        self.cmdSendQueue = queue.Queue()

        self.getDeviceInfo()
        self.createChannels()

    def getDeviceInfo(self):
        firstDevice = getFirstDevice()
        # get available data channels of connected device
        channels = firstDevice.getChannels()
        if channels:
            for channel in channels:
                # Ignore the configuration channel.
                if channel.channelNumber != 0:
                    self.dataChannelList.append(channel.channelNumber)
        print(f"{self.dataChannelList=}")
        #port = Port(firstDevice.deviceID, 1)

        self.busType = firstDevice.getBusType()
        self.deviceName = firstDevice.getDeviceName()
        self.serialNumber = firstDevice.getSerialNumber()

    def close(self):
        for ch in self.channels:
            ch.close()

    def createChannels(self):
        for c in self.dataChannelList:
            channel = ChannelSPW(c)
            self.channels.append(channel)

    def Hello(self):
        """
        creates the hello packet for the client providing information, in detail hw device, serial number,
        hw interface type and number if channels
        """
        payload = len(str(self.deviceName)).to_bytes(1, 'big')
        payload += len(str(self.serialNumber)).to_bytes(1, 'big')
        payload += len(str(self.busType)).to_bytes(1, 'big')
        payload += len(str(self.dataChannelList[-1])).to_bytes(1, 'big')

        payload += self.deviceName.encode("utf-8")
        payload += self.serialNumber.encode("utf-8")
        payload += str(self.busType).encode("utf-8")
        payload += str(self.dataChannelList[-1]).encode("utf-8")

        return payload

    def main(self):
        pass


if __name__ == "__main__":
    pass
