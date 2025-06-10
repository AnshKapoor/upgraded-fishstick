""" Functions provided by the CCSDS/SPP/TF packet library.

Brief:\n
    Functions provided by the CCSDS/SPP/TF packet library.

Copyright:\n
    2021 STAR-Dundee Ltd.
"""

from ctypes import *
import os
from typing import Tuple, Union

import numpy as np

from gspy_egse.gui.STAR_system import CCSDS_SPP_TF_LIB, CCSDS_SPP_TF_API_LIB_LOAD_ERROR_STR
from gspy_egse.gui.STAR_system.STAR_exceptions import STARAPIError
from gspy_egse.gui.STAR_system.ccsds_spp_tf_enums import CCSDS_SPP_PACKET_TYPE, CCSDS_SPP_STATUS
from gspy_egse.gui.STAR_system.ccsds_spp_tf_structs_external import CCSDS_TF_M_PDU_PACKET_EXTERNAL, CCSDS_SPP_PACKET_EXTERNAL
from gspy_egse.gui.STAR_system.ccsds_spp_tf_structs_internal import CCSDS_SPP_PACKET, CCSDS_TF_M_PDU_PACKET

sysType = os.name
if sysType == "nt":
    try:
        ccsds_spp_tf_lib = windll.LoadLibrary(CCSDS_SPP_TF_LIB)
    except Exception:
        ccsds_spp_tf_lib = None
        print(CCSDS_SPP_TF_API_LIB_LOAD_ERROR_STR)
elif sysType == "posix":
    try:
        ccsds_spp_tf_lib = cdll.LoadLibrary(CCSDS_SPP_TF_LIB)
    except Exception:
        ccsds_spp_tf_lib = None
        print(CCSDS_SPP_TF_API_LIB_LOAD_ERROR_STR)


def PopulateExternalTFPacketStructure(internalTFPacketStructure) -> CCSDS_TF_M_PDU_PACKET_EXTERNAL:
    """ Function used to populate the contents of a CCSDS_TF_M_PDU_PACKET_EXTERNAL object
    with the contents of the CCSDS_TF_M_PDU_PACKET passed in as an input parameter.
    Returns an `STAR_system.ccsds_spp_tf_structs_external.CCSDS_TF_M_PDU_PACKET_EXTERNAL` object.

    Args:\n
        internalTFPacketStructure (`STAR_system.ccsds_spp_tf_structs_internal.CCSDS_TF_M_PDU_PACKET`): CCSDS TF packet structure.

    Raises:\n
        STARAPIError:\n
            Could not get encapsulation header bytes from internal CCSDS TF packet structure.\n
            Could not get insert zone bytes from internal CCSDS TF packet structure.\n
            Could not get data field bytes from internal CCSDS TF packet structure.\n
        TypeError:\n
            internalTFPacketStructure was not a CCSDS_TF_M_PDU_PACKET.\n
    """

    if isinstance(internalTFPacketStructure, CCSDS_TF_M_PDU_PACKET) is False:
        raise TypeError("internalTFPacketStructure must be a CCSDS_TF_M_PDU_PACKET.")

    # Create external TF packet structure object
    externalPacketStructure = CCSDS_TF_M_PDU_PACKET_EXTERNAL()

    # Encapsulation header length
    externalPacketStructure.encapsulationHeader.length = internalTFPacketStructure.encapsulationHeader.length

    # Encapsulation header bytes (only retrieve if there is something to retrieve)
    if externalPacketStructure.encapsulationHeader.length > 0 and \
            internalTFPacketStructure.encapsulationHeader.pHeader is not None:

        # Get encapsulation header pointer and cast it to byte ptr
        internalTFPacketEncapsHeaderPtr = cast(internalTFPacketStructure.encapsulationHeader.pHeader, POINTER(c_uint8))

        # Internal structure header array
        try:
            headerBytes = list(np.ctypeslib.as_array(internalTFPacketEncapsHeaderPtr,
                                                     (externalPacketStructure.encapsulationHeader.length,)).tobytes())
        except TypeError as err:
            raise STARAPIError("Could not get encapsulation header bytes from internal"
                               "CCSDS_SPP_ENCAPS_HEADER structure: " + str(err))

        # Assign header bytes
        externalPacketStructure.encapsulationHeader.header = headerBytes

    # Primary header fields

    # Version number
    externalPacketStructure.primaryHeader.versionNumber = internalTFPacketStructure.primaryHeader.versionNumber

    # Spacecraft ID
    externalPacketStructure.primaryHeader.spaceCraftId = internalTFPacketStructure.primaryHeader.spaceCraftId

    # Virtual channel ID
    externalPacketStructure.primaryHeader.virtualChannelId = internalTFPacketStructure.primaryHeader.virtualChannelId

    # Virtual channel frame count
    externalPacketStructure.primaryHeader.virtualChannelFrameCount =\
        internalTFPacketStructure.primaryHeader.virtualChannelFrameCount

    # Replay flag
    externalPacketStructure.primaryHeader.replayFlag = \
        bool(internalTFPacketStructure.primaryHeader.replayFlag)

    # Virtual channel frame count usage flag
    externalPacketStructure.primaryHeader.virtualChannelFrameCountUsageFlag =\
        bool(internalTFPacketStructure.primaryHeader.virtualChannelFrameCount)

    # Reserved spare bits
    externalPacketStructure.primaryHeader.reservedSpareBits = internalTFPacketStructure.primaryHeader.reservedSpareBits

    # Virtual channel frame count cycle
    externalPacketStructure.primaryHeader.virtualChannelFrameCountCycle = \
        internalTFPacketStructure.primaryHeader.virtualChannelFrameCountCycle

    # Error control word
    externalPacketStructure.primaryHeader.errorControl = \
        internalTFPacketStructure.primaryHeader.errorControl

    # Internal structure insert zone

    # Insert zone length
    externalPacketStructure.insertZone.length = internalTFPacketStructure.insertZone.length

    # Get the insert zone bytes (is there is something to get)
    if externalPacketStructure.insertZone.length > 0 and \
            internalTFPacketStructure.insertZone.pData is not None:

        internalTFPacketInsertZoneDataPtr = cast(internalTFPacketStructure.insertZone.pData, POINTER(c_uint8))

        # Insert zone bytes
        try:
            insertZoneBytes = list(np.ctypeslib.as_array(internalTFPacketInsertZoneDataPtr,
                                                     (externalPacketStructure.insertZone.length,)).tobytes())
        except TypeError as err:
            raise STARAPIError(
                "Could not get insert zone bytes from internal CCSDS_TF_INSERT_ZONE structure: " + str(err))

        externalPacketStructure.insertZone.data = insertZoneBytes

    # Data field header reserved field
    externalPacketStructure.dataField.header.reserved = internalTFPacketStructure.dataField.header.reserved

    # Data field header first header pointer field
    externalPacketStructure.dataField.header.firstHeaderPointer =\
        internalTFPacketStructure.dataField.header.firstHeaderPointer

    # Data field data
    if internalTFPacketStructure.dataField.pData is not None:

        # Get the data field pointer and cast it to byte pointer
        internalTFPacketDataPtr = cast(internalTFPacketStructure.dataField.pData, POINTER(c_uint8))

        # Data field bytes
        try:
            dataFieldBytes = list(np.ctypeslib.as_array(internalTFPacketDataPtr, (2040,)).tobytes())
        except TypeError as err:
            raise STARAPIError(
                "Could not get data field bytes from internal CCSDS_SPP_ENCAPS_HEADER structure: " + str(err))

        externalPacketStructure.dataField.data = dataFieldBytes

    # Operational control field
    externalPacketStructure.operationalControlField = internalTFPacketStructure.operationalControlField

    # Frame error control field
    externalPacketStructure.frameErrorControlField = internalTFPacketStructure.frameErrorControlField

    return externalPacketStructure

def PopulateExternalCCSDS_SPPPacket(internalCCSDS_SPP_packet) -> CCSDS_SPP_PACKET_EXTERNAL:
    """ Function used to populate the contents of a CCSDS_SPP_PACKET_EXTERNAL object
        with the contents of the CCSDS_SPP_PACKET passed in as an input parameter.
        Returns an CCSDS_SPP_PACKET_EXTERNAL object.

        Args:\n
            internalCCSDS_SPP_packet (STAR_system.ccsds_spp_tf_structs_internal.CCSDS_SPP_PACKET): CCSDS/SPP packet structure.

        Raises:\n
            STARAPIError:\n
                Could not get encapsulation header bytes from internal CCSDS/SPP packet structure.\n
                Could not get data field bytes from internal CCSDS/SPP packet structure.\n
            TypeError:\n
                internalCCSDS_SPP_packet was not a CCSDS_SPP_PACKET.
    """

    if isinstance(internalCCSDS_SPP_packet, CCSDS_SPP_PACKET) is False:
        raise TypeError("internalCCSDS_SPP_packet must be a CCSDS_SPP_PACKET.")

    # Create external TF packet structure object
    externalPacketStructure = CCSDS_SPP_PACKET_EXTERNAL()

    # Encapsulation header length
    externalPacketStructure.encapsulationHeader.length = internalCCSDS_SPP_packet.encapsulationHeader.length

    # Encapsulation header bytes (only retrieve if there is something to retrieve)
    if externalPacketStructure.encapsulationHeader.length > 0 and\
            internalCCSDS_SPP_packet.encapsulationHeader.pHeader is not None:

        # Get encapsulation header pointer and cast it to byte ptr
        internalPacketStructureEncapsHeaderPtr = cast(internalCCSDS_SPP_packet.encapsulationHeader.pHeader,
                                                      POINTER(c_uint8))

        # Internal structure header array
        try:
            headerBytes = list(np.ctypeslib.as_array(internalPacketStructureEncapsHeaderPtr,
                                                     (externalPacketStructure.encapsulationHeader.length,)).tobytes())

        except TypeError as err:
            raise STARAPIError("Could not get encapsulation header bytes from internal"
                               "CCSDS_SPP_ENCAPS_HEADER structure: " + str(err))

        # Assign header bytes
        externalPacketStructure.encapsulationHeader.header = headerBytes

    # Primary header fields

    # Version number
    externalPacketStructure.primaryHeader.versionNumber = internalCCSDS_SPP_packet.primaryHeader.versionNumber

    # Packet type
    externalPacketStructure.primaryHeader.type = internalCCSDS_SPP_packet.primaryHeader.type

    # Internal packet type
    externalPacketStructure.primaryHeader.packetType = internalCCSDS_SPP_packet.primaryHeader.packetType

    # Secondary header flag
    externalPacketStructure.primaryHeader.secondaryHeaderFlag =\
        bool(internalCCSDS_SPP_packet.primaryHeader.secondaryHeaderFlag)

    # APID
    externalPacketStructure.primaryHeader.APID = internalCCSDS_SPP_packet.primaryHeader.APID

    # Sequence flags
    externalPacketStructure.primaryHeader.sequenceFlags = internalCCSDS_SPP_packet.primaryHeader.sequenceFlags

    # Sequence count
    externalPacketStructure.primaryHeader.sequenceCount = internalCCSDS_SPP_packet.primaryHeader.sequenceCount

    # Data field length
    externalPacketStructure.primaryHeader.dataFieldLength = internalCCSDS_SPP_packet.primaryHeader.dataFieldLength

    # Data field
    # Get the secondary header bytes first
    if externalPacketStructure.primaryHeader.secondaryHeaderFlag is True:

        # Check that the pointer is valid
        if internalCCSDS_SPP_packet.dataField.pSecondaryHeader is not None:

            # Get secondary header pointer and cast it to byte ptr
            internalPacketStructureSecondaryHeaderPtr = cast(internalCCSDS_SPP_packet.dataField.pSecondaryHeader,
                                                             POINTER(c_uint8))

            # Internal structure data field bytes
            try:
                dataFieldBytes = list(np.ctypeslib.as_array(internalPacketStructureSecondaryHeaderPtr,
                                                         (externalPacketStructure.primaryHeader.dataFieldLength,)).tobytes())
            except TypeError as err:
                raise STARAPIError(
                    "Could not get data field bytes from internal CCSDS_SPP_PACKET_DATA_FIELD structure: " + str(err))

            externalPacketStructure.dataField.secondaryHeader = dataFieldBytes
    else:

        # Check that the pointer is valid
        if internalCCSDS_SPP_packet.dataField.pUserData is not None:

            # Get user data bytes pointer and cast it to byte ptr
            internalPacketStructureUserDataPtr = cast(internalCCSDS_SPP_packet.dataField.pUserData, POINTER(c_uint8))

            # Internal structure data field bytes
            try:
                dataFieldBytes = list(np.ctypeslib.as_array(internalPacketStructureUserDataPtr,
                                                            (externalPacketStructure.primaryHeader.dataFieldLength,)).tobytes())
            except TypeError as err:
                raise STARAPIError(
                    "Could not get data field bytes from internal CCSDS_SPP_PACKET_DATA_FIELD structure: " + str(err))

            externalPacketStructure.dataField.userData = dataFieldBytes

    return externalPacketStructure

def CCSDS_SPP_CreatePacket(encapsulationHeaderBytes, packetType, secondaryHeaderFlag,
                           APID, sequenceFlags, sequenceCount, secondaryHeaderBytes, userDataFieldBytes) ->\
        Tuple[Union[list, None], Union[CCSDS_SPP_PACKET_EXTERNAL, None], CCSDS_SPP_STATUS]:
    """ Function used to create the raw packet byte buffer of the CCSDS/SPP packet.
        It will also populate the corresponding fields in the packet structure
        passed in as a parameter.
        Note: This function allocates memory (call to malloc() is performed inside)
        and it is then up to the user to free this memory by calling the
        CCSDS_SPP_FreeBuffer() function.

        Returns a tuple that has 3 elements\n
        1) a list of ints representing the raw packet bytes or None if the function fails.\n
        2) a `STAR_system.ccsds_spp_tf_structs_external.CCSDS_SPP_PACKET_EXTERNAL` object populated by this function or
        None if the function fails.\n
        3) status of the create packet operation : `STAR_system.ccsds_spp_tf_enums.CCSDS_SPP_STATUS`

        Args:\n
            encapsulationHeaderBytes (list of ints or None): List containing the encapsulation header bytes.
            packetType (STAR_system.ccsds_spp_tf_enums.CCSDS_SPP_PACKET_TYPE): Type of the CCSDS/SPP packet.
            secondaryHeaderFlag (bool): Whether the secondary header is present in the packet.
            APID (int): Application protocol identifier.
            sequenceFlags (int): Sequence flags.
            sequenceCount (int): sequenceCount
            secondaryHeaderBytes (list of ints): List containing the secondary header bytes.
            userDataFieldBytes (list of ints): List containing the user data (data field bytes).

        Raises:\n
            STARAPIError:\n
                The CCSDS/SPP/TF packet library could not be loaded.\n
                Could not populate external CCSDS/SPP packet structure.\n
            TypeError:\n
                Could not populate external CCSDS/SPP packet structure.\n
                encapsulationHeaderBytes was not a list.\n
                any element of encapsulationHeaderBytes was not an int.\n
                packetType was not a CCSDS_SPP_PACKET_TYPE.\n
                secondaryHeaderFlag was not a bool.\n
                APID was not an int.\n
                sequenceFlags was not an int.\n
                sequenceCount was not an int.\n
                secondaryHeaderBytes was not a list.\n
                any element of secondaryHeaderBytes was not an int.\n
                userDataFieldBytes was not a list.\n
                any element of userDataFieldBytes was not an int.\n
            ValueError:\n
                encapsulationHeaderBytes must contain between 1 and 65535 elements.\n
                length of the data field (secondary header length + user data length) must not exceed 65536.\n
    """

    # Protect against invalid CCSDS/SPP/TF packet library
    if ccsds_spp_tf_lib is None:
        raise STARAPIError(CCSDS_SPP_TF_API_LIB_LOAD_ERROR_STR)

    if isinstance(encapsulationHeaderBytes, list) is False and encapsulationHeaderBytes is not None:
        raise TypeError("encapsulationHeaderBytes must be a list or None.")

    if encapsulationHeaderBytes is not None:
        for encapsulationHeaderByte in encapsulationHeaderBytes:
            if type(encapsulationHeaderByte) != int:
                raise TypeError("every element in encapsulationHeaderBytes must be an int.")

    if isinstance(packetType, CCSDS_SPP_PACKET_TYPE) is False:
        raise TypeError("packetType must be a CCSDS_SPP_PACKET_TYPE object.")

    if type(secondaryHeaderFlag) != bool:
        raise TypeError("secondaryHeaderFlag must be a bool.")

    if type(APID) != int:
        raise TypeError("APID must be an int.")

    if APID < 0 or APID > 65535:
        raise ValueError("APID must be an integer between 0 and 65535.")

    if type(sequenceFlags) != int:
        raise TypeError("sequenceFlags must be an int.")

    if sequenceFlags < 0 or sequenceFlags > 255:
        raise ValueError("sequenceFlags must be an integer between 0 and 255.")

    if type(sequenceCount) != int:
        raise TypeError("sequenceCount must be an int.")

    if sequenceCount < 0 or sequenceCount > 65535:
        raise ValueError("sequenceCount must be an integer between 0 and 65535.")

    if isinstance(secondaryHeaderBytes, list) is False:
        raise TypeError("secondaryHeaderBytes must be a list.")

    for secondaryHeaderByte in secondaryHeaderBytes:
        if type(secondaryHeaderByte) != int:
            raise TypeError("every element in secondaryHeaderBytes must be an int.")

    if isinstance(userDataFieldBytes, list) is False:
        raise TypeError("userDataFieldBytes must be a list.")

    for userDataFieldByte in userDataFieldBytes:
        if type(userDataFieldByte) != int:
            raise TypeError("every element in userDataFieldBytes must be an int.")

    # Create pointer to packetStruct
    packetStruct = CCSDS_SPP_PACKET()
    pPacketStruct = pointer(packetStruct)

    # Get the encapsulation header length
    if encapsulationHeaderBytes is not None:
        encapsulationHeaderLength = len(encapsulationHeaderBytes)

        if encapsulationHeaderLength > 65535:
            raise ValueError("Maximum number of elements in the encapsulation header list is 65535.")
    else:
        encapsulationHeaderLength = 0

    # Get the length of the secondary header
    secondaryHeaderLength = len(secondaryHeaderBytes)

    # Get the data field length
    userDataFieldLength = len(userDataFieldBytes)

    # Calculate the length of the data field
    # Note: this is made up of the secondary header and the user data field
    packetDataFieldLength = secondaryHeaderLength + userDataFieldLength

    if packetDataFieldLength > 65536:
        raise ValueError("Length of the data field must not exceed 65536.")

    # Set up array that holds the encapsulation header bytes
    if encapsulationHeaderLength > 0 and encapsulationHeaderBytes is not None:
        cEncapsulationHeaderArray = (c_uint8 * encapsulationHeaderLength)()

        # Assign encapsulation header values
        for i in range(0, encapsulationHeaderLength):
            cEncapsulationHeaderArray[i] = encapsulationHeaderBytes[i]

        # Cast to pointer (for marshalling purposes)
        cEncapsulationHeaderArrayPointer = pointer(cEncapsulationHeaderArray)
    else:
        cEncapsulationHeaderArrayPointer = None

    # Set up array that holds the secondary header bytes
    cSecondaryHeaderArray = (c_uint8 * secondaryHeaderLength)()

    # Assign secondary header values
    for i in range(0, secondaryHeaderLength):
        cSecondaryHeaderArray[i] = secondaryHeaderBytes[i]

    # Cast to pointer (for marshalling purposes)
    cSecondaryHeaderArrayPointer = pointer(cSecondaryHeaderArray)

    # Set up array that holds the user data field bytes
    cUserDataFieldBytes = (c_uint8 * userDataFieldLength)()

    # Assign the user data field bytes
    for i in range(0, userDataFieldLength):
        cUserDataFieldBytes[i] = userDataFieldBytes[i]

    # Cast to pointer (for marshalling purposes)
    cUserDataFieldBytesPointer = pointer(cUserDataFieldBytes)

    # Create int variable to hold raw packet length (populated by the C function)
    rawPacketLength = c_uint32(0)
    pRawPacketLength = pointer(rawPacketLength)

    # Create int variable that will hold the status value
    statusVal = c_int32(0)
    pStatusVal = pointer(statusVal)

    # Set argument types and return type of the C function
    ccsds_spp_tf_lib.CCSDS_SPP_CreatePacket.argtypes = [POINTER(CCSDS_SPP_PACKET),
                                                        POINTER(c_uint8 * encapsulationHeaderLength), c_uint16,
                                                        CCSDS_SPP_PACKET_TYPE, c_uint8, c_uint16, c_uint8, c_uint16,
                                                        c_uint16, POINTER(c_uint8 * secondaryHeaderLength), c_uint16,
                                                        POINTER(c_uint8 * userDataFieldLength), POINTER(c_uint32),
                                                        POINTER(c_int32)]
    ccsds_spp_tf_lib.CCSDS_SPP_CreatePacket.restype = POINTER(c_ubyte)

    packet = ccsds_spp_tf_lib.CCSDS_SPP_CreatePacket(pPacketStruct, cEncapsulationHeaderArrayPointer,
                                                     c_uint16(encapsulationHeaderLength), packetType,
                                                     c_uint8(secondaryHeaderFlag), c_uint16(APID),
                                                     c_uint8(sequenceFlags), c_uint16(sequenceCount),
                                                     c_uint16(packetDataFieldLength), cSecondaryHeaderArrayPointer,
                                                     c_uint16(secondaryHeaderLength), cUserDataFieldBytesPointer,
                                                     pRawPacketLength, pStatusVal)

    # Convert int into CCSDS_SPP_STATUS enum
    status = CCSDS_SPP_STATUS(statusVal.value)

    if packet is None or rawPacketLength.value == 0 or status != CCSDS_SPP_STATUS.CCSDS_SPP_STATUS_SUCCESS:
        return None, None, status

    # Create a list containing the packet bytes
    packetList = [packet[i] for i in range(0, rawPacketLength.value)]

    try:
        externalPacketStruct = PopulateExternalCCSDS_SPPPacket(packetStruct)
    except (STARAPIError, TypeError):
        raise

    # Set argument types and return type of the C function
    ccsds_spp_tf_lib.CCSDS_SPP_FreeBuffer.argtypes = [c_void_p]
    ccsds_spp_tf_lib.CCSDS_SPP_FreeBuffer.restype = None

    # Free the memory that had been allocated by the CreatePacket function
    ccsds_spp_tf_lib.CCSDS_SPP_FreeBuffer(packet)

    return packetList, externalPacketStruct, status


def CCSDS_SPP_CreatePTPHeader(targetLogicalAddress, reservedByte, userAppByte) ->\
        Tuple[Union[list, None], CCSDS_SPP_STATUS]:
    """ Function used to create the PTP protocol header.

    Returns a tuple containing\n
    1) list of ints representing the PTP header bytes (or None if the function fails).\n
    2) status of the operation : `STAR_system.ccsds_spp_tf_enums.CCSDS_SPP_STATUS`.\n

    Args:\n
        targetLogicalAddress (int): The logical address of the target device.
        reservedByte (int): The reserved byte of the PTP header.
        userAppByte (int): the user application byte of the PTP header.

    Raises:\n
        STARAPIError:\n
            The CCSDS/SPP/TF packet library could not be loaded.\n
        TypeError:\n
            targetLogicalAddress was not an int.\n
            reservedByte was not an int.\n
            userAppByte was not an int.\n
        ValueError:\n
            targetLogicalAddress must be between 1 and 255.\n
            reservedByte must be between 1 and 255.\n
            userAppByte must be between 1 and 255.\n
    """

    # Protect against invalid CCSDS/SPP/TF packet library
    if ccsds_spp_tf_lib is None:
        raise STARAPIError(CCSDS_SPP_TF_API_LIB_LOAD_ERROR_STR)

    # Handle type errors
    if type(targetLogicalAddress) != int:
        raise TypeError("targetLogicalAddress must be an int.")

    if targetLogicalAddress < 0 or targetLogicalAddress > 255:
        raise ValueError("targetLogicalAddress must be between 1 and 255.")

    if type(reservedByte) != int:
        raise TypeError("reservedByte must be an int.")

    if reservedByte < 0 or reservedByte > 255:
        raise ValueError("reservedByte must be between 1 and 255.")

    if type(userAppByte) != int:
        raise TypeError("userAppByte must be an int.")

    if userAppByte < 0 or userAppByte > 255:
        raise ValueError("userAppByte must be between 1 and 255.")

    # Create int variable that will hold the status value
    statusVal = c_int32(0)
    pStatusVal = pointer(statusVal)

    # Set argument types and return type of the C function
    ccsds_spp_tf_lib.CCSDS_SPP_CreatePTPHeader.argtypes = [c_uint8, c_uint8, c_uint8, POINTER(c_int32)]
    ccsds_spp_tf_lib.CCSDS_SPP_CreatePTPHeader.restype = POINTER(c_ubyte)

    PTPHeader = ccsds_spp_tf_lib.CCSDS_SPP_CreatePTPHeader(targetLogicalAddress, reservedByte, userAppByte, pStatusVal)

    # Convert int into CCSDS_SPP_STATUS enum
    status = CCSDS_SPP_STATUS(statusVal.value)

    if PTPHeader is None or status != CCSDS_SPP_STATUS.CCSDS_SPP_STATUS_SUCCESS:
        return None, status

    return PTPHeader, status


def CCSDS_SPP_RetrievePacket(packet, retrievePTPHeader, encapsulationHeaderLength) ->\
        Tuple[Union[CCSDS_SPP_PACKET_EXTERNAL, None], CCSDS_SPP_STATUS]:
    """ Function used to receive/retrieve/interpret a CCSDS/SPP packet (from a list of bytes - representing
        the raw CCSDS/SPP packet).

        Returns a tuple containing\n
        1) a `STAR_system.ccsds_spp_tf_structs_external.CCSDS_SPP_PACKET_EXTERNAL` object
        (or None if the function fails).\n
        2) status of the operation : `STAR_system.ccsds_spp_tf_enums.CCSDS_SPP_STATUS`.\n

        Args:\n
            packet (list of bytes): List containing the raw packet bytes.
            retrievePTPHeader (bool): Whether the packet to be received has/hasn't got a PTP header.
            encapsulationHeaderLength (int): Length of the encapsulation header (if non-PTP header is used).

        Raises:\n
            STARAPIError:\n
                The CCSDS/SPP/TF packet library could not be loaded.\n
                Could not populate external CCSDS_SPP packet structure.\n

            TypeError:\n
                packet was not a list.\n
                any element in packet was not an int.\n
                retrievePTPHeader was not a bool.\n
                encapsulationHeaderLength was not an int.\n
    """

    # Protect against invalid CCSDS/SPP/TF packet library
    if ccsds_spp_tf_lib is None:
        raise STARAPIError(CCSDS_SPP_TF_API_LIB_LOAD_ERROR_STR)

    # Handle type errors
    if isinstance(packet, list) is False:
        raise TypeError("packet must be a list.")

    for packetByte in packet:
        if type(packetByte) != int:
            raise TypeError("every element of the packet list must be an int.")

    if type(retrievePTPHeader) != bool:
        raise TypeError("retrievePTPHeader must be a bool.")

    if type(encapsulationHeaderLength) != int:
        raise TypeError("encapsulationHeaderLength must be an int.")

    # Get the length of the packet
    packetLength = len(packet)

    # Create array that holds the packet bytes
    cPacketArray = (c_uint8 * packetLength)()

    # Assign packet values
    for k in range(0, packetLength):
        cPacketArray[k] = packet[k]

    # Cast array of packets to pointer (for marshalling purposes)
    cPacketArrayPointer = pointer(cPacketArray)

    # Create int variable that will hold the status value
    statusVal = c_int32(0)
    pStatusVal = pointer(statusVal)

    # Set argument types and return type of the C function
    ccsds_spp_tf_lib.CCSDS_SPP_RetrievePacket.argtypes = [POINTER(c_uint8 * packetLength), c_uint8, c_uint16,
                                                          POINTER(c_int32)]
    ccsds_spp_tf_lib.CCSDS_SPP_RetrievePacket.restype = CCSDS_SPP_PACKET

    CCSDS_SPP_packet = ccsds_spp_tf_lib.CCSDS_SPP_RetrievePacket(cPacketArrayPointer, c_uint8(retrievePTPHeader),
                                                                 c_uint16(encapsulationHeaderLength), pStatusVal)

    # Convert int into CCSDS_SPP_STATUS enum
    status = CCSDS_SPP_STATUS(statusVal.value)

    if CCSDS_SPP_packet is None or status != CCSDS_SPP_STATUS.CCSDS_SPP_STATUS_SUCCESS:
        return None, status

    try:
        CCSDS_SPP_packet_external = PopulateExternalCCSDS_SPPPacket(CCSDS_SPP_packet)
    except (STARAPIError, TypeError):
        raise

    return CCSDS_SPP_packet_external, status

def CCSDS_SPP_GetPTPHeaderLengthBytes() -> int:
    """Function used to retrieve and return the size of the PTP protocol header.

        Raises:\n
            STARAPIError:\n
                The CCSDS/SPP/TF packet library could not be loaded.\n
    """

    # Protect against invalid CCSDS/SPP/TF packet library
    if ccsds_spp_tf_lib is None:
        raise STARAPIError(CCSDS_SPP_TF_API_LIB_LOAD_ERROR_STR)

    # Set argument types and return type of the C function
    ccsds_spp_tf_lib.CCSDS_SPP_GetPTPHeaderLengthBytes.argtypes = []
    ccsds_spp_tf_lib.CCSDS_SPP_GetPTPHeaderLengthBytes.restype = c_uint8

    PTPHeaderLength = ccsds_spp_tf_lib.CCSDS_SPP_GetPTPHeaderLengthBytes()

    return PTPHeaderLength


def CCSDS_SPP_GetPrimaryHeaderLengthBytes() -> int:
    """Function used to retrieve and return the size of the primary header (in any CCSDS/SPP packet).

        Raises:\n
            STARAPIError:\n
                The CCSDS/SPP/TF packet library could not be loaded.\n
    """

    # Protect against invalid CCSDS/SPP/TF packet library
    if ccsds_spp_tf_lib is None:
        raise STARAPIError(CCSDS_SPP_TF_API_LIB_LOAD_ERROR_STR)

    # Set argument types and return type of the C function
    ccsds_spp_tf_lib.CCSDS_SPP_GetPrimaryHeaderLengthBytes.argtypes = []
    ccsds_spp_tf_lib.CCSDS_SPP_GetPrimaryHeaderLengthBytes.restype = c_uint8

    primaryHeaderLength = ccsds_spp_tf_lib.CCSDS_SPP_GetPrimaryHeaderLengthBytes()

    return primaryHeaderLength


def CCSDS_SPP_GetTelecommandSecondaryHeaderLengthBytes() -> int:
    """Function used to retrieve and return the size of the secondary header of any Telecommand type CCSDS/SPP packet.

        Raises:\n
            STARAPIError:\n
                The CCSDS/SPP/TF packet library could not be loaded.\n
    """

    # Protect against invalid CCSDS/SPP/TF packet library
    if ccsds_spp_tf_lib is None:
        raise STARAPIError(CCSDS_SPP_TF_API_LIB_LOAD_ERROR_STR)

    # Set argument types and return type of the C function
    ccsds_spp_tf_lib.CCSDS_SPP_GetTelecommandSecondaryHeaderLengthBytes.argtypes = []
    ccsds_spp_tf_lib.CCSDS_SPP_GetTelecommandSecondaryHeaderLengthBytes.restype = c_uint8

    telecommandPacketSecondaryHeaderLength = ccsds_spp_tf_lib.CCSDS_SPP_GetTelecommandSecondaryHeaderLengthBytes()

    return telecommandPacketSecondaryHeaderLength


def CCSDS_SPP_CheckAPID(packetType, APID) -> CCSDS_SPP_STATUS:
    """Function used to check the validity/correctness of an APID.
    Returns True if the APID is valid, False otherwise.

    Args:\n
        packetType (STAR_system.ccsds_spp_tf_enums.CCSDS_SPP_PACKET_TYPE): Type of the CCSDS/SPP packet.
        APID (int): APID of the CCSDS/SPP packet to be checked.

    Raises:\n
        STARAPIError:\n
            The CCSDS/SPP/TF packet library could not be loaded.\n

        TypeError:\n
            packetType was not a CCSDS_SPP_PACKET_TYPE.\n
            APID was not an int.\n
    """

    # Protect against invalid CCSDS/SPP/TF packet library
    if ccsds_spp_tf_lib is None:
        raise STARAPIError(CCSDS_SPP_TF_API_LIB_LOAD_ERROR_STR)

    # Handle type errors
    if isinstance(packetType, CCSDS_SPP_PACKET_TYPE) is False:
        raise TypeError("packetType must be a CCSDS_SPP_PACKET_TYPE.")

    if type(APID) != int:
        raise TypeError("APID must be an int.")

    # Set argument types and return type of the C function
    ccsds_spp_tf_lib.CCSDS_SPP_CheckAPID.argtypes = [CCSDS_SPP_PACKET_TYPE, c_uint16]
    ccsds_spp_tf_lib.CCSDS_SPP_CheckAPID.restype = CCSDS_SPP_STATUS

    status = ccsds_spp_tf_lib.CCSDS_SPP_CheckAPID(packetType, APID)

    return status


def CCSDS_TF_CreateIdlePacket(packetSize) -> Tuple[Union[list, None], CCSDS_SPP_STATUS]:
    """Function used to create IDLE packets to fill remaining bytes of M PDU
    packets of a TF (Transfer Frame).

    Returns a tuple containing\n
    1) a list of ints containing the bytes of the idle packet.\n
    2) status of the operation : `STAR_system.ccsds_spp_tf_enums.CCSDS_SPP_STATUS`.\n

    Args:\n
        packetSize (int): Size of the idle packet to be created.

    Raises:\n
        STARAPIError:\n
            The CCSDS/SPP/TF packet library could not be loaded.\n
        TypeError:\n
            packetSize was not an int.\n
    """

    # Protect against invalid CCSDS/SPP/TF packet library
    if ccsds_spp_tf_lib is None:
        raise STARAPIError(CCSDS_SPP_TF_API_LIB_LOAD_ERROR_STR)

    # Handle type errors
    if type(packetSize) != int:
        raise TypeError("packetSize must be an int.")

    # Create int variable to hold raw packet length (populated by the C function)
    rawPacketLength = c_uint32(0)
    pRawPacketLength = pointer(rawPacketLength)

    # Create int variable that will hold the status value
    statusVal = c_int32(0)
    pStatusVal = pointer(statusVal)

    # Set argument types and return type of the C function
    ccsds_spp_tf_lib.CCSDS_TF_CreateIdlePacket.argtypes = [c_uint16, POINTER(c_uint32), POINTER(c_int32)]
    ccsds_spp_tf_lib.CCSDS_TF_CreateIdlePacket.restype = POINTER(c_ubyte)

    packet = ccsds_spp_tf_lib.CCSDS_TF_CreateIdlePacket(packetSize, pRawPacketLength, pStatusVal)

    # Convert int into CCSDS_SPP_STATUS enum
    status = CCSDS_SPP_STATUS(statusVal.value)

    if packet is None or rawPacketLength.value == 0 or status != CCSDS_SPP_STATUS.CCSDS_SPP_STATUS_SUCCESS:
        return None, status

    # Create a list containing the packet bytes
    packetList = [packet[i] for i in range(0, rawPacketLength.value)]

    # Set argument types and return type of the C function
    ccsds_spp_tf_lib.CCSDS_SPP_FreeBuffer.argtypes = [c_void_p]
    ccsds_spp_tf_lib.CCSDS_SPP_FreeBuffer.restype = None

    # Free the memory that had been allocated by the CCSDS_TF_CreateIdlePacket function
    ccsds_spp_tf_lib.CCSDS_SPP_FreeBuffer(packet)

    return packetList, status


def CCSDS_TF_CreatePackets(CCSDS_SPP_packets, encapsulationHeaderBytes, versionNumber, spaceCraftId,
                           virtualChannelId, virtualChannelFrameCount, replayFlag, virtualChannelFrameCountUsageFlag,
                           virtualChannelFrameCountCycle, frameHeaderErrorControlBytes,
                           insertZoneDataBytes, operationalControlBytes, frameErrorControlBytes) ->\
        Tuple[Union[list, None], CCSDS_SPP_STATUS]:
    """Function used to create an array of TF packets (in the form of byte arrays each).
    Returns a tuple containing\n
    1) a list of TF packets (each TF packet being a list of ints itself) or None if the function fails.\n
    2) status of the operation : `STAR_system.ccsds_spp_tf_enums.CCSDS_SPP_STATUS`.\n

    Args:\n
        CCSDS_SPP_packets (list of lists of bytes): List containing lists containing the packet bytes for each CCSDS/SPP packet.
        encapsulationHeaderBytes (list of ints or None): List containing the encapsulation header bytes. If no encapsulation header is to be used, pass in None.
        versionNumber (int): Version of the transfer frame.
        spaceCraftId (int): The ID of the spacecraft.
        virtualChannelId (int): Virtual channel ID.
        virtualChannelFrameCount (int): Current frame count of the virtual channel.
        replayFlag (int): Whether the TF packet is "Live" or "Replayed".
        virtualChannelFrameCountUsageFlag (int): Whether the virtual channel frame count values are used or not.
        virtualChannelFrameCountCycle (int): value of the virtual channel frame count cycle.
        frameHeaderErrorControlBytes (list of ints or None): Bytes forming the frame header error control field.
                                                     Note: This is optional so can be omitted by passing in None.
        insertZoneDataBytes (list of ints or None): List containing the insert zone data bytes.
                                            Note: This is optional so can be omitted by passing in None.
        operationalControlBytes (list of ints or None): List containing the operational control bytes.
                                            Note: This is optional so can be omitted by passing in None.
        frameErrorControlBytes (list of ints or None): List containing the frame error control bytes.
                                            Note: This is optional so can be omitted by passing in None.

    Raises:\n
        STARAPIError:\n
            The CCSDS/SPP/TF packet library could not be loaded.\n

        TypeError:\n
            CCSDS_SPP_packets was not a list.\n
            any element of CCSDS_SPP_packets was not a list.\n
            any element of the elements of CCSDS_SPP_packets was not an int.\n
            encapsulationHeaderBytes was not a list.\n
            any element of encapsulationHeaderBytes was not an int.\n
            versionNumber was not an int.\n
            spaceCraftId was not an int.\n
            virtualChannelId was not an int.\n
            virtualChannelFrameCount was not an int.\n
            replayFlag was not an int.\n
            virtualChannelFrameCountUsageFlag was not an int.\n
            virtualChannelFrameCountCycle was not an int.\n
            frameHeaderErrorControlBytes was not a list or was not None.\n
            any element of the elements of frameHeaderErrorControlBytes was not an int.\n
            insertZoneDataBytes was not a list or was not None.\n
            any element of the elements of insertZoneDataBytes was not an int.\n
            operationalControlBytes was not a list or was not None.\n
            any element of the elements of operationalControlBytes was not an int.\n
            frameErrorControlBytes was not a list or was not None.\n
            any element of the elements of frameErrorControlBytes was not an int.\n

        ValueError:\n
            versionNumber must be a positive integer between 0 and 255.\n
            spaceCraftId must be a positive integer between 0 and 255.\n
            virtualChannelId must be a positive integer between 0 and 255.\n
            replayFlag must either be 0 or 1.\n
            virtualChannelFrameCountUsageFlag must either be 0 or 1.\n
            Length of frameHeaderErrorControlBytes list is not 2.\n
            Length of the operationalControlBytes list is not 4.\n
            Length of the frameErrorControlBytes list is not 2.\n
    """

    # Protect against invalid CCSDS/SPP/TF packet library
    if ccsds_spp_tf_lib is None:
        raise STARAPIError(CCSDS_SPP_TF_API_LIB_LOAD_ERROR_STR)

    # Handle type errors
    if isinstance(CCSDS_SPP_packets, list) is False:
        raise TypeError("CCSDS_SPP_packets must be a list.")

    for CCSDS_SPP_packet in CCSDS_SPP_packets:
        if isinstance(CCSDS_SPP_packet, list) is False:
            raise TypeError("every element in CCSDS_SPP_packets must be a list.")
        for packetByte in CCSDS_SPP_packet:
            if type(packetByte) != int:
                raise TypeError("every element of each individual list must be an int.")

    if isinstance(encapsulationHeaderBytes, list) is False and encapsulationHeaderBytes is not None:
        raise TypeError("encapsulationHeaderBytes must be a list or None.")

    if encapsulationHeaderBytes is not None:
        for encapsulationHeaderByte in encapsulationHeaderBytes:
            if type(encapsulationHeaderByte) != int:
                raise TypeError("every element in encapsulationHeaderBytes must be an int.")

    if type(versionNumber) != int:
        raise TypeError("versionNumber must be an int.")

    if type(spaceCraftId) != int:
        raise TypeError("spaceCraftId must be an int.")

    if type(virtualChannelId) != int:
        raise TypeError("virtualChannelId must be an int.")

    if type(virtualChannelFrameCount) != int:
        raise TypeError("virtualChannelFrameCount must be an int.")

    if type(replayFlag) != int:
        raise TypeError("replayFlag must be an int.")

    if type(virtualChannelFrameCountUsageFlag) != int:
        raise TypeError("virtualChannelFrameCountUsageFlag must be an int.")

    if type(virtualChannelFrameCountCycle) != int:
        raise TypeError("virtualChannelFrameCountCycle must be an int.")

    if isinstance(frameHeaderErrorControlBytes, list) is False and frameHeaderErrorControlBytes is not None:
        raise TypeError("frameHeaderErrorControlBytes must be a list or None.")

    if frameHeaderErrorControlBytes is not None:
        for frameHeaderErrorControlByte in frameHeaderErrorControlBytes:
            if type(frameHeaderErrorControlByte) != int:
                raise TypeError("every element in frameHeaderErrorControlBytes must be an int.")

    if isinstance(insertZoneDataBytes, list) is False and insertZoneDataBytes is not None:
        raise TypeError("insertZoneDataBytes must be a list or None.")

    if insertZoneDataBytes is not None:
        for insertZoneDataByte in insertZoneDataBytes:
            if type(insertZoneDataByte) != int:
                raise TypeError("every element in insertZoneDataBytes must be an int.")

    if isinstance(operationalControlBytes, list) is False and operationalControlBytes is not None:
        raise TypeError("insertZoneDataBytes must be a list or None.")

    if operationalControlBytes is not None:
        for operationalControlByte in operationalControlBytes:
            if type(operationalControlByte) != int:
                raise TypeError("every element in operationalControlBytes must be an int.")

    if isinstance(frameErrorControlBytes, list) is False and frameErrorControlBytes is not None:
        raise TypeError("frameErrorControlBytes must be a list or None.")

    if frameErrorControlBytes is not None:
        for frameErrorControlByte in frameErrorControlBytes:
            if type(frameErrorControlByte) != int:
                raise TypeError("every element in frameErrorControlBytes must be an int.")

    # Handle value errors
    if versionNumber < 0 or versionNumber > 255:
        raise ValueError("versionNumber must be between 0 and 255.")

    if spaceCraftId < 0 or spaceCraftId > 255:
        raise ValueError("spaceCraftId must be between 0 and 255.")

    if virtualChannelId < 0 or virtualChannelId > 255:
        raise ValueError("virtualChannelId must be between 0 and 255.")

    if replayFlag not in [0, 1]:
        raise ValueError("replayFlag must be either 0 or 1.")

    if virtualChannelFrameCountUsageFlag not in [0, 1]:
        raise ValueError("virtualChannelFrameCountUsageFlag must be either 0 or 1.")

    if virtualChannelFrameCountCycle < 0 or virtualChannelFrameCountCycle > 255:
        raise ValueError("virtualChannelFrameCountCycle must be between 0 and 255.")

    # Get the number of CCSDS/SPP packets
    numberOfPackets = len(CCSDS_SPP_packets)

    # Create array that will hold the arrays
    # Note: Each element is an array of bytes
    cPacketArray = (POINTER(c_uint8) * numberOfPackets)()

    # Create array of packet lengths
    packetLengthsArray = (c_uint32 * numberOfPackets)()

    for k in range(0, numberOfPackets):

        # Get current packet
        packet = CCSDS_SPP_packets[k]

        # Get the length of the current packet
        packetLength = len(packet)

        # Save the length
        packetLengthsArray[k] = packetLength

        # Create array that holds the packet bytes
        cPacket = (c_uint8 * packetLength)()

        # Assign packet byte values
        for i in range(0, packetLength):
            cPacket[i] = packet[i]

        # Save this array
        cPacketArray[k] = cPacket

    # Cast array of packets to pointer (for marshalling purposes)
    ccPacketArray = pointer(cPacketArray)

    # Cast array of packet lengths to pointer (for marshalling purposes)
    cPacketLengthsArray = pointer(packetLengthsArray)

    # Get the encapsulation header length
    if encapsulationHeaderBytes is not None:
        encapsulationHeaderLength = len(encapsulationHeaderBytes)
    else:
        encapsulationHeaderLength = 0

    # Set up array that holds the encapsulation header bytes
    if encapsulationHeaderLength > 0 and encapsulationHeaderBytes is not None:
        cEncapsulationHeaderArray = (c_uint8 * encapsulationHeaderLength)()

        # Assign encapsulation header values
        for i in range(0, encapsulationHeaderLength):
            cEncapsulationHeaderArray[i] = encapsulationHeaderBytes[i]

        # Cast to pointer (for marshalling purposes)
        cEncapsulationHeaderArrayPointer = pointer(cEncapsulationHeaderArray)
    else:
        cEncapsulationHeaderArrayPointer = None

    # Create int variable to hold virtual channel frame count
    newVirtualChannelFrameCount = c_uint32(virtualChannelFrameCount)
    pNewVirtualChannelFrameCount = pointer(newVirtualChannelFrameCount)

    # Get the length of the frame header error control
    if frameHeaderErrorControlBytes is not None:
        frameHeaderErrorControlLength = len(frameHeaderErrorControlBytes)

        if frameHeaderErrorControlLength != 2:
            raise ValueError("Frame header error control bytes list must contain exactly 2 elements.")

    else:
        frameHeaderErrorControlLength = 0

    # Create array to hold frame header error byte values
    if frameHeaderErrorControlLength > 0 and frameHeaderErrorControlBytes is not None:
        # Set up array that holds the frame header error control bytes
        cFrameHeaderErrorControlArray = (c_uint8 * frameHeaderErrorControlLength)()

        # Assign frame header error control bytes
        for i in range(0, frameHeaderErrorControlLength):
            cFrameHeaderErrorControlArray[i] = frameHeaderErrorControlBytes[i]

        # Cast to pointer (for marshalling purposes)
        cFrameHeaderErrorControlArrayPointer = pointer(cFrameHeaderErrorControlArray)
    else:
        cFrameHeaderErrorControlArrayPointer = None

    # Check to see if insert zone data bytes are present/not
    if insertZoneDataBytes is not None:
        # Get the length of the insert zone data
        insertZoneDataLength = len(insertZoneDataBytes)
    else:
        insertZoneDataLength = 0

    # Create array to hold insert zone data byte values
    if insertZoneDataLength > 0 and insertZoneDataBytes is not None:
        # Set up array that holds the insert zone data bytes
        cInsertZoneDataArray = (c_uint8 * insertZoneDataLength)()

        # Assign insert zone data byte values
        for i in range(0, insertZoneDataLength):
            cInsertZoneDataArray[i] = insertZoneDataBytes[i]

        # Cast to pointer (for marshalling purposes)
        cInsertZoneDataArrayPointer = pointer(cInsertZoneDataArray)
    else:
        cInsertZoneDataArrayPointer = None

    # Check to see if operational control bytes are present/not
    if operationalControlBytes is not None:
        operationalControlBytesLength = len(operationalControlBytes)

        if operationalControlBytesLength != 4:
            raise ValueError("Operational control bytes list must contain exactly 4 elements.")
    else:
        operationalControlBytesLength = 0

    # Create array to hold operational control byte values
    if operationalControlBytesLength > 0 and operationalControlBytes is not None:

        # Set up array that holds the operational control bytes
        cOperationalControlBytesArray = (c_uint8 * operationalControlBytesLength)()

        # Assign operational control byte values
        for i in range(0, operationalControlBytesLength):
            cOperationalControlBytesArray[i] = operationalControlBytes[i]

        # Cast to pointer (for marshalling purposes)
        cOperationalControlBytesArrayPointer = pointer(cOperationalControlBytesArray)
    else:
        cOperationalControlBytesArrayPointer = None

    # Check to see if frame error control bytes are present/not
    if frameErrorControlBytes is not None:
        frameErrorControlBytesLength = len(frameErrorControlBytes)

        if frameErrorControlBytesLength != 2:
            raise ValueError("Frame error control bytes list must contain exactly 2 elements.")
    else:
        frameErrorControlBytesLength = 0

    # Create array to hold frame error control byte values
    if frameErrorControlBytesLength > 0 and frameErrorControlBytes is not None:

        # Set up array that holds the frame error control bytes
        cFrameErrorControlBytesArray = (c_uint8 * frameErrorControlBytesLength)()

        # Assign frame error control byte values
        for i in range(0, frameErrorControlBytesLength):
            cFrameErrorControlBytesArray[i] = frameErrorControlBytes[i]

        # Cast to pointer (for marshalling purposes)
        cFrameErrorControlBytesArrayPointer = pointer(cFrameErrorControlBytesArray)
    else:
        cFrameErrorControlBytesArrayPointer = None

    # Create int variable to hold the number of TF packets created (populated by the C function)
    numberOfTFPacketsCreated = c_uint16(0)
    pNumberOfTFPacketsCreated = pointer(numberOfTFPacketsCreated)

    # Create int variable to hold length of the TF packet created (populated by the C function)
    TFPacketLength = c_uint16(0)
    pTFPacketLength = pointer(TFPacketLength)

    # Create int variable that will hold the status value
    statusVal = c_int32(0)
    pStatusVal = pointer(statusVal)

    # Set argument types and return type of the C function
    ccsds_spp_tf_lib.CCSDS_TF_CreatePackets.argtypes = [POINTER(POINTER(c_uint8) * numberOfPackets),
                                                        POINTER(c_uint32 * numberOfPackets),
                                                        c_uint16, POINTER(c_uint8 * encapsulationHeaderLength),
                                                        c_uint16, c_uint8, c_uint8, c_uint8, POINTER(c_uint32), c_uint8,
                                                        c_uint8, c_uint8,
                                                        POINTER(c_uint8 * frameHeaderErrorControlLength),
                                                        POINTER(c_uint8 * insertZoneDataLength), c_uint8,
                                                        POINTER(c_uint16),
                                                        POINTER(c_uint16), POINTER(c_uint8 * 4), POINTER(c_uint8 * 2),
                                                        POINTER(c_int32)]
    ccsds_spp_tf_lib.CCSDS_TF_CreatePackets.restype = POINTER(POINTER(c_ubyte))

    packets = ccsds_spp_tf_lib.CCSDS_TF_CreatePackets(ccPacketArray, cPacketLengthsArray, numberOfPackets,
                                                      cEncapsulationHeaderArrayPointer, encapsulationHeaderLength,
                                                      versionNumber, spaceCraftId, virtualChannelId,
                                                      pNewVirtualChannelFrameCount, replayFlag,
                                                      virtualChannelFrameCountUsageFlag, virtualChannelFrameCountCycle,
                                                      cFrameHeaderErrorControlArrayPointer,
                                                      cInsertZoneDataArrayPointer, insertZoneDataLength,
                                                      pNumberOfTFPacketsCreated, pTFPacketLength,
                                                      cOperationalControlBytesArrayPointer,
                                                      cFrameErrorControlBytesArrayPointer, pStatusVal)

    # Convert int into CCSDS_SPP_STATUS enum
    status = CCSDS_SPP_STATUS(statusVal.value)

    # Number of TF packets created
    numberOfPacketsCreated = numberOfTFPacketsCreated.value

    # Length of each TF packet
    createdTFPacketLength = TFPacketLength.value

    if packets is None or numberOfPacketsCreated == 0 or createdTFPacketLength == 0\
            or status != CCSDS_SPP_STATUS.CCSDS_SPP_STATUS_SUCCESS:
        return None, status

    # Return the packets as a list of list of bytes
    createdPackets = []

    # Go through all packets
    for i in range(0, numberOfPacketsCreated):

        # Retrieve the current packet
        packetPointer = packets[i]

        # Create an empty list that will hold the bytes of the TF packet
        createdPacket = []

        # Append the packet bytes to the list
        for j in range(0, createdTFPacketLength):
            createdPacket.append(packetPointer[j])

        # Append the list of bytes to the list of lists
        createdPackets.append(createdPacket)

        # Set argument types and return type of the C function
        ccsds_spp_tf_lib.CCSDS_SPP_FreeBuffer.argtypes = [c_void_p]
        ccsds_spp_tf_lib.CCSDS_SPP_FreeBuffer.restype = None

        # Free the memory that had been allocated for the TF packet
        ccsds_spp_tf_lib.CCSDS_SPP_FreeBuffer(packetPointer)

    # Set argument types and return type of the C function
    ccsds_spp_tf_lib.CCSDS_SPP_FreeBuffer.argtypes = [c_void_p]
    ccsds_spp_tf_lib.CCSDS_SPP_FreeBuffer.restype = None

    # Free the memory that had been allocated for the TF packets
    ccsds_spp_tf_lib.CCSDS_SPP_FreeBuffer(packets)

    return createdPackets, status


def CCSDS_TF_RetrievePacket(packet, encapsulationHeaderLength, frameHeaderErrorControlPresent,
                            insertZoneDataLength, operationalControlFieldPresent, frameErrorControlFieldPresent) ->\
        Tuple[Union[CCSDS_TF_M_PDU_PACKET_EXTERNAL, None], CCSDS_SPP_STATUS]:
    """Function used to "receive"/reconstruct a TF (Transfer Frame) from an array of raw packet bytes.

    Returns a tuple containing 2 elements\n
    1) TF packet structure `STAR_system.ccsds_spp_tf_structs_external.CCSDS_TF_M_PDU_PACKET_EXTERNAL` or None if the function fails.\n
    2) status of the operation : `STAR_system.ccsds_spp_tf_enums.CCSDS_SPP_STATUS`.\n

    Args:\n
        packet (list of bytes): List containing the raw packet bytes.
        encapsulationHeaderLength (int): Length of the encapsulation header.
        frameHeaderErrorControlPresent (bool): Whether frame header error control field is present.
        insertZoneDataLength (int): Length of the insert zone data.
        operationalControlFieldPresent (bool): Whether operational control field is present.
        frameErrorControlFieldPresent (bool): Whether frame error control field is present.

    Raises:\n
        STARAPIError:\n
            The CCSDS/SPP/TF packet library could not be loaded.\n
            External TF packet structure could not be populated.\n

        TypeError:\n
            packet was not a list.\n
            any element in packet was not an int.\n
            encapsulationHeaderLength was not an int.\n
            frameHeaderErrorControlPresent was not a bool.\n
            insertZoneDataLength was not an int.\n
            operationalControlFieldPresent was not a bool.\n
            frameErrorControlFieldPresent was not a bool.\n
    """

    # Protect against invalid CCSDS/SPP/TF packet library
    if ccsds_spp_tf_lib is None:
        raise STARAPIError(CCSDS_SPP_TF_API_LIB_LOAD_ERROR_STR)

    # Handle type errors
    if isinstance(packet, list) is False:
        raise TypeError("packet must be a list.")

    for packetByte in packet:
        if type(packetByte) != int:
            raise TypeError("every element of the packet list must be an int.")

    if type(encapsulationHeaderLength) != int:
        raise TypeError("encapsulationHeaderLength must be an int.")

    if type(frameHeaderErrorControlPresent) != bool:
        raise TypeError("frameHeaderErrorControlPresent must be a bool.")

    if type(insertZoneDataLength) != int:
        raise TypeError("insertZoneDataLength must be an int.")

    if type(operationalControlFieldPresent) != bool:
        raise TypeError("operationalControlFieldPresent must be a bool.")

    if type(frameErrorControlFieldPresent) != bool:
        raise TypeError("frameErrorControlFieldPresent must be a bool.")

    # Get packet length
    packetLength = len(packet)

    # Check that the length of the packet is positive
    if packetLength > 0:
        # Set up array that holds the secondary header bytes
        cPacketBytes = (c_uint8 * packetLength)()

        # Assign packet byte values
        for i in range(0, packetLength):
            cPacketBytes[i] = packet[i]

        # Cast to pointer (for marshalling purposes)
        cPacketBytesPointer = pointer(cPacketBytes)
    else:
        cPacketBytesPointer = None

    # Create int variable that will hold the status value
    statusVal = c_int32(0)
    pStatusVal = pointer(statusVal)

    # Set argument types and return type of the C function
    ccsds_spp_tf_lib.CCSDS_TF_RetrievePacket.argtypes = [POINTER(c_uint8 * packetLength), c_uint16,
                                                         c_uint8, c_uint8, c_uint8, c_uint8, POINTER(c_int32)]
    ccsds_spp_tf_lib.CCSDS_TF_RetrievePacket.restype = CCSDS_TF_M_PDU_PACKET

    tfPacket = ccsds_spp_tf_lib.CCSDS_TF_RetrievePacket(cPacketBytesPointer, c_uint16(encapsulationHeaderLength),
                                                        c_uint8(frameHeaderErrorControlPresent),
                                                        c_uint8(insertZoneDataLength),
                                                        c_uint8(operationalControlFieldPresent),
                                                        c_uint8(frameErrorControlFieldPresent), pStatusVal)

    

    status = CCSDS_SPP_STATUS(statusVal.value)

    if tfPacket is None or status != CCSDS_SPP_STATUS.CCSDS_SPP_STATUS_SUCCESS:
        return None, status

    # Populate external TF packet structure
    try:
        tfPacketExternal = PopulateExternalTFPacketStructure(tfPacket)
    except (STARAPIError, TypeError):
        raise

    return tfPacketExternal, status
