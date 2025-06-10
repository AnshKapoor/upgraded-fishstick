"""Represents a data chunk.

Brief:\n
    Represents a data chunk.

Copyright:\n
    2022 STAR-Dundee Ltd
"""

from gspy_egse.gui.STAR_system.STAR_enums import STAR_EOP_TYPE


class DataChunk(object):

    """Represents a chunk of contiguous SpaceWire data, within a single packet.
    
    Attributes:\n
        data (list of ints): The data buffer.
        isStart (bool): Whether the chunk of data represents the start of a new packet.
        eop (STAR_system.STAR_enums.STAR_EOP_TYPE): The type of end packet marker this data chunk has. This parameter is
        optional and defaults to None (`STAR_system.STAR_enums.STAR_EOP_TYPE.STAR_EOP_TYPE_NONE`).
    """

    # The maximum size (length) of the data stored in each DataChunk
    MAX_CHUNK_SIZE = 0xFFFC

    def __init__(self, data, isStart, eop=None):
        """Constructor:\n
            Initialises a DataChunk object.

        Args:\n
            See `STAR_system.data_chunk.DataChunk` class attributes.

        Raises:\n
            TypeError:\n
                data was not a list.\n
                isStart was not a bool.\n
                eop was not None or a STAR_EOP_TYPE.\n
            ValueError:\n
                length of data (list) exceeds the maximum permitted length of a DataChunk.
        """

        if isinstance(data, list) is False:
            raise TypeError("data must be a list.")
        if isinstance(isStart, bool) is False:
            raise TypeError("isStart must be bool.")
        if eop is not None and isinstance(eop, STAR_EOP_TYPE) is False:
            raise TypeError("eop must be None or STAR_EOP_TYPE.")
        if len(data) > self.MAX_CHUNK_SIZE:
            raise ValueError("data must contain at most 65532 elements.")

        self.data = data
        self.isStart = isStart

        self.dataBytes = bytes(self.data)
        
        if eop is None:
            self.eop = STAR_EOP_TYPE.STAR_EOP_TYPE_NONE
        else:
            self.eop = eop


