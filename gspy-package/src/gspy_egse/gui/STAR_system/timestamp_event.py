"""Represents a timestamp on receipt of data on a link.

Brief:\n
    Represents a timestamp on receipt of data on a link.

Copyright:\n
    2022 STAR-Dundee Ltd
"""

import os
from ctypes import *
from typing import Tuple

from gspy_egse.gui.STAR_system import STAR_LIB, STAR_API_LIB_LOAD_ERROR_STR
from gspy_egse.gui.STAR_system.STAR_structures import STAR_TIMESTAMP_EVENT
from gspy_egse.gui.STAR_system.STAR_enums import STAR_TIMESTAMP_TYPE, STAR_TIMESTAMP_DIRECTION
from gspy_egse.gui.STAR_system.STAR_exceptions import STARAPIError

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


class TimestampEvent(object):
    """Represents a timestamp on receipt of data on a link.
    
    Attributes:\n
        systemClockFrequency (int): The system clock frequency of the device.
        typeOfData (STAR_system.STAR_enums.STAR_TIMESTAMP_TYPE): The type of data that the timestamp represents.
        direction (STAR_system.STAR_enums.STAR_TIMESTAMP_DIRECTION): Direction of the timestamp.
        startSyncPulseCount (int): The number of synchronisation pulses when the
            start of the packet was transmitted or received.
        startClockCycleCount (int): The number of clock cycles counted when the
            start of the packet was transmitted or received.
        startTotalCycleCount (int): The number of clock cycles counted when the
            last synchronisation pulse before the start of the packet was
            received.
        endSyncPulseCount (int): The number of synchronisation pulses when the end
            of the packet was transmitted or received.
        endClockCycleCount (int): The number of clock cycles counted when the end
            of the packet was transmitted or received.
        endTotalCycleCount (int): The number of clock cycles counted when the last
            synchronisation pulse before the end of the packet was received.
    """

    def __init__(self, systemClockFrequency, typeOfData, direction,
                 startSyncPulseCount, startClockCycleCount, startTotalCycleCount,
                 endSyncPulseCount, endClockCycleCount, endTotalCycleCount):
        """Constructor:\n
            Initialises a `STAR_system.timestamp_event.TimestampEvent` object.\n

        Args:\n
            See `STAR_system.timestamp_event.TimestampEvent` class attributes.

        Raises:\n
            TypeError:\n
                Any of the arguments is not of the type specified in the `STAR_system.timestamp_event.TimestampEvent` class attributes.
            ValueError:\n
                Any of the int arguments are negative.
        """

        if type(systemClockFrequency) != int:
            raise TypeError("systemClockFrequency must be int.")
        if isinstance(typeOfData, STAR_TIMESTAMP_TYPE) is False:
            raise TypeError("typeOfData must be STAR_TIMESTAMP_TYPE.")
        if isinstance(direction, STAR_TIMESTAMP_DIRECTION) is False:
            raise TypeError("direction must be STAR_TIMESTAMP_DIRECTION.")
        if type(startSyncPulseCount) != int:
            raise TypeError("startSyncPulseCount must be int.")
        if type(startClockCycleCount) != int:
            raise TypeError("startClockCycleCount must be int.")
        if type(startTotalCycleCount) != int:
            raise TypeError("startTotalCycleCount must be int.")
        if type(endSyncPulseCount) != int:
            raise TypeError("endSyncPulseCount must be int.")
        if type(endClockCycleCount) != int:
            raise TypeError("endClockCycleCount must be int.")
        if type(endTotalCycleCount) != int:
            raise TypeError("endTotalCycleCount must be int.")

        if systemClockFrequency < 0:
            raise ValueError("systemClockFrequency cannot be negative.")
        if startSyncPulseCount < 0:
            raise ValueError("startSyncPulseCount cannot be negative.")
        if startClockCycleCount < 0:
            raise ValueError("startClockCycleCount cannot be negative.")
        if startTotalCycleCount < 0:
            raise ValueError("startTotalCycleCount cannot be negative.")
        if endSyncPulseCount < 0:
            raise ValueError("endSyncPulseCount cannot be negative.")
        if endClockCycleCount < 0:
            raise ValueError("endClockCycleCount cannot be negative.")
        if endTotalCycleCount < 0:
            raise ValueError("endTotalCycleCount cannot be negative.")

        self.systemClockFrequency = systemClockFrequency
        self.typeOfData = typeOfData
        self.direction = direction
        self.startSyncPulseCount = startSyncPulseCount
        self.startClockCycleCount = startClockCycleCount
        self.startTotalCycleCount = startTotalCycleCount
        self.endSyncPulseCount = endSyncPulseCount
        self.endClockCycleCount = endClockCycleCount
        self.endTotalCycleCount = endTotalCycleCount

    def getCorrespondingStruct(self) -> STAR_TIMESTAMP_EVENT:
        """Converts and returns the `STAR_system.timestamp_event.TimestampEvent` object (itself) into a `STAR_system.STAR_structures.STAR_TIMESTAMP_EVENT` structure."""

        clockFrequency = c_uint32(self.systemClockFrequency)
        typeOfData = c_int32(self.typeOfData.value)
        direction = c_int32(self.direction.value)
        startSyncPulseCount = c_uint32(self.startSyncPulseCount)
        startClockCycleCount = c_uint32(self.startClockCycleCount)
        startTotalCycleCount = c_uint32(self.startTotalCycleCount)
        endSyncPulseCount = c_uint32(self.endSyncPulseCount)
        endClockCycleCount = c_uint32(self.endClockCycleCount)
        endTotalCycleCount = c_uint32(self.endTotalCycleCount)

        timestampStruct = STAR_TIMESTAMP_EVENT(clockFrequency, typeOfData, direction, startSyncPulseCount,
                                               startClockCycleCount, startTotalCycleCount,
                                               endSyncPulseCount, endClockCycleCount, endTotalCycleCount)

        return timestampStruct

    def getStartValue(self, syncPulseFrequency) -> Tuple[int, int]:
        """Gets and returns the timestamp value relating to the start of the data being
        received in whole seconds and the remainder in nanoseconds.

        Args:\n
            syncPulseFrequency (int): The frequency of synchronisation pulses in Hz.

        Raises:\n
            STARAPIError:\n
                The STAR-API library could not be loaded.\n
            TypeError:\
                syncPulseFrequency is not int.\n
            ValueError:\n
                syncPulseFrequency is negative.\n
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        if type(syncPulseFrequency) != int:
            raise TypeError("syncPulseFrequency must be int.")
        if syncPulseFrequency < 0:
            raise ValueError("syncPulseFrequency cannot be negative.")

        timestampStruct = self.getCorrespondingStruct()
        pTimestampStruct = pointer(timestampStruct)

        # Create pointer to int that will be passed in as parameter into the C library function
        seconds = c_uint32(0)
        pSeconds = pointer(seconds)

        # Create pointer to int that will be passed in as parameter into the C library function
        remainder = c_uint32(0)
        pRemainder = pointer(remainder)

        # Set argument types and return type of the C function
        star_lib.STAR_getTimestampEventStartValue.argtypes = [POINTER(STAR_TIMESTAMP_EVENT), c_uint32,
                                                              POINTER(c_uint32), POINTER(c_uint32)]
        star_lib.STAR_getTimestampEventStartValue.restype = None

        star_lib.STAR_getTimestampEventStartValue(pTimestampStruct, c_uint32(syncPulseFrequency),
                                                  pSeconds, pRemainder)

        return seconds.value, remainder.value

    def getEndValue(self, syncPulseFrequency) -> Tuple[int, int]:
        """Gets and returns the timestamp value relating to the end of the data being received
           in whole seconds and the remainder in nanoseconds.

        Args:\n
            syncPulseFrequency (int): The frequency of synchronisation pulses in Hz.

        Raises:\n
            STARAPIError:\n
                The STAR-API library could not be loaded.\n
            TypeError:\n
                syncPulseFrequency is not int.\n
            ValueError:\n
                syncPulseFrequency is negative.\n
        """

        # Make sure to protect against invalid STAR-API library
        if star_lib is None:
            raise STARAPIError(STAR_API_LIB_LOAD_ERROR_STR)

        if type(syncPulseFrequency) != int:
            raise TypeError("syncPulseFrequency must be int.")
        if syncPulseFrequency < 0:
            raise ValueError("syncPulseFrequency cannot be negative.")

        timestampStruct = self.getCorrespondingStruct()
        pTimestampStruct = pointer(timestampStruct)

        # Create pointer to int that will be passed in as parameter into the C library function
        seconds = c_uint32(0)
        pSeconds = pointer(seconds)

        # Create pointer to int that will be passed in as parameter into the C library function
        remainder = c_uint32(0)
        pRemainder = pointer(remainder)

        # Set argument types and return type of the C function
        star_lib.STAR_getTimestampEventEndValue.argtypes = [POINTER(STAR_TIMESTAMP_EVENT), c_uint32,
                                                              POINTER(c_uint32), POINTER(c_uint32)]
        star_lib.STAR_getTimestampEventEndValue.restype = None

        star_lib.STAR_getTimestampEventEndValue(pTimestampStruct, c_uint32(syncPulseFrequency),
                                                  pSeconds, pRemainder)

        return seconds.value, remainder.value
