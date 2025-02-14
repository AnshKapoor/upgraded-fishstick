"""Contains classes to represent different transfer operation events.

Brief:\n
    Classes to represent a transfer operation event.

Copyright:\n
    2022 STAR-Dundee Ltd
"""

import os
import types
from ctypes import *
from typing import Union

import numpy as np

from STAR_system import STAR_LIB, STAR_API_LIB_LOAD_ERROR_STR
from STAR_system.STAR_enums import STAR_EOP_TYPE, STAR_TIMESTAMP_TYPE, STAR_ERROR_IN_DATA_TYPE, STAR_TIMESTAMP_DIRECTION,\
    STAR_OPERATION_RESULT
from STAR_system.error_in_data import ErrorInData
from STAR_system.data_chunk import DataChunk
from STAR_system.link_speed_event import LinkSpeedEvent
from STAR_system.link_state_event import LinkStateEvent
from STAR_system.packet import Packet
from STAR_system.time_code import TimeCode
from STAR_system.timestamp_event import TimestampEvent
from STAR_system.STAR_exceptions import STARAPIError
from STAR_system.STAR_structures import STAR_TIMESTAMP_EVENT, STAR_SPACEWIRE_ADDRESS, STAR_DATA_CHUNK, STAR_SPACEWIRE_PACKET,\
                                        STAR_STREAM_ITEM, STAR_TIMECODE, STAR_LINK_STATE_EVENT, STAR_LINK_SPEED_EVENT,\
                                        STAR_ERROR_IN_DATA_INJECT, STAR_BROADCAST_MESSAGE
from STAR_system.STAR_structure_classes import StarBroadcastMessage
from STAR_system.STAR_enums import STAR_TRANSFER_STATUS, STAR_STREAM_ITEM_TYPE
from STAR_system.transfer_completion_listener import TransferCompletionListener

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


class TransferOperation(object):
    """Represents a transfer operation.

    Attributes:\n
        _structAddress: (ctypes.c_void_p / int) The address where the internal C
            transfer operation is stored. This attribute is not intended to be used or modified by the user.
        _transferCompletionListener: (types.FunctionType / types.MethodType) Callback function that will
            be called when the transfer operation completion occurs.
    """

    def __init__(self, allocatedStructAddress=None):
        self._deleteTransferOp = allocatedStructAddress is None
        self._structAddress = allocatedStructAddress
        self._transferCompletionListener = None

    """Constructor:\n
        Initialises a `STAR_system.transfer_operations.TransferOperation` object.\n

        Args:\n
            See `STAR_system.transfer_operations.TransferOperation` class attributes.
    """

    def __del__(self):

        # In case this transfer operation is invalid, don't free it
        if self._structAddress is None or self._deleteTransferOp is False:
            return

        try:
            pTransferOperation = cast(self._structAddress, c_void_p)

            # Set argument types and return type of the C function
            star_lib.STAR_disposeTransferOperation.argtypes = [c_void_p]
            star_lib.STAR_disposeTransferOperation.restype = c_int32

            success = star_lib.STAR_disposeTransferOperation(pTransferOperation)

            # In case the dispose operation was a success, set the internal struct field to None
            if success == STAR_OPERATION_RESULT.STAR_SUCCESS.value:
                self._structAddress = None

        except AttributeError:
            print("Could not dispose of transfer operation.")

    def registerTransferCompletionListener(self, callback, contextObject=None):
        """Registers a call-back function that will be called when the operation completes.

        Each call-back is made using a separate thread, to ensure that STAR-System
        internal processing is not blocked by long-running callbacks. Due to
        operation system scheduling it is not possible to guarantee that call-backs
        will execute in the same order they are triggered.\n

        Args:\n
            callback (function): The call-back function.
            contextObject (user-defined class instance): Optional context information that will be passed as
                an argument to the call-back function when it is called. Default value is None.

        Raises:\n
            STARAPIError:\n
                The STAR-API library could not be loaded.\n
                Failed to register callback.\n
                Failed to create TransferCompletionListener.\n
                The transfer operation is no longer valid.\n
            TypeError:\n
                callback is not a function.\n
                Errors during creation of TransferCompletionListener.\n
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        if isinstance(callback, types.FunctionType) is False and isinstance(callback, types.MethodType) is False:
            raise TypeError("callback must be a function/method.")

        # In case this transfer operation is invalid
        if self._structAddress is None:
            raise STARAPIError("Transfer operation is no longer valid.")

        try:
            transferCompletionListener = TransferCompletionListener(callback, self, contextObject)
        except (STARAPIError, TypeError):
            raise

        # Save the transfer completion listener
        self._transferCompletionListener = transferCompletionListener

    def unregisterTransferCompletionListener(self):
        """Unregisters a call-back function that will be called when the operation completes.

        Raises:\n
            STARAPIError:\n
                The call-back was not successfully unregistered.
        """

        # In case there is no registered transfer completion listener, there is nothing to do
        if self._transferCompletionListener is not None:

            try:
                self._transferCompletionListener.unregister()
            except STARAPIError:
                raise

            self._transferCompletionListener = None

    def cancelTransferOperation(self) -> bool:
        """Cancels the transfer operation.

        Returns True if the operation was cancelled successfully, False otherwise.

        Raises:\n
            STARAPIError:\n
                The STAR-API library could not be loaded.\n
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        # In case this transfer operation is invalid
        if self._structAddress is None:
            return False

        pTransferOperation = cast(self._structAddress, c_void_p)

        # Set argument types and return type of the C function
        star_lib.STAR_cancelTransferOperation.argtypes = [c_void_p]
        star_lib.STAR_cancelTransferOperation.restype = c_int32

        status = star_lib.STAR_cancelTransferOperation(pTransferOperation)

        return bool(status)

    def cancelTransferOperationWaits(self):
        """Cancels any waits in progress on the transfer operation.

        This does not cancel the transfer operation, it simply cancels any
        calls to `STAR_system.transfer_operations.TransferOperation.waitOnTransferOperationCompletion`.

        Raises:\n
            STARAPIError:\n
                The STAR-API library could not be loaded.\n
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        # In case this transfer operation is invalid
        if self._structAddress is None:
            return

        pTransferOperation = cast(self._structAddress, c_void_p)

        # Set argument types and return type of the C function
        star_lib.STAR_cancelTransferOperationWaits.argtypes = [c_void_p]
        star_lib.STAR_cancelTransferOperationWaits.restype = None

        star_lib.STAR_cancelTransferOperationWaits(pTransferOperation)

    def getTransferOperationStatus(self) -> STAR_TRANSFER_STATUS:
        """Gets and returns the status of a transfer operation.

        Raises:\n
            STARAPIError:\n
                The STAR-API library could not be loaded.
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        # In case this transfer operation is invalid
        if self._structAddress is None:
            return STAR_TRANSFER_STATUS.STAR_TRANSFER_STATUS_ERROR

        pTransferOperation = cast(self._structAddress, c_void_p)

        # Set argument types and return type of the C function
        star_lib.STAR_getTransferOperationStatus.argtypes = [c_void_p]
        star_lib.STAR_getTransferOperationStatus.restype = STAR_TRANSFER_STATUS

        status = star_lib.STAR_getTransferOperationStatus(pTransferOperation)

        return status

    def waitOnTransferOperationCompletion(self, timeout) -> STAR_TRANSFER_STATUS:
        """Blocks until the transfer operation has completed, or the timeout period expired.

        The operation will continue to transmit or receive once this function
        returns if it has not yet completed. The operation will only be stopped
        if it completes, there is an error, or it is cancelled by calling
        `STAR_system.transfer_operations.TransferOperation.cancelTransferOperationWaits`. If the operation this
        method is called on has been submitted but has not yet completed when the
        function returns, the return value will be "started" as the operation has 
        started by not yet completed. This function can be called multiple times 
        for the same operation to wait until that operation completes.

        Returns the status of the transfer operation.

        Args:\n
            timeout (int): Max time in milliseconds to wait, or -1 to wait indefinitely.

        Raises:\n
            STARAPIError:\n
                The STAR-API library could not be loaded.\n
            TypeError:\n
                timeout is not int.
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        if type(timeout) != int:
            raise TypeError("timeout needs to be an int.")

        # In case this transfer operation is invalid
        if self._structAddress is None:
            return STAR_TRANSFER_STATUS.STAR_TRANSFER_STATUS_ERROR

        pTransferOperation = cast(self._structAddress, c_void_p)

        # Set argument types and return type of the C function
        star_lib.STAR_waitOnTransferOperationCompletion.argtypes = [c_void_p, c_int32]
        star_lib.STAR_waitOnTransferOperationCompletion.restype = STAR_TRANSFER_STATUS

        status = star_lib.STAR_waitOnTransferOperationCompletion(pTransferOperation, timeout)

        return status


class ReceiveOperation(TransferOperation):
    """Represents a receive operation.

    Attributes:
        _structAddress (ctypes.c_void_p): The address where the internal C 
            transfer operation is stored. This attribute is not intended to be
            used or modified by the user.
        _transferCompletionListener (types.FunctionType / types.MethodType): Callback function that will
            be called when the transfer operation completion occurs.
    """

    def __init__(self, itemCount=1, receivePackets=False, receiveDataChunks=False, receiveTimecodes=False,
                 receiveFCTS=False, receiveNull=False, receiveLinkStateEvents=False, receiveLinkSpeedEvents=False,
                 receiveTimestampEvents=False, receiveBroadcastMessages=False, allocatedStructAddress=None):
        """Constructor:\n
            Creates a receive operation that can then be submitted.

            Args:\n
                itemCount (int): The number of items to create the receive operation for. Defaults to 1.
                receivePackets (bool): If set to True, the transfer operation will receive Packets. Defaults to False.
                receiveDataChunks (bool): If set to True, the transfer operation will receive data chunks. Defaults to False.
                receiveTimecodes (bool): If set to True, the transfer operation will receive time-codes. Defaults to False.
                receiveFCTS (bool): If set to True, the transfer operation will receive FCTs. Defaults to False.
                receiveNull (bool): If set to True, the transfer operation will receive NULLs. Defaults to False.
                receiveLinkStateEvents (bool): If set to True, the transfer operation will receive link state events. Defaults to False.
                receiveLinkSpeedEvents (bool): If set to True, the transfer operation will receive link speed events. Defaults to False.
                receiveTimestampEvents (bool): If set to True, the transfer operation will receive link speed events. Defaults to False.
                receiveBroadcastMessages (bool): If set to True, the transfer operation will receive broadcast messages. Defaults to False.
                allocatedStructAddress (int): The struct address of a previously allocated receive operation. Note: When
                this input argument is not None, a new ReceiveOperation object will NOT be created. Defaults to None.

        Raises:\n
            STARAPIError:\n
                The STAR-API library could not be loaded.\n
            TypeError:\n
                itemCount was not int.\n
                receivePackets was not a bool.\n
                receiveDataChunks was not a bool.\n
                receiveTimecodes was not a bool.\n
                receiveFCTS was not a bool.\n
                receiveNull was not a bool.\n
                receiveLinkStateEvents was not a bool.\n
                receiveLinkSpeedEvents was not a bool.\n
                receiveTimestampEvents was not a bool.\n
                receiveBroadcastMessages was not a bool.\n
                allocatedStructAddress was not an int.\n
        """

        if allocatedStructAddress is not None and type(allocatedStructAddress) != int:
            raise TypeError(f"allocatedStructAddress must be int. Got {type(allocatedStructAddress)}.")

        super().__init__(allocatedStructAddress)

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        if type(itemCount) != int:
            raise TypeError(f"itemCount must be int. Got {type(itemCount)}.")

        if type(receivePackets) != bool:
            raise TypeError(f"receivePackets must be a bool. Got {type(receivePackets)}.")

        if type(receiveDataChunks) != bool:
            raise TypeError(f"receiveDataChunks must be a bool. Got {type(receiveDataChunks)}.")

        if type(receiveTimecodes) != bool:
            raise TypeError(f"receiveTimecodes must be a bool. Got {type(receiveTimecodes)}.")

        if type(receiveFCTS) != bool:
            raise TypeError(f"receiveFCTS must be a bool. Got {type(receiveFCTS)}.")

        if type(receiveNull) != bool:
            raise TypeError(f"receiveNull must be a bool. Got {type(receiveNull)}.")

        if type(receiveLinkStateEvents) != bool:
            raise TypeError(f"receiveLinkStateEvents must be a bool. Got {type(receiveLinkStateEvents)}.")

        if type(receiveLinkSpeedEvents) != bool:
            raise TypeError(f"receiveLinkSpeedEvents must be a bool. Got {type(receiveLinkSpeedEvents)}.")

        if type(receiveTimestampEvents) != bool:
            raise TypeError(f"receiveTimestampEvents must be a bool. Got {type(receiveTimestampEvents)}.")

        if type(receiveBroadcastMessages) != bool:
            raise TypeError(f"receiveBroadcastMessages must be a bool. Got {type(receiveBroadcastMessages)}.")

        # This is the case when the transfer operation is to be created (new)
        if allocatedStructAddress is None:

            receiveMask = ""
            if receiveBroadcastMessages:
                receiveMask += "1"
            else:
                receiveMask += "0"
            if receiveTimestampEvents:
                receiveMask += "1"
            else:
                receiveMask += "0"
            if receiveLinkSpeedEvents:
                receiveMask += "1"
            else:
                receiveMask += "0"
            if receiveLinkStateEvents:
                receiveMask += "1"
            else:
                receiveMask += "0"
            if receiveNull:
                receiveMask += "1"
            else:
                receiveMask += "0"
            if receiveFCTS:
                receiveMask += "1"
            else:
                receiveMask += "0"
            if receiveTimecodes:
                receiveMask += "1"
            else:
                receiveMask += "0"
            if receiveDataChunks:
                receiveMask += "1"
            else:
                receiveMask += "0"
            if receivePackets:
                receiveMask += "1"
            else:
                receiveMask += "0"

            receiveMaskInt = int(receiveMask, 2)

            # Set argument types and return type of the C function
            star_lib.STAR_createRxOperation.argtypes = [c_int32, c_int32]
            star_lib.STAR_createRxOperation.restype = c_void_p

            self._structAddress = star_lib.STAR_createRxOperation(itemCount, receiveMaskInt)

    @staticmethod
    def _createDataChunkFromStruct(dataChunkStruct):
        """Converts a `STAR_system.STAR_structures.STAR_DATA_CHUNK` struct into a `STAR_system.data_chunk.DataChunk` object.

        Args:
            dataChunkStruct (STAR_system.STAR_structures.STAR_DATA_CHUNK): The data chunk structure.

        Returns:
            dataChunkObj (STAR_system.data_chunk.DataChunk): Object storing the same data as the `STAR_system.STAR_structures.STAR_DATA_CHUNK` struct.

        Raises:
            STARAPIError: Errors in DataChunk class.
            TypeError: dataChunkStruct was not a STAR_DATA_CHUNK.
        """

        if isinstance(dataChunkStruct, STAR_DATA_CHUNK) is False:
            raise TypeError("dataChunkStruct must be a STAR_DATA_CHUNK.")

        pDataBuffer = cast(dataChunkStruct.data, POINTER(c_ubyte))

        dataBytes = np.ctypeslib.as_array(pDataBuffer, (dataChunkStruct.dataLength,)).tolist()

        try:
            dataChunkObj = DataChunk(dataBytes, bool(dataChunkStruct.isStart),
                                     STAR_EOP_TYPE(dataChunkStruct.eop))
        except (STARAPIError, TypeError, ValueError):
            raise

        return dataChunkObj

    @staticmethod
    def _createPacketFromStruct(packetStruct):
        """Converts a STAR_SPACEWIRE_PACKET struct from the C API into a Packet object.

        Args:
            packetStruct (STAR_SPACEWIRE_PACKET): The packet as it is represented in the C API.

        Returns:
            packet (Packet): object holding the same data as the STAR_SPACEWIRE_PACKET struct.

        Raises:
            STARAPIError: Raised by _createDataChunkFromStruct.
            TypeError: packetStruct is not a STAR_SPACEWIRE_PACKET.
                       Raised by _createDataChunkFromStruct.
            ValueError: Raise by _createDataChunkFromStruct.
            AttributeError: Could not access contents of data chunk struct pointer.
        """

        if isinstance(packetStruct, STAR_SPACEWIRE_PACKET) is False:
            raise TypeError("packetStruct must be a STAR_SPACEWIRE_PACKET.")

        pAddressStruct = cast(packetStruct.address, POINTER(STAR_SPACEWIRE_ADDRESS))

        # Check for null pointer
        if pAddressStruct:
            addressStruct = pAddressStruct.contents

            address = []
            pAddressPathBuffer = cast(addressStruct.pPath, POINTER(c_ubyte))

            try:
                addressPathBytes = np.ctypeslib.as_array(pAddressPathBuffer, (addressStruct.pathLength,)).tolist()
            except TypeError:
                raise

            for i in range(len(addressPathBytes)):
                address.append(addressPathBytes[i])
        else:
            address = None

        pDataChunkStruct = cast(packetStruct.dataChunks, POINTER(STAR_DATA_CHUNK))
        dataChunks = []

        # End iteration once pDataChunkStruct is a null pointer.
        while pDataChunkStruct:

            try:
                dataChunkStruct = pDataChunkStruct.contents
            except AttributeError:
                raise

            try:
                dataChunkObj = ReceiveOperation._createDataChunkFromStruct(dataChunkStruct)
            except (STARAPIError, TypeError, ValueError):
                raise

            dataChunks.append(dataChunkObj)
            pDataChunkStruct = cast(dataChunkStruct.pNext, POINTER(STAR_DATA_CHUNK))

        try:
            packet = Packet(dataChunks, address)
        except (TypeError, ValueError):
            raise

        return packet

    @staticmethod
    def _createTimestampFromStruct(timestampStruct):
        """Converts a STAR_TIMESTAMP_EVENT struct from the C API into a
        TimestampEvent object.

        Args:
            timestampStruct (STAR_TIMESTAMP_EVENT): The timestamp as it is
                represented in the C API.

        Returns:
            timestampObj (TimestampEvent): object holding the same data as the
            STAR_TIMESTAMP_EVENT struct.

        Raises:
            TypeError: Errors from TimestampEvent class.
            ValueError: Errors from TimestampEvent class.
        """

        try:
            timestampObj = TimestampEvent(timestampStruct.systemClockFrequency,
                                          STAR_TIMESTAMP_TYPE(timestampStruct.typeOfData),
                                          STAR_TIMESTAMP_DIRECTION(timestampStruct.direction),
                                          timestampStruct.startSyncPulseCount,
                                          timestampStruct.startClockCycleCount,
                                          timestampStruct.startTotalCycleCount,
                                          timestampStruct.endSyncPulseCount,
                                          timestampStruct.endClockCycleCount,
                                          timestampStruct.endTotalCycleCount)
        except (TypeError, ValueError):
            raise

        return timestampObj

    @staticmethod
    def _createBroadcastMessageFromStruct(broadcastMessageStruct):
        """Converts a STAR_BROADCAST_MESSAGE struct from the C API into a
        StarBroadcastMessage object.

        Args:
            broadcastMessageStruct (STAR_BROADCAST_MESSAGE): The broadcast message as it is
                represented in the C API.

        Returns:
            broadcastMessageObj (StarBroadcastMessage): object holding the same data as the
            STAR_BROADCAST_MESSAGE struct.

        Raises:
            TypeError: Errors from StarBroadcastMessage class.
            ValueError: Errors from StarBroadcastMessage class.
        """

        try:
            broadcastMessageObj = StarBroadcastMessage(broadcastMessageStruct.channel,
                                          broadcastMessageStruct.type,
                                          broadcastMessageStruct.status,
                                          broadcastMessageStruct.dataWord1,
                                          broadcastMessageStruct.dataWord2)
        except (TypeError, ValueError):
            raise

        return broadcastMessageObj

    def _createStreamItemObjectFromStruct(self, streamItemWrapper):
        """Converts a STAR_STREAM_ITEM struct into a suitable Python object.

        Args:
            streamItemWrapper (STAR_STREAM_ITEM): The struct to convert to an
                object.

        Returns:
            streamItem: A Packet, DataChunk, LinkSpeedEvent, LinkStateEvent, or TimeCode object
            containing the same data that was stored in the STAR_STREAM_ITEM struct.

        Raises:
            STARAPIError: Raised by _createPacketFromStruct.
                          Unknown STAR Stream item type, can't handle it.
            TypeError: Raised by _createPacketFromStruct.
            AttributeError: Raised by _createPacketFromStruct.
            ValueError: Error in TimeCode.
                        Raised by _createDataChunkFromStruct.
        """

        # The stream item wrapper contains a pointer to the actual stream item.
        streamItemType = STAR_STREAM_ITEM_TYPE(streamItemWrapper.itemType)

        if streamItemType == STAR_STREAM_ITEM_TYPE.STAR_STREAM_ITEM_TYPE_SPACEWIRE_PACKET:
            streamItemStructPtr = cast(streamItemWrapper.item, POINTER(STAR_SPACEWIRE_PACKET))

        elif streamItemType == STAR_STREAM_ITEM_TYPE.STAR_STREAM_ITEM_TYPE_TIMECODE:
            streamItemStructPtr = cast(streamItemWrapper.item, POINTER(STAR_TIMECODE))

        elif streamItemType == STAR_STREAM_ITEM_TYPE.STAR_STREAM_ITEM_TYPE_LINK_STATE_EVENT:
            streamItemStructPtr = cast(streamItemWrapper.item, POINTER(STAR_LINK_STATE_EVENT))

        elif streamItemType == STAR_STREAM_ITEM_TYPE.STAR_STREAM_ITEM_TYPE_DATA_CHUNK:
            streamItemStructPtr = cast(streamItemWrapper.item, POINTER(STAR_DATA_CHUNK))

        elif streamItemType == STAR_STREAM_ITEM_TYPE.STAR_STREAM_ITEM_TYPE_LINK_SPEED_EVENT:
            streamItemStructPtr = cast(streamItemWrapper.item, POINTER(STAR_LINK_SPEED_EVENT))

        elif streamItemType == STAR_STREAM_ITEM_TYPE.STAR_STREAM_ITEM_TYPE_ERROR_INJECT:
            streamItemStructPtr = cast(streamItemWrapper.item, POINTER(STAR_ERROR_IN_DATA_INJECT))

        elif streamItemType == STAR_STREAM_ITEM_TYPE.STAR_STREAM_ITEM_TYPE_TIMESTAMP_EVENT:
            streamItemStructPtr = cast(streamItemWrapper.item, POINTER(STAR_TIMESTAMP_EVENT))

        elif streamItemType == STAR_STREAM_ITEM_TYPE.STAR_STREAM_ITEM_TYPE_BROADCAST_MESSAGE:
            streamItemStructPtr = cast(streamItemWrapper.item, POINTER(STAR_BROADCAST_MESSAGE))

        else:
            raise STARAPIError("Unknown STAR Stream Item type.")

        streamItemStruct = streamItemStructPtr.contents

        # Packet
        if streamItemWrapper.itemType == STAR_STREAM_ITEM_TYPE.STAR_STREAM_ITEM_TYPE_SPACEWIRE_PACKET:
            try:
                streamItem = self._createPacketFromStruct(streamItemStruct)
            except (STARAPIError, AttributeError, TypeError, ValueError):
                raise

        # Time-code
        elif streamItemWrapper.itemType == STAR_STREAM_ITEM_TYPE.STAR_STREAM_ITEM_TYPE_TIMECODE:

            try:
                timeCodeItem = TimeCode(streamItemStruct.value, streamItemStruct.numSinceLastTx)
            except (TypeError, ValueError):
                raise

            return timeCodeItem

        # Link state event
        elif streamItemWrapper.itemType == STAR_STREAM_ITEM_TYPE.STAR_STREAM_ITEM_TYPE_LINK_STATE_EVENT:
            try:
                streamItem = LinkStateEvent(streamItemStruct.count,
                                            bool(streamItemStruct.receiveCreditError),
                                            bool(streamItemStruct.transmitCreditError),
                                            bool(streamItemStruct.escapeError),
                                            bool(streamItemStruct.parityError),
                                            bool(streamItemStruct.disconnectError),
                                            bool(streamItemStruct.linkRunning),
                                            streamItemStruct.port)
            except (TypeError, ValueError):
                raise

        # Data chunk
        elif streamItemWrapper.itemType == STAR_STREAM_ITEM_TYPE.STAR_STREAM_ITEM_TYPE_DATA_CHUNK:

            try:
                streamItem = self._createDataChunkFromStruct(streamItemStruct)
            except (STARAPIError, TypeError, ValueError):
                raise

        # Link speed event
        elif streamItemWrapper.itemType == STAR_STREAM_ITEM_TYPE.STAR_STREAM_ITEM_TYPE_LINK_SPEED_EVENT:

            try:
                streamItem = LinkSpeedEvent(streamItemStruct.linkSpeed, streamItemStruct.port)
            except (TypeError, ValueError):
                raise

        # Error in data
        elif streamItemWrapper.itemType == STAR_STREAM_ITEM_TYPE.STAR_STREAM_ITEM_TYPE_ERROR_INJECT:

            try:
                streamItem = ErrorInData(STAR_ERROR_IN_DATA_TYPE(streamItemStruct.errorType))
            except TypeError:
                raise

        # Timestamp
        elif streamItemWrapper.itemType == STAR_STREAM_ITEM_TYPE.STAR_STREAM_ITEM_TYPE_TIMESTAMP_EVENT:
            streamItem = self._createTimestampFromStruct(streamItemStruct)

        # Broadcast message
        elif streamItemWrapper.itemType == STAR_STREAM_ITEM_TYPE.STAR_STREAM_ITEM_TYPE_BROADCAST_MESSAGE:
            streamItem = self._createBroadcastMessageFromStruct(streamItemStruct)

        else:
            raise STARAPIError("Invalid item type.")

        return streamItem

    def getTransferItem(self, index) ->\
            Union[Packet, LinkSpeedEvent, LinkStateEvent, DataChunk, TimeCode, TimestampEvent, StarBroadcastMessage, None]:
        """Gets and returns the stream item at a given index of a receive operation.
        Returns None if there is no stream item to get.

        Args:\n
            index (int): Item within the receive operation to access.

        Raises:\n
            STARAPIError:\n
                The STAR-API library could not be loaded.\n
                Raised by _createStreamItemObjectFromStruct.\n
                The receive transfer operation is no longer valid.\n
            TypeError:\n
                index is not an int.\n
                Raised by _createStreamItemObjectFromStruct.\n
            AttributeError:\n
                Raised by _createStreamItemObjectFromStruct.
            ValueError:\n
                Raised by _createStreamItemObjectFromStruct.
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        if type(index) != int:
            raise TypeError("index must be an int.")

        if self._structAddress is None:
            raise STARAPIError("The receive transfer operation is no longer valid.")

        pTransferOperation = cast(self._structAddress, c_void_p)

        # Set argument types and return type of the C function
        star_lib.STAR_getTransferItem.argtypes = [c_void_p, c_uint32]
        star_lib.STAR_getTransferItem.restype = POINTER(STAR_STREAM_ITEM)

        streamItemWrapperPtr = star_lib.STAR_getTransferItem(pTransferOperation, c_uint32(index))

        # Check for null pointer
        if streamItemWrapperPtr:

            # Cast the value returned by STAR_getTransferItem to POINTER(STAR_STREAM_ITEM) type
            streamItemWrapperPointer = cast(streamItemWrapperPtr, POINTER(STAR_STREAM_ITEM))

            streamItemWrapper = streamItemWrapperPointer.contents

            try:
                streamItem = self._createStreamItemObjectFromStruct(streamItemWrapper)
            except (STARAPIError, AttributeError, TypeError, ValueError):
                raise

            return streamItem
        else:
            return None

    def getTransferItemCount(self) -> int:
        """Gets and returns the current count of stream items received by the operation.

        Raises:\n
            STARAPIError:\n
                The STAR-API library could not be loaded.\n
                The receive transfer operation is no longer valid.\n
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        if self._structAddress is None:
            raise STARAPIError("The receive transfer operation is no longer valid.")

        pTransferOperation = cast(self._structAddress, c_void_p)

        # Set argument types and return type of the C function
        star_lib.STAR_getTransferItemCount.argtypes = [c_void_p]
        star_lib.STAR_getTransferItemCount.restype = c_uint32

        itemCount = star_lib.STAR_getTransferItemCount(pTransferOperation)

        return itemCount

    def getTransferItemList(self) -> list:
        """Gets and returns the entire list of transfer items associated with the receive operation.
        A stream item may be a `STAR_system.packet.Packet`, a `STAR_system.data_chunk.DataChunk`, a `STAR_system.link_speed_event.LinkSpeedEvent`,
        `STAR_system.link_state_event.LinkStateEvent`, `STAR_system.timestamp_event.TimestampEvent` or a `STAR_system.time_code.TimeCode`.
        Returns an empty list if there are no transfer items to get.

        Raises:\n
            STARAPIError:\n
                The STAR-API library could not be loaded.\n
                Raised by _createStreamItemObjectFromStruct.\n
                The receive transfer operation is no longer valid.\n
            TypeError:\n
                Raised by _createStreamItemObjectFromStruct.\n
            ValueError:\n
                Raised by _createStreamItemObjectFromStruct.\n
            AttributeError:\n
                Raised by _createStreamItemObjectFromStruct.\n
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        if self._structAddress is None:
            raise STARAPIError("The receive transfer operation is no longer valid.")

        # Create pointer to int variable that will be used as input parameter to the C library function
        streamItemCount = c_uint32(0)
        pStreamItemCount = pointer(streamItemCount)

        pTransferOperation = cast(self._structAddress, c_void_p)

        # Set argument types and return type of the C function
        star_lib.STAR_getTransferItemList.argtypes = [c_void_p, POINTER(c_uint32)]
        star_lib.STAR_getTransferItemList.restype = POINTER(POINTER(STAR_STREAM_ITEM))

        streamItemWrapperArray = star_lib.STAR_getTransferItemList(pTransferOperation, pStreamItemCount)

        streamItemWrapperPointers = [cast(streamItemWrapperArray[i], POINTER(STAR_STREAM_ITEM))
                                     for i in range(streamItemCount.value)]

        try:
            streamItems = [self._createStreamItemObjectFromStruct(streamItemWrapperPointer.contents)
                           for streamItemWrapperPointer in streamItemWrapperPointers]
        except (STARAPIError, TypeError, ValueError, AttributeError):
            raise

        # Set argument types and return type of the C function
        star_lib.STAR_destroyStreamItem.argtypes = [POINTER(STAR_STREAM_ITEM)]
        star_lib.STAR_destroyStreamItem.restype = None

        # Free memory
        [star_lib.STAR_destroyStreamItem(streamItemWrapperPointer)
         for streamItemWrapperPointer in streamItemWrapperPointers]

        return streamItems


class TransmitOperation(TransferOperation):
    """Represents a transmit operation.

    Attributes:\n
        _structAddress (ctypes.c_void_p): The address where the internal C
            transfer operation is stored. This attribute is not intended to be
            used or modified by the user.
        _transferCompletionListener (types.FunctionType / types.MethodType): Callback function that will
            be called when the transfer operation completion occurs.

    Args:\n
        streamItems (list): A list of stream items. Stream items are instances
            of `STAR_system.packet.Packet`, a `STAR_system.data_chunk.DataChunk`, a `STAR_system.link_speed_event.LinkSpeedEvent`,
            `STAR_system.link_state_event.LinkStateEvent`, `STAR_system.error_in_data.ErrorInData` or a `STAR_system.time_code.TimeCode`.\n
            Note that the user should not need to transmit event types and this may lead to errors.
        allocatedStructAddress (int): The struct address of a previously allocated receive operation. Note: When
                this input argument is not None, a new ReceiveOperation object will NOT be created. Defaults to None.
    """

    def __init__(self, streamItems, allocatedStructAddress=None):
        """Constructor:\n
            Creates a transmit operation that can be submitted later. In case the allocatedStructAddress variable
            is not None, a new transfer operation will not be created (but the existing one, as defined
            by the transmit operation structure pointer address, referenced and used).\n

        Raises:\n
            STARAPIError:\n
                The STAR-API library could not be loaded.\n
            TypeError:\n
                streamItems is not a list.\n
                streamItems contained an object that was not an instance of
                Packet, DataChunk, LinkSpeedEvent, LinkStateEvent, TimeCode,
                ErrorInData or TimestampEvent.\n
                allocatedStructAddress was not an int.\n
        """

        if allocatedStructAddress is not None and type(allocatedStructAddress) != int:
            raise TypeError(f"allocatedStructAddress must be int. Got {type(allocatedStructAddress)}.")

        super().__init__(allocatedStructAddress)

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        if isinstance(streamItems, list) is False:
            raise TypeError("streamItems must be a list.")

        if allocatedStructAddress is None:

            if streamItems is not None:
                nrOfStreamItems = len(streamItems)
                streamItemArrayType = POINTER(STAR_STREAM_ITEM) * nrOfStreamItems
                streamItemArray = streamItemArrayType()

                for i in range(len(streamItems)):

                    currentStreamItem = streamItems[i]

                    makePointer = True

                    if isinstance(currentStreamItem, Packet) is True:
                        streamItemStruct = self._convertPacketToStreamItemStruct(currentStreamItem)
                    elif isinstance(currentStreamItem, DataChunk) is True:
                        streamItemStruct = self._convertDataChunkToStreamItemStruct(currentStreamItem)
                    elif isinstance(currentStreamItem, LinkSpeedEvent) is True:
                        streamItemStruct = self._convertLinkSpeedEventToStreamItemStruct(currentStreamItem)
                    elif isinstance(currentStreamItem, LinkStateEvent) is True:
                        streamItemStruct = self._convertLinkStateEventToStreamItemStruct(currentStreamItem)
                    elif isinstance(currentStreamItem, TimeCode) is True:
                        streamItemStruct = self._convertTimeCodeToStreamItemStruct(currentStreamItem)
                    elif isinstance(currentStreamItem, ErrorInData) is True:
                        streamItemStruct = self._convertErrorInDataToStreamItemStruct(currentStreamItem)
                    elif isinstance(currentStreamItem, StarBroadcastMessage) is True:
                        streamItemStruct = self._convertBroadcastMessageToStreamItemStruct(currentStreamItem)
                    elif isinstance(currentStreamItem, POINTER(STAR_STREAM_ITEM)) is True:
                        streamItemStruct = currentStreamItem
                        makePointer = False
                    else:
                        raise STARAPIError("Unknown stream item.")

                    if makePointer is True:
                        streamItemArray[i] = pointer(streamItemStruct)
                    else:
                        streamItemArray[i] = streamItemStruct

                pStreamItemArray = pointer(streamItemArray)

                star_lib.STAR_createTxOperation.argtypes = [POINTER(POINTER(STAR_STREAM_ITEM) * nrOfStreamItems), c_uint32]
                star_lib.STAR_createTxOperation.restype = c_void_p

                self._structAddress = star_lib.STAR_createTxOperation(pStreamItemArray, c_uint32(nrOfStreamItems))

    @staticmethod
    def _convertErrorInDataToStreamItemStruct(errorInData):
        """Converts an ErrorInData object into a STAR_ERROR_IN_DATA_INJECT structure.

        Args:
            errorInData: The ErrorInData object to be converted.

        Returns:
            streamItemStruct (STAR_STREAM_ITEM): A struct containing a pointer to a
                STAR_ERROR_IN_DATA_INJECT struct that holds the same information as
                the original ErrorInData object.
        Raises:
            TypeError: errorInData was not a ErrorInData object.
        """

        if isinstance(errorInData, ErrorInData) is False:
            raise TypeError("errorInData must be an ErrorInData.")

        errorStruct = STAR_ERROR_IN_DATA_INJECT(c_int32(errorInData.errorType.value))

        streamItemStruct = STAR_STREAM_ITEM()
        streamItemStruct.itemType = STAR_STREAM_ITEM_TYPE.STAR_STREAM_ITEM_TYPE_ERROR_INJECT
        streamItemStruct.item = cast(pointer(errorStruct), c_void_p)

        return streamItemStruct

    @staticmethod
    def _convertBroadcastMessageToStreamItemStruct(broadcastMessage):
        """Converts a StarBroadcastMessage object into a STAR_BROADCAST_MESSAGE structure.

        Args:
            broadcastMessage: The StarBroadcastMessage object to be converted.

        Returns:
            streamItemStruct (STAR_STREAM_ITEM): A struct containing a pointer to a
                STAR_BROADCAST_MESSAGE struct that holds the same information as
                the original StarBroadcastMessage object.
        Raises:
            TypeError: broadcastMessage was not a StarBroadcastMessage object.
        """

        if isinstance(broadcastMessage, StarBroadcastMessage) is False:
            raise TypeError("broadcastMessage must be an StarBroadcastMessage.")

        broadcastMessageStruct = STAR_BROADCAST_MESSAGE()
        broadcastMessageStruct.channel = c_uint8(broadcastMessage.channel)
        broadcastMessageStruct.type = c_uint8(broadcastMessage.bType)
        broadcastMessageStruct.status = c_uint8(broadcastMessage.status)
        broadcastMessageStruct.dataWord1 = c_uint8(broadcastMessage.dataWord1)
        broadcastMessageStruct.dataWord2 = c_uint8(broadcastMessage.dataWord2)

        streamItemStruct = STAR_STREAM_ITEM()
        streamItemStruct.itemType = STAR_STREAM_ITEM_TYPE.STAR_STREAM_ITEM_TYPE_BROADCAST_MESSAGE
        streamItemStruct.item = cast(pointer(broadcastMessageStruct), c_void_p)

        return streamItemStruct

    @staticmethod
    def _convertPacketToStreamItemStruct(packet):
        """Converts a Packet object into a STAR_STREAM_ITEM structure.

        Args:
            packet: The Packet object to be converted.

        Returns:
            streamItemStruct (STAR_STREAM_ITEM) A struct containing a pointer to a
                STAR_SPACEWIRE_PACKET struct that holds the same data as the original Packet object.

        Raises:
            TypeError: packet was not a Packet object.
        """

        if isinstance(packet, Packet) is False:
            raise TypeError("packet must be a Packet.")

        packetStruct = STAR_SPACEWIRE_PACKET()

        if packet.address is not None:

            address = STAR_SPACEWIRE_ADDRESS()
            address.pathLength = len(packet.address)

            pathArray = (c_uint8 * address.pathLength)()

            for i in range(len(packet.address)):
                pathArray[i] = packet.address[i]

            address.pPath = cast(pathArray, c_void_p)

            packetStruct.address = pointer(address)

        dataChunkStructs = []
        for i in range(len(packet.dataChunks)):
            dataChunk = packet.dataChunks[i]

            dataChunkStruct = STAR_DATA_CHUNK()

            packetData = c_char_p(dataChunk.dataBytes)
            pPacketData = cast(packetData, c_void_p)

            dataChunkStruct.data = pPacketData
            dataChunkStruct.dataLength = c_uint32(len(dataChunk.data))
            dataChunkStruct.isStart = c_int32(dataChunk.isStart)

            dataChunkStruct.eop = c_int32(dataChunk.eop.value)

            dataChunkStructs.append(dataChunkStruct)

        for i in range(len(dataChunkStructs)):
            dataChunkStruct = dataChunkStructs[i]

            if i > 0:
                dataChunkStruct.pPrev = cast(pointer(dataChunkStructs[i-1]), c_void_p)
            else:
                lastChunkIndex = len(dataChunkStructs)-1
                dataChunkStruct.pPrev = cast(pointer(dataChunkStructs[lastChunkIndex]), c_void_p)

            if i < len(dataChunkStructs) - 1:
                dataChunkStruct.pNext = cast(pointer(dataChunkStructs[i+1]), c_void_p)
            else:
                dataChunkStruct.pNext = None

        dataChunksPointer = pointer(dataChunkStructs[0])
        packetStruct.dataChunks = dataChunksPointer

        streamItemStruct = STAR_STREAM_ITEM()
        streamItemStruct.itemType = STAR_STREAM_ITEM_TYPE.STAR_STREAM_ITEM_TYPE_SPACEWIRE_PACKET
        streamItemStruct.item = cast(pointer(packetStruct), c_void_p)

        return streamItemStruct

    @staticmethod
    def _convertDataChunkToStreamItemStruct(dataChunk):
        """Converts a DataChunk object into a STAR_STREAM_ITEM structure.

        Args:
            dataChunk: The DataChunk object to be converted.

        Returns:
            streamItemStruct (STAR_STREAM_ITEM): A struct containing a pointer to a
                STAR_DATA_CHUNK struct that holds the same data as the original DataChunk object.

        Raises:
            TypeError: dataChunk was not a DataChunk object.
        """

        if isinstance(dataChunk, DataChunk) is False:
            raise TypeError("dataChunk must be a DataChunk.")

        dataChunkStruct = STAR_DATA_CHUNK()

        # Create ctypes array from the contents of the DataChunk
        data = c_char_p(dataChunk.dataBytes)

        # Cast the ctypes array to c_void_p
        pData = cast(data, c_void_p)

        dataChunkStruct.data = pData

        dataChunkStruct.dataLength = c_uint32(len(dataChunk.data))
        dataChunkStruct.isStart = c_int32(dataChunk.isStart)

        dataChunkStruct.eop = c_int32(dataChunk.eop.value)

        dataChunkStruct.pPrev = cast(pointer(dataChunkStruct), c_void_p)

        streamItemStruct = STAR_STREAM_ITEM()
        streamItemStruct.itemType = STAR_STREAM_ITEM_TYPE.STAR_STREAM_ITEM_TYPE_DATA_CHUNK
        streamItemStruct.item = cast(pointer(dataChunkStruct), c_void_p)

        return streamItemStruct

    @staticmethod
    def _convertTimeCodeToStreamItemStruct(timeCode):
        """Converts a TimeCode object into a STAR_STREAM_ITEM structure.

        Args:
            timeCode: The TimeCode object to be converted.

        Returns:
            streamItemStruct (STAR_STREAM_ITEM): A struct containing a pointer to a STAR_TIMECODE
            struct that holds the same data as the original TimeCode object.

        Raises:
            TypeError: timeCode was not a TimeCode object.
        """

        if isinstance(timeCode, TimeCode) is False:
            raise TypeError("timeCode must be a TimeCode.")

        timeCodeStruct = STAR_TIMECODE()
        timeCodeStruct.numSinceLastTx = c_uint16(timeCode.numSinceLastTx)
        timeCodeStruct.value = c_uint8(timeCode.value)

        streamItemStruct = STAR_STREAM_ITEM()
        streamItemStruct.itemType = STAR_STREAM_ITEM_TYPE.STAR_STREAM_ITEM_TYPE_TIMECODE
        streamItemStruct.item = cast(pointer(timeCodeStruct), c_void_p)
        streamItemStruct.pReceivedOperation = None
        streamItemStruct.pNext = None

        return streamItemStruct

    @staticmethod
    def _convertLinkSpeedEventToStreamItemStruct(linkSpeedEvent):
        """Converts a LinkSpeedEvent object into a STAR_STREAM_ITEM structure.

        Args:
            linkSpeedEvent: The LinkSpeedEvent object to be converted.

        Returns:
            streamItemStruct (STAR_STREAM_ITEM): A struct containing a pointer to a 
            STAR_LINK_SPEED_EVENT struct that holds the same data as the original 
            LinkSpeedEvent object.

        Raises:
            TypeError: linkSpeedEvent was not a LinkSpeedEvent object.
        """

        if isinstance(linkSpeedEvent, LinkSpeedEvent) is False:
            raise TypeError("linkSpeedEvent must be a LinkSpeedEvent.")

        linkSpeedEventStruct = STAR_LINK_SPEED_EVENT()
        linkSpeedEventStruct.linkSpeed = c_uint32(linkSpeedEvent.linkSpeed)
        linkSpeedEventStruct.port = c_uint8(linkSpeedEvent.port)

        streamItemStruct = STAR_STREAM_ITEM()
        streamItemStruct.itemType = STAR_STREAM_ITEM_TYPE.STAR_STREAM_ITEM_TYPE_LINK_SPEED_EVENT
        streamItemStruct.item = cast(pointer(linkSpeedEventStruct), c_void_p)

        return streamItemStruct

    @staticmethod
    def _convertLinkStateEventToStreamItemStruct(linkStateEvent):
        """Converts a LinkStateEvent object into a STAR_STREAM_ITEM structure.

        Args:
            linkStateEvent: The LinkStateEvent object to be converted.

        Returns:
            streamItemStruct (STAR_STREAM_ITEM): A struct containing a pointer to a 
            STAR_LINK_STATE_EVENT struct that holds the same data as the original LinkStateEvent 
            object.

        Raises:
            TypeError: linkStateEvent was not a LinkStateEvent object.
        """

        if isinstance(linkStateEvent, LinkStateEvent) is False:
            raise TypeError("linkStateEvent must be a LinkStateEvent.")

        linkStateEventStruct = STAR_LINK_STATE_EVENT()
        linkStateEventStruct.count               = c_uint8(    linkStateEvent.count             )
        linkStateEventStruct.receiveCreditError  = c_uint32(int(linkStateEvent.receiveCreditError ))
        linkStateEventStruct.transmitCreditError = c_uint32(int(linkStateEvent.transmitCreditError))
        linkStateEventStruct.escapeError         = c_uint32(int(linkStateEvent.escapeError        ))
        linkStateEventStruct.parityError         = c_uint32(int(linkStateEvent.parityError        ))
        linkStateEventStruct.disconnectError     = c_uint32(int(linkStateEvent.disconnectError    ))
        linkStateEventStruct.linkRunning         = c_uint32(int(linkStateEvent.linkRunning        ))
        linkStateEventStruct.port                = c_uint8(int(linkStateEvent.port              ))

        streamItemStruct = STAR_STREAM_ITEM()
        streamItemStruct.itemType = STAR_STREAM_ITEM_TYPE.STAR_STREAM_ITEM_TYPE_LINK_STATE_EVENT
        streamItemStruct.item = cast(pointer(linkStateEventStruct), c_void_p)

        return streamItemStruct
