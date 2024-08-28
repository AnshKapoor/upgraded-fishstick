import queue
import threading
from ServerSocket import Server

from util import getFirstDevice
from STAR_system.data_chunk import DataChunk
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
        self.transmitChannel = 1
        self.receiveChannel = 2
        self.host = configuration.get("host")
        self.port = configuration.get("port")
        self.channel_tx = None
        self.channel_rx = None
        self.server = None
        self.active = True
        self.firstDevice = getFirstDevice()

        self.receiveQueue = queue.Queue()
        self.sendQueue = queue.Queue()
        self.cmdReceiveQueue = queue.Queue()
        self.cmdSendQueue = queue.Queue()

        self.destinationAddress = None
        self.receivedPacketsNumber = 0

        self.server = Server(self.receiveQueue, self.sendQueue, self.cmdReceiveQueue, self.cmdSendQueue,
                             self.host, self.port).start()

        self.channel_tx = Channel(self.transmitChannel, self.firstDevice.deviceID)
        self.channel_tx.openChannelToDevice(STAR_CHANNEL_DIRECTION.OUT, queued=False)

        self.channel_rx = Channel(self.receiveChannel, self.firstDevice.deviceID)
        self.channel_rx.openChannelToDevice(STAR_CHANNEL_DIRECTION.IN, queued=False)

        self.deviceConfig = DeviceConfig(self.firstDevice.deviceID)
        self.configPort0 = ConfigPort(self.deviceConfig.deviceID, 0)
        self.port1 = Port(self.deviceConfig.deviceID, 1)
        self.link1 = LinkPort(self.firstDevice.deviceID, 1)
        self.port2 = Port(self.deviceConfig.deviceID, 2)
        self.link2 = LinkPort(self.firstDevice.deviceID, 2)

        tr = threading.Thread(target=self.receive_thread, args=(), daemon=True)
        tr.start()
        ts = threading.Thread(target=self.send_thread, args=(), daemon=True)
        ts.start()

        self.main()

    def main(self):
        """status and cmd message handler"""
        while self.active:
            try:
                item = self.cmdReceiveQueue.get(block=False)
            except queue.Empty:
                pass
            # TODO communication with core and socket here
            # TODO react to incoming cmd messages here
            # TODO sending of cmd messages here
        print("spw main thread gone")

    def send_thread(self):
        """
        send thread for sending data over spacewire, the data was received via socket and put in the
        clientToServer queue
        """
        while self.active:
            # go through data queue
            try:
                item = self.sendQueue.get(block=False)
                print(f"{item} from data in send thread SPW conn")
                self.sendQueue.task_done()
                self.send(item)
            except queue.Empty:
                pass
            # go through cmd queue
            try:
                item = self.cmdSendQueue.get(block=False)
                print(f"{item} from data in send thread SPW conn")
                self.sendQueue.task_done()
                self.send(item)
            except queue.Empty:
                pass
        print("send thread spw gone, tx channel spw closed")
        self.channel_tx.close()

    def send(self, item):
        """..."""
        sendItem = []

        for i in item:
            sendItem.append(i)

        dataChunk = DataChunk(sendItem, isStart=True, eop=STAR_EOP_TYPE.STAR_EOP_TYPE_EOP)
        dataPacket = Packet([dataChunk], self.destinationAddress, STAR_EOP_TYPE.STAR_EOP_TYPE_EOP)

        sendTransferOperation = TransmitOperation([dataPacket])

        self.channel_tx.submitTransferOperation(sendTransferOperation)

        # Wait indefinitely for transfer to complete.
        status = sendTransferOperation.waitOnTransferOperationCompletion(-1)

        # Check that packet was sent.
        if status != STAR_TRANSFER_STATUS.STAR_TRANSFER_STATUS_COMPLETE:
            print("Packet was not sent successfully.")
        print(f"{sendItem} sent on channel {self.transmitChannel}")

    def receive_thread(self):
        """
        receive thread for receiving  data over spacewire, received data is stored in the serverToClient queue
        so that it can be transferred to server via socket by the socket client
        """
        while self.active:
            message = self.receive()
            print(f"{message} in receive thread spw")
            # TODO decide where to put packet data vs cmd
            # match message[0]:
            # case data:
            # case cmd:
            # try:
            # self.cmdReceiveQueue.put(message, block=False)
            # catch queue.Full:
            # print("cmd receive queue full")
            try:
                self.receiveQueue.put(message, block=False)
            except queue.Full:
                print("data receive queue spw full")
        print("receive thread spw gone, rx channel spw closed")
        self.channel_rx.close()

    def receive(self):
        """receives data over spacewire connection in packet form"""
        # Create receive transfer operation.
        receiveTransferOperation = ReceiveOperation(1, receivePackets=True)

        # Start receiving packet.
        self.channel_rx.submitTransferOperation(receiveTransferOperation)

        # Wait for packet to be received. timeout in mS to wait for (-1) is wait indefinitely
        status = receiveTransferOperation.waitOnTransferOperationCompletion(timeout=-1)

        # Check that valid packet was received.
        if status == STAR_TRANSFER_STATUS.STAR_TRANSFER_STATUS_COMPLETE:
            # Get received packet.
            packet = receiveTransferOperation.getTransferItem(0)

            # Get packet data.
            data = packet.getPacketData()

            # Print received packet.
            print(f"{data} received on channel {self.receiveChannel}")

            self.receivedPacketsNumber += 1
        else:
            print("Did not receive valid packet.")
            data = None

        return data


if __name__ == "__main__":
    d = {"host": "127.0.0.1",
         "port": 5555}
    _ = Spacewire(d)
