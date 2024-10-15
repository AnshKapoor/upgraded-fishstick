import queue
import time

from ChannelSPW import ChannelSPW
from util import getFirstDevice

from STAR_system.STAR_exceptions import STARAPIError


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

        self.firstDevice = None

        self.cmdReceiveQueue = queue.Queue()
        self.cmdSendQueue = queue.Queue()

        self.getDeviceInfo()
        self.createChannels()

    def getDeviceInfo(self):
        self.firstDevice = getFirstDevice()

        # get available data channels of connected device
        channels = self.firstDevice.getChannels()
        if channels:
            for channel in channels:
                # Ignore the configuration channel.
                if channel.channelNumber != 0:
                    self.dataChannelList.append(channel.channelNumber)

        self.busType = self.firstDevice.getBusType()
        self.deviceName = self.firstDevice.getDeviceName()
        self.serialNumber = self.firstDevice.getSerialNumber()

    def close(self):
        for ch in self.channels:
            ch.close()

    def createChannels(self):
        for c in self.dataChannelList:
            channel = ChannelSPW(c, self.firstDevice)
            self.channels.append(channel)

    def config(self, payload):
        """sets transmission rate in MBit/s to given channel"""
        channelNumber = payload[0]
        bitRateMbitSec = payload[1]
        try:
            self.channels[channelNumber].setTransmissionRate(bitRateMbitSec)
            payloadAnswer = bytes(channelNumber)
            # 01 for success
            payloadAnswer += b'\x01'
        except STARAPIError:
            payloadAnswer = bytes(channelNumber)
            # 00 for error
            payloadAnswer += b'\x00'
        return payloadAnswer

    def resetHw(self):
        try:
            self.firstDevice.resetDevice()
            print("--Device reset successfully")
            # 01 for success
            payloadAnswer = b'\x01'
        except STARAPIError:
            # 00 for error
            payloadAnswer = b'\x00'
        return payloadAnswer

    def getStatus(self):
        self.getDeviceInfo()
        if self.firstDevice is not None:
            return self.deviceName.encode('utf-8')
        else:
            # if no device is connected return 00 as payload
            return b'\x00'

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
