"""Represents a channel on a device.

Brief:\n
    Represents a channel on a device.

Copyright:\n
    2022 STAR-Dundee Ltd
"""

import os
import numpy as np
from ctypes import *
from typing import Union, Tuple

from gspy_egse.gui.STAR_system import STAR_LIB, STAR_API_LIB_LOAD_ERROR_STR
from gspy_egse.gui.STAR_system.STAR_enums import STAR_CHANNEL_DIRECTION, STAR_CHANNEL_TYPE, STAR_OPERATION_RESULT, STAR_EOP_TYPE,\
                                   STAR_TRANSFER_STATUS
from gspy_egse.gui.STAR_system.STAR_exceptions import STARAPIError
from gspy_egse.gui.STAR_system.packet import Packet
from gspy_egse.gui.STAR_system.data_chunk import DataChunk
from gspy_egse.gui.STAR_system.transfer_operations import TransferOperation

# Load C API
systemType = os.name
if systemType == ("nt" or "WINDOWS_NT"):
    try:
        star_lib = windll.LoadLibrary(STAR_LIB)
    except Exception:
        star_lib = None
        print(STAR_API_LIB_LOAD_ERROR_STR)

elif systemType == "posix":
    try:
        star_lib = cdll.LoadLibrary(STAR_LIB)
    except Exception:
        star_lib = None
        print(STAR_API_LIB_LOAD_ERROR_STR)


class Channel(object):
    """Represents a channel on a device.
    
    Attributes:\n
        channelNumber (int): The number of this channel.
        owningDeviceID (int): The ID of the device the channel is part of.
        channelID (int): Optional. The ID of the channel if it is open.
    """

    def __init__(self, channelNumber, owningDeviceID, channelID=None):
        """Constructor:\n
            Initialises a Channel object.

        Args:\n
            See `STAR_system.channel.Channel` class attributes.

        Raises:\n
            STARAPIError:\n
                STAR-API library could not be loaded.\n
            TypeError:\n
                channelNumber was not an int.\n
                owningDeviceID was not an int.\n
                channelID was not None or an int.\n
            ValueError:\n
                channelNumber was negative.\n
                owningDeviceID was negative.\n
                channelID was less than 1.\n
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        if type(channelNumber) != int:
            raise TypeError("channelNumber must be int.")
        if type(owningDeviceID) != int:
            raise TypeError("owningDeviceID must be int.")
        if channelID is not None and type(channelID) != int:
            raise TypeError("channelID must be None or int.")
        if channelNumber < 0:
            raise ValueError("channelNumber cannot be negative.")
        if owningDeviceID < 0:
            raise ValueError("owningDeviceID cannot be negative.")
        if channelID is not None and channelID < 1:
            raise ValueError("channelID cannot be negative or 0.")

        self.owningDeviceID = owningDeviceID
        self.channelNumber = channelNumber
        self.channelID = channelID

    def getDirection(self) -> Union[STAR_CHANNEL_DIRECTION, None]:
        """Gets and returns the direction information of the channel if it is open.
        Returns None if the channel is closed.

        Raises:\n
            STARAPIError:\n
                The C API failed to get direction information.\n
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        # Make sure that the channel is open/valid
        if self.channelID is None:
            return None

        # Set argument types and return type of the C function
        star_lib.STAR_getChannelDirection.argtypes = [c_uint32]
        star_lib.STAR_getChannelDirection.restype = STAR_CHANNEL_DIRECTION

        # Get the channel direction
        direction = star_lib.STAR_getChannelDirection(c_uint32(self.channelID))

        return direction

    def transmitPacket(self, packet, timeout=None):
        """Transmit a single packet on a previously opened channel.
        This method is provided to simplify the process of transmitting
        packets, but is not as efficient or as flexible as using
        `STAR_system.transfer_operations.TransferOperation`. This method should not be
        used if high performance or low CPU utilisation is required.

        Args:\n
            packet (Packet): The `STAR_system.packet.Packet` object to be transmitted.
            timeout (int or None): The maximum time in milliseconds to wait for the
                packet to be transmitted, or None to wait indefinitely.

        Raises:\n
            STARAPIError:\n
                The C API failed to transmit the packet.\n
                Channel is closed.\n
            TypeError:\n
                packet was not an instance of Packet.\n
                timeout was not an int or None.\n
            ValueError:\n
                timeout was a negative number or 0.
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        if isinstance(packet, Packet) is False:
            raise TypeError("Packet must be an instance on Packet.")
        if timeout is not None and type(timeout) != int:
            raise TypeError("Timeout must be int or None.")
        if timeout is not None and timeout < 1:
            raise ValueError("Timeout must be positive and non-zero.")

        # Make sure the channel is open/valid
        if self.channelID is None:
            raise STARAPIError("Channel is closed.")

        # If no timeout has been specified, set the timeout to -1 (infinite wait)
        if timeout is None:
            timeout = -1

        data = []
        if packet.address is not None:
            for item in packet.address:
                data.append(int(item))

        for dataChunk in packet.dataChunks:
            for byte in dataChunk.data:
                data.append(int(byte))

        dataLength = len(data)

        sendBufferType = c_ubyte * dataLength
        sendBuffer = sendBufferType()

        for i in range(dataLength):
            sendBuffer[i] = data[i]

        if len(packet.dataChunks) > 0:
            eopMarker = packet.dataChunks[-1].eop
        else:
            eopMarker = STAR_EOP_TYPE.STAR_EOP_TYPE_NONE

        # Set argument types and return type of the C function
        star_lib.STAR_transmitPacket.argtypes = [c_uint32, c_void_p, c_uint32, STAR_EOP_TYPE, c_int32]
        star_lib.STAR_transmitPacket.restype = STAR_TRANSFER_STATUS

        status = star_lib.STAR_transmitPacket(c_uint32(self.channelID), byref(sendBuffer), c_uint32(dataLength),
                                              eopMarker, c_int32(timeout))

        if status != STAR_TRANSFER_STATUS.STAR_TRANSFER_STATUS_COMPLETE:
            raise STARAPIError("Error transmitting packet.")

    def receivePacket(self, bufferLength, timeout=None) -> Tuple[STAR_TRANSFER_STATUS, Union[Packet, None]]:
        """Receive a single packet on a previously opened channel into the buffer specified.

        This method is provided to simplify the process of receiving packets, but
        is not as efficient or flexible as using 
        `STAR_system.transfer_operations.TransferOperation`. This method should not be
        used if high performance of low CPU utilisation is required. Note also
        that if the received packet is longer than the buffer provided, the end
        of the packet will be dropped and the end of packet marker will indicate
        there was no end of packet marker.

        Returns a Tuple, the status of the receive operation (`STAR_system.STAR_enums.STAR_TRANSFER_STATUS`) and
        the received `STAR_system.packet.Packet` (None if the receive operation has not yet completed).

        Args:\n
            bufferLength (int): The length of buffer to create to receive packet data.
            timeout (int or None): The maximum time in milliseconds to wait for the packet
                to be received, or None to wait indefinitely.

        Raises:\n
            STARAPIError:\n
                The C API failed to transmit the packet.\n
                Channel is closed.\n
            TypeError:\n
                timeout was not an int or None.\n
            ValueError:\n
                timeout was a negative number or 0.\n
                Exception raised by Packet constructor.\n
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        # Make sure that the timeout value is positive (if supplied by the caller)
        if timeout is not None and type(timeout) != int:
            raise TypeError("Timeout must be int or None.")
        if timeout is not None and timeout < 1:
            raise ValueError("Timeout must be positive and non-zero.")

        # Make sure the channel is open/valid
        if self.channelID is None:
            raise STARAPIError("Channel is closed.")

        # If no timeout has been specified, set the timeout to -1 (infinite wait)
        if timeout is None:
            timeout = -1

        packetData = (c_uint8 * bufferLength)()
        pPacketData = pointer(packetData)

        packetLength = c_uint32(bufferLength)
        pPacketLength = pointer(packetLength)

        endOfPacketMarker = c_int32(0)
        pEndOfPacketMarker = pointer(endOfPacketMarker)

        # Set argument types and return type of the C function
        star_lib.STAR_receivePacket.argtypes = [c_uint32, c_void_p, POINTER(c_uint32), POINTER(c_int32), c_int32]
        star_lib.STAR_receivePacket.restype = STAR_TRANSFER_STATUS

        status = star_lib.STAR_receivePacket(c_uint32(self.channelID), pPacketData, pPacketLength, pEndOfPacketMarker,
                                             c_int32(timeout))

        # Check that the operation completed
        if status != STAR_TRANSFER_STATUS.STAR_TRANSFER_STATUS_COMPLETE:
            return status, None

        packetDataList = np.frombuffer(packetData, dtype=np.uint8, count=packetLength.value).tolist()

        # Create data chunk object
        try:
            dataChunk = DataChunk(packetDataList, True, STAR_EOP_TYPE(endOfPacketMarker.value))
        except (STARAPIError, TypeError, ValueError) as err:
            print("Could not create data chunk object: " + str(err))
            raise

        # Create packet object
        try:
            packet = Packet([dataChunk])
        except (TypeError, ValueError):
            raise

        return status, packet

    def getDeviceAttachedToChannel(self):
        """Returns the device attached to the channel.
        Returns a `STAR_system.device.Device` object attached to the channel or None if no device is attached.

        Raises:\n
            STARAPIError:\n
                The C API failed to transmit the packet.\n
        """

        from gspy_egse.gui.STAR_system.device import Device

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        star_lib.STAR_getLocalDeviceAttachedToChannel.argtypes = [c_uint32, c_uint32]
        star_lib.STAR_getLocalDeviceAttachedToChannel.restype = c_uint32

        deviceID = star_lib.STAR_getLocalDeviceAttachedToChannel(c_uint32(self.owningDeviceID),
                                                                 c_uint32(self.channelNumber))

        if deviceID == 0:
            return None
        else:
            return Device(deviceID)

    def isOpen(self) -> bool:
        """Gets and returns whether the channel is open.

        Raises:\n
            STARAPIError:\n
                STAR-API library could not be loaded.
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        star_lib.STAR_isChannelOpen.argtypes = [c_uint32, c_uint32]
        star_lib.STAR_isChannelOpen.restype = STAR_CHANNEL_TYPE

        # This function returns a STAR_CHANNEL_TYPE variable
        isOpen = star_lib.STAR_isChannelOpen(c_uint32(self.owningDeviceID), c_uint32(self.channelNumber))

        # Check that the returned value is not STAR_CHANNEL_TYPE_NOT_OPEN
        return isOpen != STAR_CHANNEL_TYPE.STAR_CHANNEL_TYPE_NOT_OPEN

    def getTypeOfAttached(self) -> STAR_CHANNEL_TYPE:
        """If the channel is open, returns the type of what is attached to the channel.

        Raises:\n
            STARAPIError:\n
                STAR-API library could not be loaded.\n
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        star_lib.STAR_isChannelOpen.argtypes = [c_uint32, c_uint32]
        star_lib.STAR_isChannelOpen.restype = STAR_CHANNEL_TYPE

        attached = star_lib.STAR_isChannelOpen(c_uint32(self.owningDeviceID), c_uint32(self.channelNumber))
        
        return attached

    def close(self):
        """Closes the channel.

        If a channel could not be closed, it was not open or has already been closed.

        Raises:\n
            STARAPIError:\n
                STAR-API library could not be loaded.
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        # Make sure that we don't try to close a channel that is basically not closable
        if self.channelID is None:
            return

        # Set argument types and return type of the C function
        star_lib.STAR_closeChannel.argtypes = [c_uint32]
        star_lib.STAR_closeChannel.restype = c_int32

        # We are not really interested in the returned value as the end result if the same, namely
        # That the channel is closed or had already been closed before
        star_lib.STAR_closeChannel(c_uint32(self.channelID))

        self.channelID = None

    def openBetweenLocalDevices(self, otherChannel):
        """Opens a channel between two devices.

        When the channel is not longer required it should be closed by calling
        `STAR_system.channel.Channel.close`().

        Args:\n
            otherChannel (`STAR_system.channel.Channel`): The channel on another device to attach to.

        Raises:\n
            STARAPIError:\n
                STAR-API library could not be loaded.\n
                The C API failed to open the channel.\n
            TypeError:\n
                otherChannel was not an instance of Channel.
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        if isinstance(otherChannel, Channel) is False:
            raise TypeError("otherChannel must be an instance of Channel.")

        # Set argument types and return type of the C function
        star_lib.STAR_openChannelBetweenLocalDevices.argtypes = [c_uint32, c_uint8, c_uint32, c_uint8]
        star_lib.STAR_openChannelBetweenLocalDevices.restype = c_uint32

        channelID = star_lib.STAR_openChannelBetweenLocalDevices(c_uint32(self.owningDeviceID),
                                                                 c_uint8(self.channelNumber),
                                                                 c_uint32(otherChannel.owningDeviceID),
                                                                 c_uint8(otherChannel.channelNumber))
        if channelID == 0:
            raise STARAPIError("An error occurred opening the channel.")
        else:
            self.channelID = channelID
            otherChannel.channelID = channelID

    def submitTransferOperationList(self, transferOperationList):
        """Submits a list of transfer operations.

        Once a transfer operation has completed, it can be resubmitted. This can
        be useful for receiving a number of packets in a loop, or transmitting the
        same packet repeatedly. Note that if an operation is resubmitted before it
        has completed, the original operation will be cancelled and then the new
        one submitted. This means it is not useful to submit a list containing
        multiple instances of the same operation.

        Args:\n
            transferOperationList (list): A list of `STAR_system.transfer_operations.TransferOperation` objects to submit.

        Raises:\n
            STARAPIError:\n
                STAR-API library could not be loaded.\n
                The C API failed to submit the transfer operations.\n
                The channel is closed.\n
            TypeError:\n
                transferOperationList was not a list of TransferOperations.
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        if isinstance(transferOperationList, list) is False:
            raise TypeError("transferOperationList must be a list.")
        for transferOperation in transferOperationList:
            if not isinstance(transferOperation, TransferOperation):
                raise TypeError("Every item in transferOperationList must be an instance of TransferOperation.")

        if self.channelID is None:
            raise STARAPIError("Channel is closed.")

        # Length of the transfer operation list
        count = len(transferOperationList)

        # Set up an array holding the transfer operations
        transferOperationArray = (c_void_p * count)()

        # Assign the transfer operations
        for i in range(count):
            pTransferOperation = cast(transferOperationList[i]._structAddress, c_void_p)
            transferOperationArray[i] = pTransferOperation

        # Cast to pointer (for marshalling purposes)
        pTransferOperationArray = pointer(transferOperationArray)

        # Set argument types and return type of the C function
        star_lib.STAR_submitTransferOperationList.argtypes = [c_uint32, POINTER(c_void_p * count), c_uint32]
        star_lib.STAR_submitTransferOperationList.restype = c_int32

        status = star_lib.STAR_submitTransferOperationList(self.channelID, pTransferOperationArray, count)

        if status != STAR_OPERATION_RESULT.STAR_SUCCESS.value:
            raise STARAPIError("Error submitting transfer operations.")

    def submitTransferOperation(self, transferOperation):
        """Submits a single transfer operation.

        Once a transfer operation has completed, it can be resubmitted. This
        can be useful for receiving a number of packets in a loop, or transmitting
        the same packet repeatedly. Not that if an operation is resubmitted before
        it has completed, the original operation will be cancelled and then the new one submitted.

        Args:\n
            transferOperation (STAR_system.transfer_operations.TransferOperation): The TransferOperation object to submit.

        Raises:\n
            STARAPIError:\n
                STAR-API library could not be loaded.\n
                The C API failed to submit the transfer operation.\n
                The channel is closed.\n
            TypeError:\n
                transferOperation was not an instance of TransferOperation.
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        if not isinstance(transferOperation, TransferOperation):
            raise TypeError("transferOperation must be an instance of TransferOperation.")

        if self.channelID is None:
            raise STARAPIError("Channel is closed.")

        pTransferOperation = cast(transferOperation._structAddress, c_void_p)

        # Set argument types and return type of the C function
        star_lib.STAR_submitTransferOperation.argtypes = [c_uint32, c_void_p]
        star_lib.STAR_submitTransferOperation.restype = c_int32

        status = star_lib.STAR_submitTransferOperation(c_uint32(self.channelID), pTransferOperation)

        if status != STAR_OPERATION_RESULT.STAR_SUCCESS.value:
            raise STARAPIError("Error submitting transfer operation.")

    def getApplicationAttachedToChannel(self) -> Union[int, None]:
        """Returns the ID of an application attached to the given channel.
        Returns None if the application ID was 0.

        Raises:\n
            STARAPIError:\n
                STAR-API library could not be loaded.\n
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        star_lib.STAR_getApplicationAttachedToChannel.argtypes = [c_uint32, c_uint32]
        star_lib.STAR_getApplicationAttachedToChannel.restype = c_uint32

        applicationID = star_lib.STAR_getApplicationAttachedToChannel(self.owningDeviceID, self.channelNumber)

        # Set application ID to None in case 0 was returned
        if applicationID == 0:
            applicationID = None

        return applicationID

    def openChannelToDevice(self, direction, queued=True):
        """Opens the channel to the device.

        When the channel is no longer required it should be closed by calling
        `STAR_system.channel.Channel.close`.

        Note that a channel cannot be opened in a particular direction while it is
        already open in that direction, but it is possible to open a channel to
        receive, then open it again to transmit.\n

        The queued parameter determines whether received traffic is buffered when
        it is received. As well as buffering in the device, there is also buffering
        in the device driver, and if an application is open with a channel open
        to receive data, there is also buffering in STAR-API for this channel.\n

        As these buffers become full, the device will stop issuing credit, so the
        transmitting device can no longer transmit.\n

        The queued parameter can be thought of as a way to override this
        behaviour. When it is set to False, packets will be received as normal.
        However, if the STAR-API buffer becomes full, the API will keep reading data
        from the driver. If another packet is received from the driver before the
        application reads a packet from the channel, the API will drop a packet
        from its buffer and read in the new packet.\n

        The benefit of passing False for the queued parameter is that the link
        shouldn't become blocked, as the device should always be issuing credit. The
        obvious disadvantage is that packets can be dropped, so this isn't a mode
        that is often used.\n

        In most circumstances it is recommended that True is provided for this
        argument, although note that the argument will be ignored for transmit-only
        channels.\n

        Args:\n
            direction (STAR_system.STAR_enums.STAR_CHANNEL_DIRECTION): Direction of the channel.
            queued (bool): Optional, default=True. Whether the traffic received on this channel should be buffered
                if there is not receive operation waiting to receive it.

        Raises:\n
            STARAPIError:\n
                STAR-API library could not be loaded.\n
                Failed to open the channel.\n
            TypeError:\n
                direction was not a STAR_CHANNEL_DIRECTION.\n
                queued was not a bool.\n
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        if isinstance(direction, STAR_CHANNEL_DIRECTION) is False:
            raise TypeError("direction must be STAR_CHANNEL_DIRECTION. See enum for values.")
        if isinstance(queued, bool) is False:
            raise TypeError("queued must be a bool.")

        # Set argument types and return type of the C function
        star_lib.STAR_openChannelToLocalDevice.argtypes = [c_uint32, STAR_CHANNEL_DIRECTION, c_uint8, c_int32]
        star_lib.STAR_openChannelToLocalDevice.restype = c_uint32

        channelID = star_lib.STAR_openChannelToLocalDevice(c_uint32(self.owningDeviceID), direction,
                                                           c_uint8(self.channelNumber), c_int32(queued))

        if channelID == 0:
            raise STARAPIError("Failed to open channel.")
        else:
            self.channelID = channelID
