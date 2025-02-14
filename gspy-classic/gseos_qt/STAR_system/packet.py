"""Represents a SpaceWire packet.

Brief:\n
    Represents a packet.

Copyright:\n
    2022 STAR-Dundee Ltd
"""
from typing import Union

from STAR_system.data_chunk import DataChunk
from STAR_system.STAR_exceptions import STARAPIError
from STAR_system.STAR_enums import STAR_EOP_TYPE


class Packet(object):
    """Represents a packet.
    
    Attributes:\n
        dataChunks (list of STAR_system.data_chunk.DataChunk): The data that makes up the packet.
        address (list of ints): The packet's address (optional), defaults to None.
            This is provided for convenience only (see constructor signature for details).
            There is no difference between specifying a packet with an address of [0xFE, 0xAB] and data of
            [0x01, 0x02, 0x03, 0x03] and specifying a packet with no explicit address and data of [0xFE, 0xAB, 0x01, 0x02, 0x03, 0x04].
    """

    # This is the main constructor of this class
    def __init__(self, data, address=None, eop=STAR_EOP_TYPE.STAR_EOP_TYPE_EOP):
        """Constructor:\n
            Initialises a `STAR_system.packet.Packet` object. The constructor of the Packet class always takes at least 1 parameter (compulsory)
            and a maximum of 3 parameters (1 or 2 optional parameters).\n

            The first parameter is always the data. It can be either a list of `STAR_system.data_chunk.DataChunk` objects or
            a list of ints (bytes).\n

            The second parameter is the address and it takes the form of a list of ints (bytes). This parameter is optional
            and defaults to None (no address bytes).\n

            The third parameter is the EOP marker (`STAR_system.STAR_enums.STAR_EOP_TYPE`). This parameter is optional
            and defaults to `STAR_system.STAR_enums.STAR_EOP_TYPE.STAR_EOP_TYPE_EOP`.\n
            Note: The third parameter is only taken into account if the first parameter (data) is specified in the form of a list of ints.
            Otherwise (in case the data is specified in the form of a list of `STAR_system.data_chunk.DataChunk` objects,
            the correct EOP marker needs to be specified for each `STAR_system.data_chunk.DataChunk` object.

            Note: The order of the parameters (if more than 1 is provided) must always be maintained: data, address, EOP marker.

        Raises:\n
            TypeError:\n
                First argument passed to the constructor of the Packet class needs to be a list (of DataChunk objects or ints).\n
            ValueError:\n
                Constructor of the Packet class requires at least 1 argument (and a maximum of 3 arguments).\n
                There must be at least one element in the first parameter (list of DataChunk objects or list of ints) of the constructor.\n

        """

        # See which "constructor" needs to be called
        if len(data) > 0:
            if isinstance(data[0], DataChunk):
                try:
                    self._constructPacketFromDataChunks(data, address)
                except TypeError:
                    raise
            elif isinstance(data[0], int):
                try:
                    self._constructPacketFromDataBytes(data, address, eop)
                except (TypeError, ValueError):
                    raise
            else:
                raise TypeError("First argument of the Packet class constructor most be either a list of"
                                "DataChunk objects or a list of ints.")
        else:
            raise ValueError("There must be at least one element in the first argument (list of DataChunk objects"
                             "or list of ints) of the Packet constructor.")

    def _constructPacketFromDataChunks(self, dataChunks, address=None):
        """Constructor:\n
            Initialises a `STAR_system.packet.Packet` object.

        Args:\n
            dataChunks (list of STAR_system.data_chunk.DataChunk): The data that makes up the packet.
            address (list or None): The packet's address (optional), defaults to None.

        Raises:\n
            TypeError:\n
                dataChunks is not a list.\n
                At least one item in dataChunks is not an instance of DataChunks.\n
                address is not a list or None.\n
        """

        if isinstance(dataChunks, list) is False:
            raise TypeError("dataChunks must be a list of DataChunk objects.")
        if address is not None and isinstance(address, list) is False:
            raise TypeError("address must be None or a list.")
        for dataChunk in dataChunks:
            if not isinstance(dataChunk, DataChunk):
                raise TypeError("Every item in dataChunks must be an instance of DataChunk.")

        self.address = address
        self.dataChunks = dataChunks

    def _constructPacketFromDataBytes(self, dataBytes, address=None, eopMarker=None):
        """Constructor:\n
            Initialises a `STAR_system.packet.Packet` object.

        Args:\n
            dataBytes (list): The data that makes up the packet.
            address (list): The packet's address (optional), defaults to None.
            eopMarker (STAR_system.STAR_enums.STAR_EOP_TYPE): EOP marker of the last DataChunk of the Packet (optional), defaults to None.

        Raises:\n
            TypeError:\n
                dataBytes is not a list.\n
                At least one item in dataBytes is not an int.\n
                address is not a list or None.\n
                Exception raised by DataChunk constructor.
            ValueError:\n
                Exception raised by DataChunk constructor.
        """

        if isinstance(dataBytes, list) is False:
            raise TypeError("dataBytes must be a list of ints.")
        for dataByte in dataBytes:
            if type(dataByte) != int:
                raise TypeError("Every item in dataBytes must be an int.")
        if address is not None and isinstance(address, list) is False:
            raise TypeError("address must be None or a list.")
        if eopMarker is not None and isinstance(eopMarker, STAR_EOP_TYPE) is False:
            raise TypeError("eopMarker must be None or a STAR_EOP_TYPE.")

        # Set the address
        self.address = address

        # Determine the number of DataChunk objects to be created
        dataLength = len(dataBytes)

        # The number of full DataChunk objects
        nrOfFullDataChunks = dataLength // DataChunk.MAX_CHUNK_SIZE

        # The number of partial DataChunk objects
        if dataLength > nrOfFullDataChunks * DataChunk.MAX_CHUNK_SIZE:
            nrOfPartialDataChunks = 1
        else:
            nrOfPartialDataChunks = 0

        # The number of DataChunk objects
        nrOfDataChunks = nrOfFullDataChunks + nrOfPartialDataChunks

        # In case the data can be fit into just one single DataChunk
        if nrOfDataChunks == 1:

            # Create the one single DataChunk object
            try:
                newDataChunk = DataChunk(dataBytes, True, eopMarker)
            except (TypeError, ValueError):
                raise

            # The internal list of DataChunks is made up of this single DataChunk
            self.dataChunks = [newDataChunk]

        else:

            # Set the internal list of DataChunks to be empty
            self.dataChunks = []

            # Keep track of the current offset
            dataBytesOffset = 0

            # Keep track of the remaining data bytes
            nrOfRemainingDataBytes = dataLength

            # Create each DataChunk
            for i in range(0, nrOfDataChunks):

                # Check whether this is the first DataChunk
                isStart = i == 0

                # Check whether the EOP flag needs to be set
                if i == nrOfDataChunks - 1:
                    dataChunkEOPMarker = eopMarker
                else:
                    dataChunkEOPMarker = STAR_EOP_TYPE.STAR_EOP_TYPE_NONE

                # Size of new DataChunk object (to be created)
                sizeOfNewDataChunk = min(DataChunk.MAX_CHUNK_SIZE, nrOfRemainingDataBytes)

                # Create DataChunk object
                try:
                    newDataChunk = DataChunk(
                        dataBytes[dataBytesOffset:dataBytesOffset+sizeOfNewDataChunk], isStart, dataChunkEOPMarker)
                except (TypeError, ValueError):
                    raise

                # Add this DataChunk object to the internal list
                self.dataChunks.append(newDataChunk)

                # Move the data bytes offset
                dataBytesOffset += sizeOfNewDataChunk

                # Adjust the number of remaining data bytes
                nrOfRemainingDataBytes -= sizeOfNewDataChunk

    def getPacketData(self) -> list:
        """Returns the data stored in the packet's data chunks."""

        data = []
        for chunk in self.dataChunks:
            data += chunk.data
        return data

    def getPacketEOP(self) -> Union[STAR_EOP_TYPE, None]:
        """Returns the end of packet marker for this packet.

        This is the end of packet marker of the last data chunk in the packet's list of `STAR_system.data_chunk.DataChunk` objects.\n

        Returns None if the Packet does not have any data chunks.
        """

        if len(self.dataChunks) > 0:
            return self.dataChunks[-1].eop
        else:
            return None

    def getPacketLength(self) -> int:
        """Returns the length of the packet.\n

        The length is the sum of the length of the list containing the address bytes and the length of each
        DataChunk in the packet's internal list of `STAR_system.data_chunk.DataChunk` objects.
        """

        length = 0
        for dataChunk in self.dataChunks:
            length += len(dataChunk.data)

        if self.address is not None:
            length += len(self.address)

        return length

    def setPacketEOP(self, eopMarker):
        """Sets the end of packet marker for the packet.

        This is the same as the end of packet marker in the last DataChunk of the packet.

        Args:\n
            eopMarker (STAR_system.STAR_enums.STAR_EOP_TYPE): Apart from the enum values, None is also valid.

        Raises:\n
            STARAPIError:\n
                The packet has no data chunks.\n
        """

        if len(self.dataChunks) == 0:
            raise STARAPIError("Cannot set EOP of empty packet.")

        if isinstance(eopMarker, STAR_EOP_TYPE) is False and eopMarker is not None:
            raise TypeError("eop must be None or STAR_EOP_TYPE.")

        # Set the eop marker of the last data chunk
        self.dataChunks[-1].eop = eopMarker


