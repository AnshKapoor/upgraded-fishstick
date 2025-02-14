"""Data structures used by CCSDS/SPP/TF packet library to efficiently pass data between
the Python API and the C API.

Brief:\n
    Data structures used by CCSDS/SPP/TF packet library to efficiently pass data between
    the Python API and the C API. These are used internally by the API and MUST NOT be used by the user.

Copyright:\n
    2021 STAR-Dundee Ltd.
"""

from ctypes import *

class CCSDS_SPP_ENCAPS_HEADER(Structure):
    """A structure used to describe an encapsulation header in the CCSDS/SPP/TF packet library.
    This structure should never be used to access the encapsulation header of a CCSDS/SPP/TF packet.
    See the equivalent `STAR_system.ccsds_spp_tf_structs_external.CCSDS_SPP_ENCAPS_HEADER_EXTERNAL` that users NEED to use.

    Attributes:\n
        pHeader: (unsigned char* / int) Array of bytes holding the encapsulation header.
        length: (unsigned short / int) Length of the encapsulation header.
    """

    _fields_ = [
        ("pHeader", POINTER(c_ubyte)),
        ("length", c_uint16)]

class M_PDU_PACKET(Structure):
    """A structure used to represent an M_PDU packet.
    This structure should never be used to access the contents of the M_PDU_PACKET part of a TF packet.

    Attributes:\n
        header: (unsigned short / int) Header of the M_PDU packet.
        headerSet: (unsigned char / int) Helper variable that assists in keeping track whether the header pointer has been set for this M_PDU packet.
        packet: (unsigned char[2040] / list of ints) Packet bytes.

    """

    _fields_ = [
        ("header", c_uint16),
        ("headerSet", c_uint8),
        ("packet", (c_uint8 * 2040))]  # M_PDU_PACKET_MAX_SIZE macro in C


class CCSDS_TF_M_PDU_HEADER(Structure):
    """A structure used to represent the header of a M_PDU packet.
    This structure should never be used to access the TF M_PDU header part of a TF packet.
    See the equivalent `STAR_system.ccsds_spp_tf_structs_external.CCSDS_TF_M_PDU_HEADER_EXTERNAL` that users NEED to use.

    Attributes:\n
        reserved: (unsigned int / int) Reserved bits.
        firstHeaderPointer: (unsigned int / int) First header pointer.

    """

    _fields_ = [
        ("reserved", c_uint32, 5),
        ("firstHeaderPointer", c_uint32, 11)]


class CCSDS_TF_PACKET_PRIMARY_HEADER(Structure):
    """A structure used to represent the primary header of a transfer frame.
    This structure should never be used to access the primary header of a TF packet.
    See the equivalent `STAR_system.ccsds_spp_tf_structs_external.CCSDS_TF_PACKET_PRIMARY_HEADER_EXTERNAL` that users NEED to use.

    Attributes:\n
        versionNumber: (unsigned int / int) Version number of the tf.
        spaceCraftId: (unsigned char / int) ID of the spacecraft.
        virtualChannelId: (unsigned int / int) ID of the virtual channel used.
        virtualChannelFrameCount: (unsigned int / int) Sequential binary count of the transmitted tf packets.
        replayFlag: (unsigned int / int) Flag specifying whether the data is "live" or "replayed".
        virtualChannelFrameCountUsageFlag: (unsigned int / int) Flag specifying whether the frame count is used or not.
        reservedSpareBits: (unsigned int / int) Reserved bits (by the CCSDS/SPP standard for future use).
        virtualChannelFrameCountCycle: (unsigned int / int) Whenever the VC frame count returns to 0, this is incremented.
        errorControl: (unsigned int / int) Frame header error control. This field is optional.

    """

    _fields_ = [
        ("versionNumber", c_uint32, 2),
        ("spaceCraftId", c_uint8),
        ("virtualChannelId", c_uint32, 6),
        ("virtualChannelFrameCount", c_uint32, 24),
        ("replayFlag", c_uint32, 1),
        ("virtualChannelFrameCountUsageFlag", c_uint32, 1),
        ("reservedSpareBits", c_uint32, 2),
        ("virtualChannelFrameCountCycle", c_uint32, 4),
        ("errorControl", c_uint16)]


class CCSDS_TF_INSERT_ZONE(Structure):
    """A structure used to represent the insert zone field inside a Transfer Frame
       Note: The insert zone is AOS (Advanced Orbiting Systems) specific field
       and as such it is optional.
       This structure should never be used to access the insert zone contents of a TF packet.
       See the equivalent `STAR_system.ccsds_spp_tf_structs_external.CCSDS_TF_INSERT_ZONE_EXTERNAL` that users NEED to use.

    Attributes:\n
        pData: (unsigned char * / int) Array of bytes holding the data.
        length: (unsigned char / int) Length of the data.

    """

    _fields_ = [
        ("pData", POINTER(c_ubyte)),
        ("length", c_uint8)]


class CCSDS_TF_M_PDU_DATA_FIELD(Structure):
    """A structure used to represent the data field of a M_PDU packet.
        This structure should never be used to access the
        M_PDU data field contents of a TF packet.
        See the equivalent `STAR_system.ccsds_spp_tf_structs_external.CCSDS_TF_M_PDU_DATA_FIELD_EXTERNAL`.

    Attributes:\n
        header (STAR_system.ccsds_spp_tf_structs_internal.CCSDS_TF_M_PDU_HEADER): Header structure of the M_PDU packet.
        pData: (unsigned char * / int) CCSDS/SPP packet data bytes.

    """

    _fields_ = [
        ("header", CCSDS_TF_M_PDU_HEADER),
        ("pData", POINTER(c_ubyte))]


class CCSDS_TF_M_PDU_PACKET(Structure):
    """A structure used to represent a complete transfer frame that is using
       M_PDU packets as payload.
       This structure should never be used to access the M_PDU packet contents of a TF packet.
       See the equivalent `STAR_system.ccsds_spp_tf_structs_external.CCSDS_TF_M_PDU_PACKET_EXTERNAL` that users NEED to use.

    Attributes:\n
        encapsulationHeader (STAR_system.ccsds_spp_tf_structs_internal.CCSDS_SPP_ENCAPS_HEADER): Structure holding the encapsulation header of the packet.
        primaryHeader (STAR_system.ccsds_spp_tf_structs_internal.CCSDS_TF_PACKET_PRIMARY_HEADER): Structure holding the primary header information.
        insertZone (STAR_system.ccsds_spp_tf_structs_internal.CCSDS_TF_INSERT_ZONE): Structure holding the insert zone data.
        dataField (STAR_system.ccsds_spp_tf_structs_internal.CCSDS_TF_M_PDU_DATA_FIELD): Structure holding the data field of the packet.
        operationalControlField: (unsigned int / int) Operational control field (optional).
        frameErrorControlField: (unsigned short / int) Frame error control field (optional).

    """

    _fields_ = [
        ("encapsulationHeader", CCSDS_SPP_ENCAPS_HEADER),
        ("primaryHeader", CCSDS_TF_PACKET_PRIMARY_HEADER),
        ("insertZone", CCSDS_TF_INSERT_ZONE),
        ("dataField", CCSDS_TF_M_PDU_DATA_FIELD),
        ("operationalControlField", c_uint32),
        ("frameErrorControlField", c_uint16)]


class CCSDS_SPP_PACKET_PRIMARY_HEADER(Structure):
    """A structure used to represent the primary header of a CCSDS/SPP packet.
        This structure should never be used to access the primary header contents of a CCSDS/SPP packet.
        See the equivalent `STAR_system.ccsds_spp_tf_structs_external.CCSDS_SPP_PACKET_PRIMARY_HEADER_EXTERNAL` that users NEED to use.

        Attributes:\n
            versionNumber: (unsigned int / int) Version number of the packet.
            type: (unsigned int / int) Type of the packet (0 for Telemetry / 1 for Telecommand).
            packetType: (int / int) This is an internal variable.
            secondaryHeaderFlag: (unsigned int / int) Flag that shows the presence of the secondary header.
            APID: (unsigned int / int) Application Process Identifier.
            sequenceFlags: (unsigned int / int) Sequence flags.
            sequenceCount: (unsigned int / int) Sequence count of the packet.
            dataFieldLength: (unsigned int / int) The length of the data field.

        """

    _fields_ = [
        ("versionNumber", c_uint32, 3),
        ("type", c_uint32, 1),
        ("packetType", c_int32),
        ("secondaryHeaderFlag", c_uint32, 1),
        ("APID", c_uint32, 11),
        ("sequenceFlags", c_uint32, 2),
        ("sequenceCount", c_uint32, 14),
        ("dataFieldLength", c_uint16)]


class CCSDS_SPP_PACKET_DATA_FIELD(Structure):
    """A structure used to represent the data field
       of a CCSDS/SPP/PUS packet. This structure should never be
       written to directly. Instead, pass the desired contents
       into the CCSDS_SPP_CreatePacket* function.
       This structure should never be used to access the
       data field contents of a CCSDS/SPP packet.
       See the equivalent `STAR_system.ccsds_spp_tf_structs_external.CCSDS_SPP_PACKET_DATA_FIELD_EXTERNAL` that users NEED to use.

    Attributes:\n
        pSecondaryHeader: (unsigned char * / int) Pointer pointing to the secondary header of a packet.
        pUserData: (unsigned char * / int) Pointer pointing to the user data section of a packet.

    """

    _fields_ = [
        ("pSecondaryHeader", POINTER(c_ubyte)),
        ("pUserData", POINTER(c_ubyte))]


class CCSDS_SPP_PACKET(Structure):
    """A structure used to represent the contents
       of a CCSDS/SPP/PUS packet. This structure should never be
       written to directly. This structure should never be used
       to access the contents of a CCSDS/SPP packet.
       See the equivalent `STAR_system.ccsds_spp_tf_structs_external.CCSDS_SPP_PACKET_EXTERNAL` that users NEED to use.

    Attributes:\n
        encapsulationHeader (STAR_system.ccsds_spp_tf_structs_internal.CCSDS_SPP_ENCAPS_HEADER): Structure holding the encapsulation header of the packet.
        primaryHeader (STAR_system.ccsds_spp_tf_structs_internal.CCSDS_SPP_PACKET_PRIMARY_HEADER): Structure holding the primary header of the packet.
        dataField (STAR_system.ccsds_spp_tf_structs_internal.CCSDS_SPP_PACKET_DATA_FIELD): Structure holding the data field of the packet.

    """

    _fields_ = [
        ("encapsulationHeader", CCSDS_SPP_ENCAPS_HEADER),
        ("primaryHeader", CCSDS_SPP_PACKET_PRIMARY_HEADER),
        ("dataField", CCSDS_SPP_PACKET_DATA_FIELD)]

