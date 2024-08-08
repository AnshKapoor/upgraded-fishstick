import queue
import random
import time
import threading

from gseos_qt.utils.utilities import getFirstDevice, printPacketContents
from STAR_system.link_port import LinkPort
from STAR_system.packet import Packet
from STAR_system.device_config import DeviceConfig
from STAR_system.STAR_enums import STAR_EOP_TYPE, STAR_CHANNEL_DIRECTION, STAR_TRANSFER_STATUS
from STAR_system.channel import Channel
from STAR_system.transfer_operations import TransmitOperation, ReceiveOperation
from STAR_system.config_port import ConfigPort
from STAR_system.port import Port


class Loopback:
    def __init__(self, sendQueue, receiveQueue, transmitChannel, receiveChannel):
        self.transmitChannel = transmitChannel
        self.receiveChannel = receiveChannel
        self.channel_tx = None
        self.channel_rx = None
        self.firstDevice = getFirstDevice()
        self.sendQueue = sendQueue
        self.receiveQueue = receiveQueue

        self.destinationAddress = None
        self.receivedPacketsNumber = 0
        self.doReceive = True

        self.deviceConfig = DeviceConfig(self.firstDevice.deviceID)
        self.configPort0 = ConfigPort(self.deviceConfig.deviceID, 0)
        self.port1 = Port(self.deviceConfig.deviceID, 1)
        self.link1 = LinkPort(self.firstDevice.deviceID, 1)
        self.port2 = Port(self.deviceConfig.deviceID, 2)
        self.link2 = LinkPort(self.firstDevice.deviceID, 2)

        # self.deviceConfig.identify()

        threading.Thread(target=self.receive_thread, args=()).start()
        threading.Thread(target=self.send_thread, args=()).start()

    def send_thread(self):
        while True:
            item = self.sendQueue.get(block=True, timeout=None)
            self.sendQueue.task_done()
            self.send(item)

    def send(self, item, address=None):
        print(f"{item} item sent on channel {self.transmitChannel}")
        # Create the channel object
        self.channel_tx = Channel(self.transmitChannel, self.firstDevice.deviceID)

        # Open channel to send out of and receive into.
        self.channel_tx.openChannelToDevice(STAR_CHANNEL_DIRECTION.OUT, queued=False)

        # self.destinationAddress = address
        dataPacket = Packet(item, self.destinationAddress, STAR_EOP_TYPE.STAR_EOP_TYPE_EOP)

        # Create send transfer operation.
        sendTransferOperation = TransmitOperation([dataPacket])

        # Start transmitting the packet.
        self.channel_tx.submitTransferOperation(sendTransferOperation)

        # Wait indefinitely for transfer to complete.
        status = sendTransferOperation.waitOnTransferOperationCompletion(-1)

        # Check that packet was sent.
        if status != STAR_TRANSFER_STATUS.STAR_TRANSFER_STATUS_COMPLETE:
            print("Packet was not sent successfully.")

        self.channel_tx.close()

    def receive_thread(self):
        while True:
            message = self.receive()
            # print(f"received {message}")
            self.receiveQueue.put(message, block=False, timeout=None)

    def receive(self):
        # Create the channel object
        self.channel_rx = Channel(self.receiveChannel, self.firstDevice.deviceID)

        # Open receive channel.
        self.channel_rx.openChannelToDevice(STAR_CHANNEL_DIRECTION.IN, queued=False)

        # Create receive transfer operation.
        receiveTransferOperation = ReceiveOperation(1, receivePackets=True)

        # Start receiving packet.
        self.channel_rx.submitTransferOperation(receiveTransferOperation)

        # Wait for packet to be received.
        status = receiveTransferOperation.waitOnTransferOperationCompletion(-1)

        # Check that valid packet was received.
        if status == STAR_TRANSFER_STATUS.STAR_TRANSFER_STATUS_COMPLETE:
            # Get received packet.
            packet = receiveTransferOperation.getTransferItem(0)

            # Get packet data.
            data = packet.getPacketData()

            # Print received packet.
            # printPacketContents(data)
            print(f"{data} received on channel {self.receiveChannel}")

            self.receivedPacketsNumber += 1
        else:
            print("Did not receive valid packet.")
            data = None

        self.channel_rx.close()
        return data


def test():
    sendQueue = queue.Queue()
    sendQueue1 = queue.Queue()
    receiveQueue = queue.Queue()
    receiveQueue1 = queue.Queue()

    Loopback(sendQueue, receiveQueue, 1, 2)
    Loopback(sendQueue1, receiveQueue1, 2, 1)

    while True:
        payload = [random.randrange(0, 10) for i in range(10)]
        sendQueue.put(payload)

        time.sleep(1)

        payload = [random.randrange(0, 10) for i in range(10)]
        sendQueue1.put(payload)

        time.sleep(1)
        receiveQueue.get()
        receiveQueue1.get()


def test1():
    sendQueue = queue.Queue()
    receiveQueue = queue.Queue()
    Loopback(sendQueue, receiveQueue, 1, 2)
    while True:
        payload = [random.randrange(0, 10) for i in range(10)]
        sendQueue.put(payload)


class DataHandler:
    def __init__(self):
        pass

    def readReceivedDate(self):
        pass

    def sendData(self):
        pass


if __name__ == "__main__":
    test()
