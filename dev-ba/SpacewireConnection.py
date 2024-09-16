import queue
import threading

from ChannelSPW import ChannelSPW
from util import getFirstDevice


class Spacewire:
    """..."""
    def __init__(self, configuration=None):
        self.config = configuration
        self.active = True
        self.channels = []

        self.cmdReceiveQueue = queue.Queue()
        self.cmdSendQueue = queue.Queue()

        self.firstDevice = getFirstDevice()

    def createChannels(self):
        channelOne = ChannelSPW(1)
        self.channels.append(channelOne)
        channelTwo = ChannelSPW(2)
        self.channels.append(channelTwo)

    def Hello(self):
        """
        creates the hello packet for the client providing information, in detail hw device, serial number,
        hw interface type and number if channels
        """
        # TODO let server identify connected device and get these information
        hwDevice = "SpwBrickMk4"
        serialNumber = "123-345-abc"
        hwInterfaceType = "spacewire"
        numChannels = "3"

        payload = len(str(hwDevice)).to_bytes(1, 'big')
        payload += len(str(serialNumber)).to_bytes(1, 'big')
        payload += len(str(hwInterfaceType)).to_bytes(1, 'big')
        payload += len(str(numChannels)).to_bytes(1, 'big')

        payload += hwDevice.encode("utf-8")
        payload += serialNumber.encode("utf-8")
        payload += hwInterfaceType.encode("utf-8")
        payload += numChannels.encode("utf-8")

        return payload

    def main(self):
        pass


if __name__ == "__main__":
    # self.firstDevice = getFirstDevice()
    # self.port = Port(self.firstDevice.deviceID, self.channelNumber)
    # getPortType() -> data port -> add this port as available channel, channel numbers as list
    # device.getXXX for other information hopefully (helper functions in example)
    # busType = device.getBusType()

    # channels = device.getChannels()
    # if channels:
    #    for channel in channels:
    #        print(channel.channelNumber)
    # else:
    #    print("None")

    # Ignore the configuration channel.
    # for channel in channels:
    #     if channel.channelNumber == 0:
    #         channels.remove(channel)
    pass
