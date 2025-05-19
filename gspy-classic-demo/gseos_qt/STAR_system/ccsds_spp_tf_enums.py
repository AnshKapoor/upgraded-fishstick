""" Contains all the enums used by the CCSDS/SPP/TF packet library.

Brief:\n
    Contains all the enums used by the CCSDS/SPP/TF packet library.

Copyright:\n
    2021 STAR-Dundee Ltd
"""

from enum import IntEnum


class CCSDS_SPP_STATUS(IntEnum):
    """Possible values for the status of CCSDS/SPP/TF/PUS related operations."""

    CCSDS_SPP_STATUS_SUCCESS = 0
    """The status value indicating success."""

    CCSDS_SPP_STATUS_RAW_DATA_POINTER_NULL = 1
    """The status value indicating that the pointer pointing to the raw data packet is NULL."""

    CCSDS_SPP_STATUS_STATUS_POINTER_NULL = 2
    """The status value indicating that the pointer holding the returned status of the CCSDS_SPP* operation was NULL."""

    CCSDS_SPP_STATUS_RAW_PACKET_LENGTH_POINTER_NULL = 3
    """The status value indicating that the pointer holding the length of the raw packet was NULL."""

    CCSDS_SPP_STATUS_PACKET_TYPE_UNKNOWN = 4
    """The status value indicating that the packet type is unknown."""

    CCSDS_SPP_STATUS_APID_INVALID = 5
    """The status value indicating that the APID (Application Process Identifier) is invalid."""

    CCSDS_SPP_STATUS_SEQUENCE_FLAGS_INVALID = 6
    """The status value indicating that the value of the sequence flags is invalid."""

    CCSDS_SPP_STATUS_DATA_LENGTH_INVALID = 7
    """The status value indicating that the given data length value is invalid."""

    CCSDS_SPP_STATUS_MEMORY_FAILURE = 8
    """The status value indicating that the requested memory could not be allocated."""

    CCSDS_SPP_STATUS_PACKET_STRUCTURE_POINTER_NULL = 9
    """The status value indicating that the packet structure pointer containing information about the CCSDS/SPP packet
    was NULL (invalid)."""

    CCSDS_SPP_STATUS_VALUE_POINTER_NULL = 10
    """The status value indicating that the pointer holding the value of the variable to be retrieved is NULL."""

    CCSDS_SPP_STATUS_ENCAPSULATION_HEADER_NULL = 11
    """The status value indicating that the encapsulation header within the CCSDS/SPP packet was NULL."""

    CCSDS_SPP_STATUS_PTP_HEADER_INCOMPLETE = 12
    """The status value indicating that the PTP protocol header within the CCSDS/SPP packet was incomplete."""

    CCSDS_SPP_STATUS_SECONDARY_HEADER_POINTER_NULL = 13
    """The status value indicating that the pointer pointing to the secondary header is NULL."""

    CCSDS_SPP_STATUS_SECONDARY_HEADER_LENGTH_INVALID = 14
    """The status value indicating that the length of the secondary header is invalid (zero)."""

    CCSDS_SPP_STATUS_ENCAPSULATION_HEADER_LENGTH_INVALID = 15
    """The status value indicating that the length of the encapsulation header is invalid (zero)."""

    CCSDS_SPP_STATUS_RECEIVED_RAW_DATA_POINTER_NULL = 16
    """The status value indicating that the pointer pointing to the received raw data is NULL."""

    CCSDS_SPP_STATUS_PTP_PROTOCOL_IDENTIFIER_INCORRECT = 17
    """The status value indicating that the PTP protocol identifier value is incorrect."""

    CCSDS_SPP_STATUS_PTP_HEADER_INVALID = 18
    """The status value indicating that the PTP header is invalid."""

    CCSDS_SPP_STATUS_PTP_HEADER_POINTER_NULL = 19
    """The status value indicating that the pointer pointing to the PTP header is NULL."""

    CCSDS_SPP_STATUS_TELECOMMAND_SECONDARY_HEADER_INVALID = 20
    """The status value indicating that the secondary header used for telecommand type packets is invalid."""

    CCSDS_SPP_STATUS_SECONDARY_HEADER_FLAG_PACKET_TYPE_CONFLICT = 21
    """The status value indicating that the secondary header flag and the packet type are in conflict."""

    CCSDS_SPP_STATUS_TOO_MANY_DEVICE_REGISTER_ADDRESSES_SPECIFIED = 22
    """The status value indicating that too many device register addresses have been specified."""

    CCSDS_SPP_STATUS_BOTH_SECONDARY_HEADER_AND_USER_DATA_FIELD_MISSING = 23
    """The status value indicating that both the secondary header and user data field are missing,
    which is impossible according to the CCSDS/SPP standard."""

    CCSDS_SPP_STATUS_ZERO_CCSDS_SPP_PACKETS_PROVIDED_FOR_TF_CREATION = 24
    """The status value indicating that the length of the array holding the CCSDS/SPP packets that are being used to
    create TF packets was zero."""

    CCSDS_TF_STATUS_PACKET_LENGTHS_POINTER_INVALID = 25
    """The status value indicating that the pointer to the array holding the CCSDS/SPP packet length was invalid."""

    CCSDS_TF_STATUS_NUMBER_OF_CCSDS_SPP_PACKETS_ZERO = 26
    """The status value indicating that the number of CCSDS/SPP packets passed into the
    CCSDS_TF_DetermineNumberOfTFPackets function was zero."""

    CCSDS_TF_STATUS_NUMBER_OF_TF_PACKETS_ZERO = 27
    """The status value indicating that the number of TF packets passed into the Create_M_PDU_Packets function was zero."""

    CCSDS_SPP_STATUS_GENERAL_ERROR = 28
    """The status value indicating that the error does not match any of the other status messages."""

    @classmethod
    def from_param(cls, obj):
        """Function needed for marshalling purposes between Python and the C API."""
        return int(obj)


class CCSDS_SPP_PACKET_TYPE(IntEnum):
    """Possible values for the packet type of CCSDS/SPP packets.
    Note: This enumeration is internal to this library and the values
    only partially reflect the TYPE field in the primary header."""

    CCSDS_SPP_PACKET_TYPE_TELEMETRY = 0
    """Telemetry packet type."""

    CCSDS_SPP_PACKET_TYPE_TELECOMMAND = 1
    """Telecommand packet type."""

    CCSDS_SPP_PACKET_TYPE_CPDU_COMMAND = 2
    """CPDU command packet type."""

    CCSDS_SPP_PACKET_TYPE_SPACECRAFT_TIME_PACKET = 3
    """Spacecraft time packet packet type."""

    CCSDS_SPP_PACKET_TYPE_IDLE_PACKET = 4
    """IDLE data packet type."""

    @classmethod
    def from_param(cls, obj):
        """Function needed for marshalling purposes between Python and the C API."""
        return int(obj)
