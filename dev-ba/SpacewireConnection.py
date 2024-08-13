import queue
import random
import time
import threading
from STAR_system.data_chunk import DataChunk
from ClientSocket import Client

from gseos_qt.utils.utilities import getFirstDevice, printPacketContents
from STAR_system.link_port import LinkPort
from STAR_system.packet import Packet
from STAR_system.device_config import DeviceConfig
from STAR_system.STAR_enums import STAR_EOP_TYPE, STAR_CHANNEL_DIRECTION, STAR_TRANSFER_STATUS
from STAR_system.channel import Channel
from STAR_system.transfer_operations import TransmitOperation, ReceiveOperation
from STAR_system.config_port import ConfigPort
from STAR_system.port import Port


class Spacewire:
    """..."""
    def __init__(self, configuration=None):
        self.config = configuration
        self.transmitChannel = self.config.get("transmitChannel")
        self.receiveChannel = self.config.get("receiveChannel")
        self.channel_tx = None
        self.channel_rx = None
        self.client = None
        self.firstDevice = getFirstDevice()
        self.serverToClient = queue.Queue()
        self.clientToServer = queue.Queue()

        self.destinationAddress = None
        self.receivedPacketsNumber = 0

        self.createSocketClient()

        self.deviceConfig = DeviceConfig(self.firstDevice.deviceID)
        self.configPort0 = ConfigPort(self.deviceConfig.deviceID, 0)
        self.port1 = Port(self.deviceConfig.deviceID, 1)
        self.link1 = LinkPort(self.firstDevice.deviceID, 1)
        self.port2 = Port(self.deviceConfig.deviceID, 2)
        self.link2 = LinkPort(self.firstDevice.deviceID, 2)

        # self.deviceConfig.identify()

        tr = threading.Thread(target=self.receive_thread, args=(), daemon=True)
        tr.start()
        ts = threading.Thread(target=self.send_thread, args=(), daemon=True)
        ts.start()

    def createSocketClient(self, host='127.0.0.1', port=5555):
        """
        create client socket for given host and port
        :param str host: IPV4 address of host system
        :param int port: port of host system
        """
        self.client = Client(self.serverToClient, self.clientToServer, host, port)
        self.client.start()
        threading.Thread(target=self.singleSend).start()
        # threading.Thread(target=self.testing).start()

    def testing(self):
        for i in range(3):
            data = [random.randrange(100) for j in range(10)]
            self.serverToClient.put(data)
            time.sleep(2)

    def singleSend(self):
        data = [random.randrange(10) for j in range(3)]
        self.serverToClient.put(data)

    def send_thread(self):
        """
        send thread for sending data over spacewire, the data was received via socket and put in the
        serverToClient queue
        """
        while True:
            item = self.serverToClient.get(block=True, timeout=None)
            print(f"{item} in send thread SPW conn")
            self.serverToClient.task_done()
            self.send(item)

    def send(self, item):
        """..."""
        self.channel_tx = Channel(self.transmitChannel, self.firstDevice.deviceID)
        self.channel_tx.openChannelToDevice(STAR_CHANNEL_DIRECTION.OUT, queued=False)

        if not isinstance(item, list):
            item = [item]
        dataChunk = DataChunk(item, isStart=True, eop=STAR_EOP_TYPE.STAR_EOP_TYPE_EOP)
        dataPacket = Packet([dataChunk], self.destinationAddress, STAR_EOP_TYPE.STAR_EOP_TYPE_EOP)

        sendTransferOperation = TransmitOperation([dataPacket])

        self.channel_tx.submitTransferOperation(sendTransferOperation)

        # Wait indefinitely for transfer to complete.
        status = sendTransferOperation.waitOnTransferOperationCompletion(-1)

        # Check that packet was sent.
        if status != STAR_TRANSFER_STATUS.STAR_TRANSFER_STATUS_COMPLETE:
            print("Packet was not sent successfully.")

        self.channel_tx.close()
        print(f"{item} sent on channel {self.transmitChannel}")

    def receive_thread(self):
        """
        receive thread for receiving  data over spacewire, received data is stored in the clientToServer queue
        so that it can be transferred to server via socket by the socket client
        """
        while True:
            message = self.receive()
            print(f"{message} in spw receive thread spw")
            self.clientToServer.put(message, block=False, timeout=None)

    def receive(self):
        """receives data over spacewire connection in packet form"""
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
