from typing import *
import os
import sys
import threading
import time
import csv
from PyQt6.QtCore import QObject, pyqtSignal
import json

module_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(module_path)

try:
    from ..utils.misc import WrappedMessageHandler
    from .spacewire import ISpaceWireBridge
    from ..utils.utilities import getFirstDevice, printPacketContents
except (ValueError, ImportError):
    from utils.misc import WrappedMessageHandler
    from hardware_modules.spacewire import ISpaceWireBridge
    from utils.utilities import getFirstDevice, printPacketContents


from STAR_system.STAR_exceptions import STARAPIError
from STAR_system.data_chunk import DataChunk
from STAR_system.link_port import LinkPort
from STAR_system.packet import Packet
from STAR_system.device_config import DeviceConfig
from STAR_system.STAR_enums import STAR_EOP_TYPE, STAR_CHANNEL_DIRECTION, STAR_TRANSFER_STATUS
from STAR_system.channel import Channel
from STAR_system.transfer_operations import TransmitOperation, ReceiveOperation
from STAR_system.config_port import ConfigPort
from STAR_system.port import Port
from STAR_system.device import Device


class SpaceWireBrickMk4(ISpaceWireBridge):
    """_summary_
    The SpaceWireBrickMk4 class is used as a general SpacewireBridge which converts USB protocl to SpaceWire protocol.
    The parent class ISpaceWireBridge should be used if a new type of SpaceWireBridge should be implemented.
    A SpaceWireBridge has to implement at least the function prototypes inherited by the parent ISpaceWireBridge.
    Args:
        ISpaceWireBridge (_type_): _description_
    """

    # the tcp_ip and tcp_port are not used/applicable to this bridge, but have not been changed,
    # to reduce the changes that have to be made to some functions
    def __init__(self, tcp_ip='127.0.0.1', tcp_port=3000, message_handler=None):
        
        message_handler = WrappedMessageHandler(message_handler, "SpwBrick Mk4")
        self.message_handler = message_handler

        print(f"now we are in BrickMk4 init function")
        
        self.transmitResult = None
        self.total_duration = 0
        self.dataThroughPut = 0
        self.receivedPackage = None
        self.hasAddress = None
        self.stop_event = threading.Event()
        self.lockWriteOut = threading.Lock()
        self.lock = threading.Lock()  # used in receive_thread from hardware_modules/spacewire.py
        self.lockReceive = threading.Lock()
        self.transmitChannel = 1
        self.receiveChannel = 2
        self.tx_open = False 
        self.rx_open = False
        self.boolSendMultiplePackets = False
        self.signalEmitter = SpaceWireSignalEmitter()

        try:
            self.firstDevice = getFirstDevice()
            self.dummy = False

            if self.firstDevice is None:
                # dummy as brickmk4 device
                self.firstDevice = Device(65536)
                print("creating dummy device for software demonstration purpose")
                self.dummy = True
            print(f"{self.dummy=}")
        except (STARAPIError, TypeError, ValueError):
            print("Could not get first device")
            self.message_handler.error("No Spw Brick available")
            return

        # write dummy state to json file for further use in i.e. plugins
        dummy_dict = {"dummymode": self.dummy}
        # Serializing json
        json_object = json.dumps(dummy_dict, indent=4)
        # Writing to json
        with open("dummymode.json", "w") as outfile:
            outfile.write(json_object)
        
        if self.firstDevice is None:
            print("No devices are connected.")
            return
        
        try:
            self.deviceConfig = DeviceConfig(self.firstDevice.deviceID)
        except (TypeError, ValueError):
            print("Could not create DeviceConfig object.")
            return
        
        try:
            self.configPort0 = ConfigPort(self.deviceConfig.deviceID, 0)
            self.port1 = Port(self.deviceConfig.deviceID, 1)
            self.link1 = LinkPort(self.firstDevice.deviceID, 1)
            self.port2 = Port(self.deviceConfig.deviceID, 2)
            self.link2 = LinkPort(self.firstDevice.deviceID, 2)
            self.message_handler.success("BrickMk4 connected")
        except (TypeError, ValueError):
            print("Could not create config port object.")
            print("Could not create port object.")
            print("Could not create link port object.")
            self.message_handler.error("BrickMk4 not connected")
            return
             
        self.error_printer = print
        self.success_printer = print
        
        self.message_handler.info("Brick Mk4 initialised.")
        if not self.dummy:
            self.deviceConfig.identify()

    def get_dummy(self):
        return self.dummy

    def __del__(self):
        self.close()

    def is_open(self):
        return self.tx_open and self.rx_open

    def open(self):
        if self.dummy:
            return
        self.tx_open = True
        self.rx_open = True

        try:
            self.channel_tx = Channel(self.transmitChannel, self.firstDevice.deviceID)
        except (STARAPIError, TypeError, ValueError) as err:
            self.error_printer(err)
            self.tx_open = False
            return
        
        try:
            self.channel_rx = Channel(self.receiveChannel, self.firstDevice.deviceID)
        except (STARAPIError, TypeError, ValueError) as err:
            self.error_printer(err)
            self.rx_open = False
            return

    def close(self):
        if self.tx_open:
            try:
                self.channel_tx.close()
                self.tx_open = False
            except STARAPIError as err:
                self.error_printer(err)
                return
                
        if self.rx_open:
            try:
                self.channel_rx.close()
                self.rx_open = False
            except STARAPIError as err:
                self.error_printer(err)
                return
        return

    def send(self, packetData: list[int], address: int = None):
        if self.dummy:
            return
        chunksList = []
        self.packetsList = []
        self.transmittedPacketDataList = []
        self.transmittedLengthList = []

        # Create the channel object
        if packetData is None or not packetData:
            # packetData is either None or an empty list
            self.message_handler.warning("no input for packetData")
            
        if address is None or not address:
            self.hasAddress = False
        else:
            self.hasAddress = True
            
        self.transmittedData = packetData
        self.transmittedAddress = address
        
        if self.channel_tx is None:
            try:
                self.channel_tx = Channel(self.transmitChannel, self.firstDevice.deviceID)
                self.tx_open = True
            except (STARAPIError, TypeError, ValueError) as err:
                self.error_printer(err)
                self.tx_open = False
                return

        # Open channel to send out of and receive into.
        try:
            self.channel_tx.openChannelToDevice(STAR_CHANNEL_DIRECTION.OUT, queued=True)
        except (STARAPIError, TypeError) as err:
            self.error_printer(err)
            self.tx_open = False
            return
        
        DataChunkInstance = DataChunk
        
        if self.boolSendMultiplePackets:
            chunksList = self.send_multiple_packets(self.transmittedData, DataChunkInstance.MAX_CHUNK_SIZE)
            # Create packet(s)
            for index, packet in enumerate(chunksList):
                try:
                    if index == 0:
                        if self.hasAddress:
                            transmittedPacket = Packet([packet], self.transmittedAddress)
                        else:
                            transmittedPacket = Packet([packet])
                    else:
                        transmittedPacket = Packet([packet])
                    transmittedLength = transmittedPacket.getPacketLength()
                    transmittedPacketData = transmittedPacket.getPacketData()
                    self.packetsList.append(transmittedPacket)
                    self.transmittedLengthList.append(transmittedLength)
                    self.transmittedPacketDataList.append(transmittedPacketData)
                except (TypeError, ValueError) as err:
                    self.error_printer(err)
                    try:
                        self.channel_tx.close()
                    except STARAPIError as err:
                        self.error_printer(err)
                    return

        else:
            try:
                dataPacket = Packet(self.transmittedData, self.transmittedAddress, STAR_EOP_TYPE.STAR_EOP_TYPE_EOP)
                transmittedLength = dataPacket.getPacketLength()
                transmittedPacketData = dataPacket.getPacketData()
                self.packetsList.append(dataPacket)
                self.transmittedLengthList.append(transmittedLength)
                self.transmittedPacketDataList.append(transmittedPacketData)
            except (TypeError, ValueError) as err:
                self.error_printer(err)
                try:
                    self.channel_tx.close()
                except STARAPIError as err:
                    self.error_printer(err)
                return
        
        # Create send transfer operation.
        try:
            self.sendTransferOperation = TransmitOperation(self.packetsList)
        except (STARAPIError, TypeError) as err:
            self.error_printer(err)

            try:
                self.channel_tx.close()
            except STARAPIError as err:
                self.error_printer(err)

            return

        # Start transmitting the packet.
        self.start = time.perf_counter_ns()

        try:
            self.channel_tx.submitTransferOperation(self.sendTransferOperation)
        except (STARAPIError, TypeError) as err:
            self.error_printer(err)

            try:
                self.channel_tx.close()
            except STARAPIError as err:
                self.error_printer(err)

            return

        # Wait indefinitely for transfer to complete.
        try:
            self.status = self.sendTransferOperation.waitOnTransferOperationCompletion(-1)
        except (STARAPIError, TypeError) as err:
            self.error_printer(err)

            try:
                self.channel_tx.close()
            except STARAPIError as err:
                self.error_printer(err)

            return

        # Check that packet was sent.
        if self.status != STAR_TRANSFER_STATUS.STAR_TRANSFER_STATUS_COMPLETE:
            try:
                self.channel_tx.close()
            except STARAPIError as err:
                self.error_printer(err)
                return
        else:
            pass
            self.message_handler.success("###Packet(s) succesfully sended###")

        try:
            self.channel_tx.close()
        except STARAPIError as err:
            self.error_printer(err)
            return
        
        return
            
    def receive(self) -> Optional[bytes]:
        if self.dummy:
            return
        self.receivedPacketNumber = 0
        self.receivedPacketsTotalLenghts = 0
        self.fileCompareErrors = 0

        if self.channel_rx is None:
            # Create the channel object
            try:
                self.channel_rx = Channel(self.receiveChannel, self.firstDevice.deviceID)
                self.rx_open = True
            except (STARAPIError, TypeError, ValueError) as err:
                self.error_printer(err)
                self.rx_open = False
                return

        # Open receive channel.
        try:
            self.channel_rx.openChannelToDevice(STAR_CHANNEL_DIRECTION.IN, queued=True)
        except (STARAPIError, TypeError) as err:
            self.error_printer(err)
            self.rx_open = False
            return

        try:
            # Create receive transfer operation.
            receiveTransferOperation = ReceiveOperation(1, receivePackets=True)
        except (STARAPIError, TypeError) as err:
            self.error_printer(err)

            try:
                self.channel_rx.close()
            except STARAPIError as err:
                self.error_printer(err)
            return

        try:
            # Start receiving packet.
            self.channel_rx.submitTransferOperation(receiveTransferOperation)
        except (STARAPIError, TypeError) as err:
            self.error_printer(err)

            try:
                self.channel_rx.close()
            except STARAPIError as err:
                self.error_printer(err)
            return
        
        # helps to synchronize the retrieving of the results
        # otherwise the getTransmitResult function will retrieve the values before the receive function executes 
        # because the receive function works in a subthread, created by call_async(self.receive_thread)
        # from hardware_modules/spacewire.py and the getTransmitResult, which will be called in the main_thread,
        # executes his code before the receive function
        with self.lockReceive:
            try:
                # Wait for packet to be received.
                self.status = receiveTransferOperation.waitOnTransferOperationCompletion(-1)
            except (STARAPIError, TypeError) as err:
                self.error_printer(err)

                try:
                    self.channel_rx.close()
                except STARAPIError as err:
                    self.error_printer(err)
                return
            
            self.finish = time.perf_counter_ns()
                
            if self.status == STAR_TRANSFER_STATUS.STAR_TRANSFER_STATUS_COMPLETE:
                
                if self.boolSendMultiplePackets:
                    self.receivedPackage = self.multiplePacketReceive(receiveTransferOperation)
                else:
                    self.receivedPackage = self.singlePacketReceive(receiveTransferOperation)
            else:
                self.error_printer("Did not receive valid packet")
            
            # convert nanoseconds to seconds by dividing by 10E9
            self.total_duration = (self.finish - self.start)/1000000000.0

            self.dataThroughPutBit_s = float(self.receivedPacketsTotalLenghts*8)/float(self.total_duration)
            self.dataThroughPutMBit_s = self.dataThroughPutBit_s/1000000.0
                      
            self.message_handler.success("###packet(s) successfully received###")
            if self.fileCompareErrors != 0:
                self.transmitResult = False
            else:
                self.transmitResult = True

            self.dataThroughPutMBit_s = round(self.dataThroughPutMBit_s, 3)
            # convert seconds to microseconds
            self.total_duration = self.total_duration*1000000
            self.total_duration = round(self.total_duration, 3)

            with self.lockWriteOut:
                threading.Thread(target=self.writeOutResults, args=(self.transmitResult, self.dataThroughPutMBit_s,
                                                                    self.total_duration,
                                                                    self.receivedPacketsTotalLenghts)).start()
            
            try:
                self.channel_rx.close()
            except STARAPIError as err:
                self.error_printer(err)
                return
            
            self.stop_event.set()
            self.stop_event.clear()

            receivedPackageBytes = bytes(self.receivedPackage)
            print(f"received package: {self.receivedPackage}")
            print(f"received package bytes: {receivedPackageBytes}")
        
            self.signalEmitter.dataReceived.emit(self.transmitResult, self.dataThroughPutMBit_s, self.total_duration, self.receivedPackage)
            return receivedPackageBytes
        
    def send_multiple_packets(self, transmittedDataChunks, maxDataSize):
        if self.dummy:
            return
        chunksList = []
        
        length_trans_Data = len(transmittedDataChunks)
        for i in range(0, length_trans_Data, maxDataSize):
            chunk = transmittedDataChunks[i:i + maxDataSize]
            try:
                dataChunks = DataChunk(chunk, isStart=True, eop=STAR_EOP_TYPE.STAR_EOP_TYPE_EOP)
            except (ValueError, TypeError) as err:
                print(err)
                # Handle error if needed
                return chunksList
            
            chunksList.append(dataChunks)
       
        return chunksList

    def ft_getMultiplePacket(self, receiveTransferOperation, receivedPacketNumber):
        try:
            # Get received packet.
            packet = receiveTransferOperation.getTransferItem(0)
        except (STARAPIError, TypeError, AttributeError, ValueError) as err:
            self.error_printer(err)

            try:
                self.channel_rx.close()
            except STARAPIError as err:
                self.error_printer(err)

            return

        # Get packet data.
        if packet is None:
            self.message_handler.error("no packet available")
        else:
            receivedPackage = packet.getPacketData()
            receivedPackageLength = packet.getPacketLength()
            self.receivedPacketsTotalLenghts = self.receivedPacketsTotalLenghts + receivedPackageLength
            receivedPackageData = []
            
            if receivedPacketNumber == 0:
                if self.hasAddress:
                    receivedPackageData = receivedPackage[1:]
                else:
                    receivedPackageData = receivedPackage
            else:
                receivedPackageData = receivedPackage

            if receivedPackageLength == self.transmittedLengthList[receivedPacketNumber]:
                if receivedPackageData == self.transmittedPacketDataList[receivedPacketNumber]:
                    pass
                else:
                    self.fileCompareErrors = self.fileCompareErrors + 1
                    print("Data compare is false")
            else:
                print("Length compare is false")
                self.fileCompareErrors = self.fileCompareErrors + 1

        return receivedPackage, receivedPackageLength

    def ft_getSinglePacket(self, receiveTransferOperation):
        receivedPackageLength = 0
        receivedPackage = None
        receivedPackageAddress = []
        receivedPackageData = []
    
        try:
            # Get received packet.
            packet = receiveTransferOperation.getTransferItem(0)
            
        except (STARAPIError, TypeError, AttributeError, ValueError) as err:
            self.error_printer(err)
            try:
                self.channel_rx.close()
            except STARAPIError as err:
                self.error_printer(err)
                return

        # Get packet data.
        if packet is None:
            self.message_handler.error("no packet available")
        else:
            receivedPackage = packet.getPacketData()
            receivedPackageLength = packet.getPacketLength()
            if self.hasAddress:
                receivedPackageAddress = receivedPackage[:len(self.transmittedAddress)]
                receivedPackageData = receivedPackage[len(self.transmittedAddress):]
            else:
                receivedPackageData = receivedPackage

            if receivedPackageLength == self.transmittedLengthList[0]:
                if receivedPackageData == self.transmittedPacketDataList[0]:
                    pass
                else:
                    self.fileCompareErrors = self.fileCompareErrors + 1
                    print("Data compare is false")
            else:
                print("Length compare is false")
                self.fileCompareErrors = self.fileCompareErrors + 1

        return receivedPackageData, receivedPackageLength
    
    def reset_Spw_Device(self):
        try:
            self.firstDevice.resetDevice()
            self.port1.clearPortErrors()
            self.port2.clearPortErrors()
            self.configPort0.clearPortErrors()
            self.link1.clearPortErrors()
            self.link2.clearPortErrors()
            self.message_handler.success("Deviced Reseted")
        except STARAPIError as err:
            self.error_printer(err)
            if self.dummy:
                self.message_handler.warning("dummy device cant be retested")
                return
            try:
                self.channel_rx.close()
            except STARAPIError as err:
                self.error_printer(err)
            return
        
    def writeOutResults(self, transmitResult, dataThroughputMbit_s, totalDuration, receivedPacketsTotalLengthsBytes):
        if os.name == 'nt':
            file_path = "../output/windows_transmit_output_GSpy.csv"  # Name und Pfad der CSV-Datei
        else:
            file_path = "../output/linux_transmit_output_GSpy.csv"  # Name und Pfad der CSV-Datei

        fieldnames = ['Transmit Result', 'Data Throughput (Mbit/s)', 'Total Duration in microsec',
                      'Received Packets in Bytes']

        # Schreiben der Daten in die CSV-Datei
        with open(file_path, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            # Überprüfen, ob die Datei leer ist, um die Spaltenüberschriften zu schreiben
            file.seek(0, 2)  # Dateiposition setzen
            is_empty = file.tell() == 0

            if is_empty:  # Wenn die Datei leer ist, Spaltenüberschriften schreiben
                writer.writeheader()

            # Schreiben der Daten in die CSV-Datei
            writer.writerow({
                'Transmit Result': transmitResult,
                'Data Throughput (Mbit/s)': dataThroughputMbit_s,
                'Total Duration in microsec': totalDuration,
                'Received Packets in Bytes': receivedPacketsTotalLengthsBytes
            })

    def spw_raw_setTransmitSignallingRate(self, bitRateMbitSec, linkNum):

        if linkNum == 1:
            self.link1.setTransmitSignallingRate(bitRateMbitSec)
        elif linkNum == 2:
            self.link2.setTransmitSignallingRate(bitRateMbitSec)
        else:
            self.link1.setTransmitSignallingRate(bitRateMbitSec)
            self.link2.setTransmitSignallingRate(bitRateMbitSec)

    def spw_raw_getTransmitSignallingRate(self):
        if not self.dummy:
            transmitRateLink1 = self.link1.getTransmitSignallingRate()
            transmitRateLink2 = self.link2.getTransmitSignallingRate()
        else:
            transmitRateLink1 = 0
            transmitRateLink2 = 0

        return transmitRateLink1, transmitRateLink2

    def multiplePacketReceive(self, receiveTransferOperation):
        if self.dummy:
            return
        receivedPackage, receivedPackageLength = self.ft_getMultiplePacket(receiveTransferOperation, self.receivedPacketNumber)
        self.receivedPacketNumber += 1
  
        self.message_handler.info("received package no. : %s has size of: %s Bytes" %(self.receivedPacketNumber, receivedPackageLength))
        
        actualPacketNumber = len(self.transmittedLengthList)
        
        # Check if all sent packets are received
        while self.receivedPacketNumber < actualPacketNumber and not self.dummy:
            try:
                # Start receiving packet.
                self.channel_rx.submitTransferOperation(receiveTransferOperation)
            except (STARAPIError, TypeError) as err:
                self.error_printer(err)
                try:
                    self.channel_rx.close()
                except STARAPIError as err:
                    self.error_printer(err)
                return

            try:
                # Wait for packet to be received.
                self.status = receiveTransferOperation.waitOnTransferOperationCompletion(-1)
            except (STARAPIError, TypeError) as err:
                self.error_printer(err)

                try:
                    self.channel_rx.close()
                except STARAPIError as err:
                    self.error_printer(err)
                return
            
            self.finish = time.perf_counter_ns()

            if self.status == STAR_TRANSFER_STATUS.STAR_TRANSFER_STATUS_COMPLETE:
                receivedPackage, receivedPackageLength = self.ft_getMultiplePacket(receiveTransferOperation, self.receivedPacketNumber)
                self.receivedPacketNumber += 1
            
                self.message_handler.info("received package no. : %s has size of: %s Bytes" %(self.receivedPacketNumber, receivedPackageLength))

                return receivedPackage
            else:
                self.error_printer("Did not receive valid packet")

    def singlePacketReceive(self, receiveTransferOperation):
        receivedPackageData, receivedPackageLength = self.ft_getSinglePacket(receiveTransferOperation)
        self.receivedPacketsTotalLenghts = receivedPackageLength

        return receivedPackageData

    def setMultiplePacket(self, boolState):
        self.boolSendMultiplePackets = boolState

    def waitEvent(self):
        self.stop_event.wait()


class SpaceWireSignalEmitter(QObject):
    dataReceived = pyqtSignal(bool, float, float, list)

    def __init__(self):
        super().__init__()
