"""Contains classes to represent stream items.

Brief:\n
    Classes to represent the different stream items.

Copyright:\n
    2022 STAR-Dundee Ltd.
"""

import os
from ctypes import *

from STAR_system import STAR_LIB, STAR_API_LIB_LOAD_ERROR_STR
from STAR_system.error_in_data import STAR_ERROR_IN_DATA_TYPE
from STAR_system.STAR_enums import STAR_EOP_TYPE
from STAR_system.STAR_exceptions import STARAPIError
from STAR_system.STAR_structures import STAR_STREAM_ITEM, STAR_SPACEWIRE_ADDRESS
from STAR_system.STAR_structure_classes import StarBroadcastMessage

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


class StreamItem(object):

    # Create STAR packet
    @staticmethod
    def createPacket(address, data, eopMarker) -> POINTER(STAR_STREAM_ITEM):
        """ Creates a new SpaceWire packet stream item from user provided data.  This
            stream item should be destroyed when it is no longer required by calling
            `STAR_system.stream_item.StreamItem.destroyStreamItem`.

            Returns a `STAR_system.STAR_structures.STAR_STREAM_ITEM` pointer object containing the Packet.

            Args:\n
                address (list of ints or None): Routing address of the packet. None in case it is not used.
                data (list of ints): Data that the Packet stream item will contain.
                eopMarker (STAR_system.STAR_enums.STAR_EOP_TYPE): EOP marker that will be put at the end of the Packet stream item.

            Raises:\n
                STARAPIError:\n
                    The STAR-API library could not be loaded.\n

                TypeError:\n
                    address is not a list and address is not None.\n
                    any element in address must be an int.\n
                    data is not a list.\n
                    any element in data must be an int.\n
                    eopMarker is not a STAR_EOP_TYPE.\n
        """

        if isinstance(address, list) is False and address is not None:
            raise TypeError("address must be a list of ints or None.")

        if address is not None:
            for addressByte in address:
                if type(addressByte) != int:
                    raise TypeError("every address byte must be an int.")

        if isinstance(data, list) is False:
            raise TypeError("data must be a list of ints.")

        for dataByte in data:
            if type(dataByte) != int:
                raise TypeError("an element in data (list) was not an int.")

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        # Construct the STAR_SPACEWIRE_ADDRESS object
        addressObject = STAR_SPACEWIRE_ADDRESS()

        # Address length
        if address is not None:
            addressLength = len(address)

            # Create an array that holds the path bytes
            addressPath = (c_uint8 * addressLength)()

            # Assign values of the array
            for i in range(addressLength):
                addressPath[i] = address[i]

            # Cast it to pointer
            pAddressPath = cast(addressPath, c_void_p)

        else:
            pAddressPath = None
            addressLength = 0

        pathLength = c_uint16(addressLength)

        # Populate the fields of the STAR_SPACEWIRE_ADDRESS object
        addressObject.pPath = pAddressPath
        addressObject.pathLength = pathLength

        # Cast to pointer
        pAddressObject = pointer(addressObject)

        # Determine the length of the data
        dataLength = len(data)

        # Create c type array
        dataArray = (c_uint8 * dataLength)()
        for i in range(0, dataLength):
            dataArray[i] = c_uint8(data[i])

        # Cast to pointer
        pDataArray = pointer(dataArray)

        # Set argument types and return type of the C function
        star_lib.STAR_createPacket.argtypes = [POINTER(STAR_SPACEWIRE_ADDRESS), POINTER(c_uint8 * dataLength),
                                               c_uint32, STAR_EOP_TYPE]
        star_lib.STAR_createPacket.restype = POINTER(STAR_STREAM_ITEM)

        packetStreamItem = star_lib.STAR_createPacket(pAddressObject, pDataArray, c_uint32(dataLength), eopMarker)

        if packetStreamItem is None:
            raise STARAPIError("Could not create STAR packet stream item.")

        return packetStreamItem

    @staticmethod
    def createTimeCode(value) -> POINTER(STAR_STREAM_ITEM):
        """Creates a Time-code stream item. This stream item should be destroyed when
           it is no longer required by calling `STAR_system.stream_item.StreamItem.destroyStreamItem`.

           Returns a `STAR_system.STAR_structures.STAR_STREAM_ITEM` pointer object containing the Timecode.

           Args:\n
               value (int): The value of the timecode.

            Raises:\n
                STARAPIError:\n
                    The STAR-API library could not be loaded.\n
                TypeError:\n
                    value is not an int.
        """

        if type(value) != int:
            raise TypeError("value must be an int.")

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        star_lib.STAR_createTimeCode.argtypes = [c_uint8]
        star_lib.STAR_createTimeCode.restype = POINTER(STAR_STREAM_ITEM)

        timeCodeStreamItem = star_lib.STAR_createTimeCode(c_uint8(value))

        if timeCodeStreamItem is None:
            raise STARAPIError("Could not create STAR Timecode stream item.")

        return timeCodeStreamItem

    @staticmethod
    def createDataChunk(data, isStart, eopMarker) -> POINTER(STAR_STREAM_ITEM):
        """ Creates a new SpaceWire data chunk stream item from user provided data. This
            stream item should be destroyed when it is no longer required by calling `STAR_system.stream_item.StreamItem.destroyStreamItem`.\n

            Returns a `STAR_system.STAR_structures.STAR_STREAM_ITEM` pointer object containing the DataChunk.\n

            Args:\n
                data (list of ints): Data that the DataChunk stream item will contain.
                isStart (bool): Whether the chunk is the start of a packet (True) or not (False).
                eopMarker (STAR_system.STAR_enums.STAR_EOP_TYPE): EOP marker that will be put at the end of the DataChunk stream item.

            Raises:\n
                STARAPIError:\n
                    The STAR-API library could not be loaded.\n

                TypeError:\n
                    data is not a list.\n
                    any element in data must be an int.\n
                    eopMarker is not a STAR_EOP_TYPE.\n
        """

        if isinstance(data, list) is False:
            raise TypeError("data must be a list of ints.")

        for dataByte in data:
            if type(dataByte) != int:
                raise TypeError("an element in data (list) was not an int.")

        if type(isStart) != bool:
            raise TypeError("isStart must be a bool.")

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        # Determine the length of the data
        dataLength = len(data)

        # Create c type array
        dataArray = (c_uint8 * dataLength)()
        for i in range(0, dataLength):
            dataArray[i] = c_uint8(data[i])

        # Cast to pointer
        pDataArray = pointer(dataArray)

        # Set argument types and return type of the C function
        star_lib.STAR_createDataChunk.argtypes = [POINTER(c_uint8 * dataLength), c_uint32, c_int32, STAR_EOP_TYPE]
        star_lib.STAR_createDataChunk.restype = POINTER(STAR_STREAM_ITEM)

        dataChunkStreamItem = star_lib.STAR_createDataChunk(pDataArray, dataLength, c_int32(isStart), eopMarker)

        if dataChunkStreamItem is None:
            raise STARAPIError("Could not create STAR Data Chunk stream item.")

        return dataChunkStreamItem

    @staticmethod
    def createErrorInData(error) -> POINTER(STAR_STREAM_ITEM):
        """Creates an error in data stream item. This stream item can be transmitted to
           cause an error to occur on the next data character to be transmitted.
           This stream item should be destroyed when it is no longer required by calling `STAR_system.stream_item.StreamItem.destroyStreamItem`.

            Returns a `STAR_system.STAR_structures.STAR_STREAM_ITEM` pointer object containing the Error in Data.

           Args:\n
               error (STAR_system.STAR_enums.STAR_ERROR_IN_DATA_TYPE): The error.

            Raises:\n
                STARAPIError:\n
                    The STAR-API library could not be loaded.\n
                TypeError:\n
                    error is not an STAR_ERROR_IN_DATA_TYPE.
        """

        if isinstance(error, STAR_ERROR_IN_DATA_TYPE) is False:
            raise TypeError("error must be an STAR_ERROR_IN_DATA_TYPE.")

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        star_lib.STAR_createErrorInData.argtypes = [STAR_ERROR_IN_DATA_TYPE]
        star_lib.STAR_createErrorInData.restype = POINTER(STAR_STREAM_ITEM)

        errorInDataStreamItem = star_lib.STAR_createErrorInData(error)

        if errorInDataStreamItem is None:
            raise STARAPIError("Could not create STAR Error in Data object.")

        return errorInDataStreamItem

    @staticmethod
    def createBroadcastMessage(broadcastMessage) -> POINTER(STAR_STREAM_ITEM):
        """Creates a broadcast message stream item.
           This stream item should be destroyed when it is no longer required by calling `STAR_system.stream_item.StreamItem.destroyStreamItem`.

            Returns a `STAR_system.STAR_structures.STAR_STREAM_ITEM` pointer object containing the Broadcast Message.

           Args:\n
               broadcastMessage (STAR_system.STAR_structure_classes.StarBroadcastMessage): The broadcast message instance.

            Raises:\n
                STARAPIError:\n
                    The STAR-API library could not be loaded.\n
                TypeError:\n
                    StarBroadcastMessage is not an `STAR_system.STAR_structure_classes.StarBroadcastMessage`.\n
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        if isinstance(broadcastMessage, StarBroadcastMessage) is False:
            raise TypeError("broadcastMessage must be a StarBroadcastMessage.")

        # Set argument types and return type of the C function
        star_lib.STAR_createBroadcastMessage.argtypes = [c_uint8, c_uint8, c_uint8, c_uint32, c_uint32]
        star_lib.STAR_createBroadcastMessage.restype = POINTER(STAR_STREAM_ITEM)

        broadcastMessageStreamItem = star_lib.STAR_createBroadcastMessage(broadcastMessage.channel,
                                                                          broadcastMessage.bType,
                                                                          broadcastMessage.status,
                                                                          broadcastMessage.dataWord1,
                                                                          broadcastMessage.dataWord2)

        if broadcastMessageStreamItem is None:
            raise STARAPIError("Could not create Broadcast Message object.")

        return broadcastMessageStreamItem

    @staticmethod
    def destroyStreamItem(streamItemPtr):
        """Destroys the pointer to a stream item created by one of the functions `STAR_system.stream_item.StreamItem.createPacket`,
        `STAR_system.stream_item.StreamItem.createTimeCode`, `STAR_system.stream_item.StreamItem.createDataChunk`,
        `STAR_system.stream_item.StreamItem.createErrorInData`.

       Args:\n
           streamItemPtr (STAR_system.STAR_structures.STAR_STREAM_ITEM pointer): Pointer to the `STAR_system.STAR_structures.STAR_STREAM_ITEM` that is to be destroyed.

        Raises:\n
            STARAPIError:\n
                The STAR-API library could not be loaded.\n
            TypeError:\n
                streamItem is not an LP_STAR_STREAM_ITEM.
        """

        if isinstance(streamItemPtr, POINTER(STAR_STREAM_ITEM)) is False:
            raise TypeError("streamItemPtr must be an LP_STAR_STREAM_ITEM.")

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        star_lib.STAR_destroyStreamItem.argtypes = [POINTER(STAR_STREAM_ITEM)]
        star_lib.STAR_destroyStreamItem.restype = None

        star_lib.STAR_destroyStreamItem(streamItemPtr)


