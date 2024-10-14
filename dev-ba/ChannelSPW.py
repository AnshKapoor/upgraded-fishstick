import queue
import threading

from enums import Ptype

from STAR_system.data_chunk import DataChunk
from STAR_system.link_port import LinkPort
from STAR_system.packet import Packet
from STAR_system.STAR_enums import STAR_EOP_TYPE, STAR_CHANNEL_DIRECTION, STAR_TRANSFER_STATUS
from STAR_system.channel import Channel
from STAR_system.transfer_operations import TransmitOperation, ReceiveOperation
from STAR_system.port import Port


class ChannelSPW:
    def __init__(self, channelNumber, firstDevice):
        self.receiveQueue = queue.Queue()
        self.sendQueue = queue.Queue()

        self.channelNumber = channelNumber
        self.active = True

        self.firstDevice = firstDevice

        self.timeoutSek = 0.000000001

        self.channel_rx = Channel(self.channelNumber, self.firstDevice.deviceID)
        self.channel_tx = Channel(self.channelNumber, self.firstDevice.deviceID)

        self.receiveThread = None
        self.sendThread = None

        # TODO close channel and Link.stopLink()
        self.port = Port(self.firstDevice.deviceID, self.channelNumber)
        self.link = LinkPort(self.firstDevice.deviceID, self.channelNumber)

        self.main()

    def main(self):
        self.channel_rx.openChannelToDevice(STAR_CHANNEL_DIRECTION.IN, queued=False)
        self.channel_tx.openChannelToDevice(STAR_CHANNEL_DIRECTION.OUT, queued=False)

        print(f"starting threads for channel {self.channelNumber}")
        self.receiveThread = threading.Thread(target=self.receiveMessage, args=())
        self.receiveThread.start()
        self.sendThread = threading.Thread(target=self.sendMessage, args=())
        self.sendThread.start()

    def setTransmissionRate(self, bitRateMbitSec):
        # set transmission speed
        self.link.setTransmitSignallingRate(bitRateMbitSec)
        print(f" \nset signaling rate to {bitRateMbitSec} Mbit / s on channel {self.channelNumber} \n")

    def sendMessage(self):
        """
        send thread for sending data over spacewire, the data was received via socket and put in the
        clientToServer queue
        """
        while self.active:
            # check for data data queue
            try:
                # TODO timeout
                item = self.sendQueue.get(block=True, timeout=self.timeoutSek)
                print(f"{item} from data in send thread SPW conn")
                self.sendQueue.task_done()
                self.send(item)
            except queue.Empty:
                pass
        print(f"send thread spw gone {self.channelNumber}")

    def send(self, item):
        """..."""
        sendItem = []
        for i in item:
            sendItem.append(i)

        dataChunk = DataChunk(sendItem, isStart=True, eop=STAR_EOP_TYPE.STAR_EOP_TYPE_EOP)
        dataPacket = Packet([dataChunk], None, STAR_EOP_TYPE.STAR_EOP_TYPE_EOP)

        sendTransferOperation = TransmitOperation([dataPacket])

        self.channel_tx.submitTransferOperation(sendTransferOperation)

        # Wait indefinitely for transfer to complete.
        # TODO timeout
        status = sendTransferOperation.waitOnTransferOperationCompletion(-1)

        # Check that packet was sent.
        if status != STAR_TRANSFER_STATUS.STAR_TRANSFER_STATUS_COMPLETE:
            print("Packet was not sent successfully.")
        print(f"{sendItem} sent on channel {self.channelNumber}")

    def receiveMessage(self):
        """
        receive thread for receiving  data over spacewire, received data is stored in the serverToClient queue
        so that it can be transferred to server via socket by the socket client
        """
        while self.active:
            message = self.receive()
            channelNumberBytes = self.channelNumber.to_bytes(1, 'big')
            if not message:
                continue
            try:
                # TODO block
                self.receiveQueue.put([Ptype.DATA.value, channelNumberBytes + bytes(message)], block=True, timeout=self.timeoutSek)
            except queue.Full:
                print("data receive queue spw full")
        print(f"receive thread spw gone {self.channelNumber}")
        self.channel_rx.close()

    def receive(self):
        """receives data over spacewire connection in packet form"""
        # Create receive transfer operation.
        receiveTransferOperation = ReceiveOperation(1, receivePackets=True)

        # Start receiving packet.
        self.channel_rx.submitTransferOperation(receiveTransferOperation)

        # TODO right timeout
        # Wait for packet to be received. timeout in mS to wait for (-1) is wait indefinitely
        status = receiveTransferOperation.waitOnTransferOperationCompletion(timeout=100)

        # Check that valid packet was received.
        if status == STAR_TRANSFER_STATUS.STAR_TRANSFER_STATUS_COMPLETE:
            # Get received packet.
            packet = receiveTransferOperation.getTransferItem(0)

            # Get packet data.
            data = packet.getPacketData()

            # Print received packet.
            print(f"{data} received on channel {self.channelNumber}")
        else:
            # print("Did not receive valid packet.")
            data = None

        return data

    def close(self):
        self.active = False
