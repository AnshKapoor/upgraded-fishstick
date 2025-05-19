"""Data structures used by CCSDS/SPP/TF packet library to present the contents of a
    CCSDS_SPP and TF packet to the user.

Brief:\n
    Data structures used by CCSDS/SPP/TF packet library to present the contents of a
    CCSDS_SPP and TF packet to the user. These structures are populated by the corresponding
    functions that create/fill CCSDS/SPP and TF packets.

Copyright:\n
    2021 STAR-Dundee Ltd.
"""

from STAR_system.ccsds_spp_tf_enums import CCSDS_SPP_PACKET_TYPE


class CCSDS_SPP_ENCAPS_HEADER_EXTERNAL():
    """A structure/class used to describe an encapsulation header in the CCSDS/SPP/TF packet library.
    This is the structure/class that the user should ALWAYS use.

    Attributes:\n
        Same as the fields of the `STAR_system.ccsds_spp_tf_structs_internal.CCSDS_SPP_ENCAPS_HEADER` structure, the type of each field
        being the Python equivalent.
    """

    def __init__(self):
        #: header: list of ints (see equivalent Structure member in `STAR_system.ccsds_spp_tf_structs_internal.CCSDS_SPP_ENCAPS_HEADER`)
        self.header = []

        #: length: int (see equivalent Structure member in `STAR_system.ccsds_spp_tf_structs_internal.CCSDS_SPP_ENCAPS_HEADER`)
        self.length = 0


class CCSDS_SPP_PACKET_PRIMARY_HEADER_EXTERNAL():
    """A structure/class used to represent the primary header of a CCSDS/SPP packet.
    This is the structure/class that the user should ALWAYS use.

    Attributes:\n
        Same as the fields of the `STAR_system.ccsds_spp_tf_structs_internal.CCSDS_SPP_PACKET_PRIMARY_HEADER` structure, the type of each field
        being the Python equivalent.

    """

    def __init__(self):
        #: versionNumber: int (see equivalent Structure member in `STAR_system.ccsds_spp_tf_structs_internal.CCSDS_SPP_PACKET_PRIMARY_HEADER`)
        self.versionNumber = 0

        #: type: int (see equivalent Structure member in `STAR_system.ccsds_spp_tf_structs_internal.CCSDS_SPP_PACKET_PRIMARY_HEADER`)
        self.type = 0

        #: packetType: `STAR_system.ccsds_spp_tf_enums.CCSDS_SPP_PACKET_TYPE` (see equivalent Structure member in `STAR_system.ccsds_spp_tf_structs_internal.CCSDS_SPP_PACKET_PRIMARY_HEADER`)
        self.packetType = CCSDS_SPP_PACKET_TYPE(0)

        #: secondaryHeaderFlag: bool (see equivalent Structure member in `STAR_system.ccsds_spp_tf_structs_internal.CCSDS_SPP_PACKET_PRIMARY_HEADER`)
        self.secondaryHeaderFlag = False

        #: APID: int (see equivalent Structure member in `STAR_system.ccsds_spp_tf_structs_internal.CCSDS_SPP_PACKET_PRIMARY_HEADER`)
        self.APID = 0

        #: sequenceFlags: int (see equivalent Structure member in `STAR_system.ccsds_spp_tf_structs_internal.CCSDS_SPP_PACKET_PRIMARY_HEADER`)
        self.sequenceFlags = 0

        #: sequenceCount: int (see equivalent Structure member in `STAR_system.ccsds_spp_tf_structs_internal.CCSDS_SPP_PACKET_PRIMARY_HEADER`)
        self.sequenceCount = 0

        #: dataFieldLength: int (see equivalent Structure member in `STAR_system.ccsds_spp_tf_structs_internal.CCSDS_SPP_PACKET_PRIMARY_HEADER`)
        self.dataFieldLength = 0


class CCSDS_SPP_PACKET_DATA_FIELD_EXTERNAL():
    """A structure/class used to represent the data field of a CCSDS/SPP/PUS packet.
    This is the structure/class that the user should ALWAYS use.

    Attributes:\n
        Same as the fields of the `STAR_system.ccsds_spp_tf_structs_internal.CCSDS_SPP_PACKET_DATA_FIELD` structure, the type of each field
        being the Python equivalent.

    """
    def __init__(self):
        #: secondaryHeader: list of ints (see equivalent Structure member in `STAR_system.ccsds_spp_tf_structs_internal.CCSDS_SPP_PACKET_DATA_FIELD`)
        self.secondaryHeader = []

        #: userData: list of ints (see equivalent Structure member in `STAR_system.ccsds_spp_tf_structs_internal.CCSDS_SPP_PACKET_DATA_FIELD`)
        self.userData = []


class CCSDS_SPP_PACKET_EXTERNAL():
    """A structure/class used to represent the contents of a CCSDS/SPP/PUS packet.
    This is the structure/class that the user should ALWAYS use.

    Attributes:\n
        Same as the fields of the `STAR_system.ccsds_spp_tf_structs_internal.CCSDS_SPP_PACKET` structure, the type of each field
        being the Python equivalent.
    """

    def __init__(self):
        #: encapsulationHeader: `STAR_system.ccsds_spp_tf_structs_external.CCSDS_SPP_ENCAPS_HEADER_EXTERNAL` (see equivalent Structure member in `STAR_system.ccsds_spp_tf_structs_internal.CCSDS_SPP_PACKET`)
        self.encapsulationHeader = CCSDS_SPP_ENCAPS_HEADER_EXTERNAL()

        #: primaryHeader: `STAR_system.ccsds_spp_tf_structs_external.CCSDS_SPP_PACKET_PRIMARY_HEADER_EXTERNAL` (see equivalent Structure member in `STAR_system.ccsds_spp_tf_structs_internal.CCSDS_SPP_PACKET`)
        self.primaryHeader = CCSDS_SPP_PACKET_PRIMARY_HEADER_EXTERNAL()

        #: dataField: `STAR_system.ccsds_spp_tf_structs_external.CCSDS_SPP_PACKET_DATA_FIELD_EXTERNAL` (see equivalent Structure member in `STAR_system.ccsds_spp_tf_structs_internal.CCSDS_SPP_PACKET`)
        self.dataField = CCSDS_SPP_PACKET_DATA_FIELD_EXTERNAL()

class CCSDS_TF_PACKET_PRIMARY_HEADER_EXTERNAL():
    """A structure/class used to represent the primary header of a transfer frame.
    This is the structure/class that the user should ALWAYS use.

    Attributes:\n
        Same as the fields of the `STAR_system.ccsds_spp_tf_structs_internal.CCSDS_TF_PACKET_PRIMARY_HEADER` structure, the type of each field
        being the Python equivalent.

    """
    def __init__(self):
        #: versionNumber: int (see equivalent Structure member in `STAR_system.ccsds_spp_tf_structs_internal.CCSDS_TF_PACKET_PRIMARY_HEADER`)
        self.versionNumber = 0

        #: spaceCraftId: int (see equivalent Structure member in `STAR_system.ccsds_spp_tf_structs_internal.CCSDS_TF_PACKET_PRIMARY_HEADER`)
        self.spaceCraftId = 0

        #: virtualChannelId: int (see equivalent Structure member in `STAR_system.ccsds_spp_tf_structs_internal.CCSDS_TF_PACKET_PRIMARY_HEADER`)
        self.virtualChannelId = 0

        #: virtualChannelFrameCount: int (see equivalent Structure member in `STAR_system.ccsds_spp_tf_structs_internal.CCSDS_TF_PACKET_PRIMARY_HEADER`)
        self.virtualChannelFrameCount = 0

        #: replayFlag: bool (see equivalent Structure member in `STAR_system.ccsds_spp_tf_structs_internal.CCSDS_TF_PACKET_PRIMARY_HEADER`)
        self.replayFlag = False

        #: virtualChannelFrameCountUsageFlag: bool (see equivalent Structure member in `STAR_system.ccsds_spp_tf_structs_internal.CCSDS_TF_PACKET_PRIMARY_HEADER`)
        self.virtualChannelFrameCountUsageFlag = False

        #: reservedSpareBits: int (see equivalent Structure member in `STAR_system.ccsds_spp_tf_structs_internal.CCSDS_TF_PACKET_PRIMARY_HEADER`)
        self.reservedSpareBits = 0

        #: virtualChannelFrameCountCycle: int (see equivalent Structure member in `STAR_system.ccsds_spp_tf_structs_internal.CCSDS_TF_PACKET_PRIMARY_HEADER`)
        self.virtualChannelFrameCountCycle = 0

        #: errorControl: int (see equivalent Structure member in `STAR_system.ccsds_spp_tf_structs_internal.CCSDS_TF_PACKET_PRIMARY_HEADER`)
        self.errorControl = 0


class CCSDS_TF_INSERT_ZONE_EXTERNAL():
    """A structure/class used to represent the insert zone field inside a Transfer Frame
       Note: The insert zone is AOS (Advanced Orbiting Systems) specific field
       and as such it is optional.
       This is the structure/class that the user should ALWAYS use.

    Attributes:\n
        Same as the fields of the `STAR_system.ccsds_spp_tf_structs_internal.CCSDS_TF_INSERT_ZONE` structure, the type of each field
        being the Python equivalent.

   """

    def __init__(self):
        #: data: list of ints (see equivalent Structure member in `STAR_system.ccsds_spp_tf_structs_internal.CCSDS_TF_INSERT_ZONE`)
        self.data = []

        #: length: int (see equivalent Structure member in `STAR_system.ccsds_spp_tf_structs_internal.CCSDS_TF_INSERT_ZONE`)
        self.length = 0

class CCSDS_TF_M_PDU_HEADER_EXTERNAL():
    """A structure/class used to represent the header of a M_PDU packet.
    This is the structure/class that the user should ALWAYS use.

    Attributes:\n
        Same as the fields of the `STAR_system.ccsds_spp_tf_structs_internal.CCSDS_TF_M_PDU_HEADER` structure, the type of each field
        being the Python equivalent.

    """

    def __init__(self):
        #: reserved: int (see equivalent Structure member in `STAR_system.ccsds_spp_tf_structs_internal.CCSDS_TF_M_PDU_HEADER`)
        self.reserved = 0

        #: firstHeaderPointer: int (see equivalent Structure member in `STAR_system.ccsds_spp_tf_structs_internal.CCSDS_TF_M_PDU_HEADER`)
        self.firstHeaderPointer = 0


class CCSDS_TF_M_PDU_DATA_FIELD_EXTERNAL():
    """A structure/class used to represent the data field of a M_PDU packet.
    This is the structure/class that the user should ALWAYS use.

    Attributes:\n
        Same as the fields of the `STAR_system.ccsds_spp_tf_structs_internal.CCSDS_TF_M_PDU_DATA_FIELD` structure, the type of each field
        being the Python equivalent.

    """

    def __init__(self):
        #: header: `STAR_system.ccsds_spp_tf_structs_external.CCSDS_TF_M_PDU_HEADER_EXTERNAL` (see equivalent Structure member in `STAR_system.ccsds_spp_tf_structs_internal.CCSDS_TF_M_PDU_DATA_FIELD`)
        self.header = CCSDS_TF_M_PDU_HEADER_EXTERNAL()

        #: data: list of ints (see equivalent Structure member in `STAR_system.ccsds_spp_tf_structs_internal.CCSDS_TF_M_PDU_DATA_FIELD`)
        self.data = []


class CCSDS_TF_M_PDU_PACKET_EXTERNAL():
    """A structure/class used to represent a complete transfer frame that is using M_PDU packets as payload.
    This is the structure/class that the user should ALWAYS use.

    Attributes:\n
        Same as the fields of the `STAR_system.ccsds_spp_tf_structs_internal.CCSDS_TF_M_PDU_PACKET` structure, the type of each field
        being the Python equivalent.

   """

    def __init__(self):
        #: encapsulationHeader: `STAR_system.ccsds_spp_tf_structs_external.CCSDS_SPP_ENCAPS_HEADER_EXTERNAL` (see equivalent Structure member in `STAR_system.ccsds_spp_tf_structs_internal.CCSDS_TF_M_PDU_PACKET`)
        self.encapsulationHeader = CCSDS_SPP_ENCAPS_HEADER_EXTERNAL()

        #: primaryHeader: `STAR_system.ccsds_spp_tf_structs_external.CCSDS_TF_PACKET_PRIMARY_HEADER_EXTERNAL` (see equivalent Structure member in `STAR_system.ccsds_spp_tf_structs_internal.CCSDS_TF_M_PDU_PACKET`)
        self.primaryHeader = CCSDS_TF_PACKET_PRIMARY_HEADER_EXTERNAL()

        #: insertZone: `STAR_system.ccsds_spp_tf_structs_external.CCSDS_TF_INSERT_ZONE_EXTERNAL` (see equivalent Structure member in `STAR_system.ccsds_spp_tf_structs_internal.CCSDS_TF_M_PDU_PACKET`)
        self.insertZone = CCSDS_TF_INSERT_ZONE_EXTERNAL()

        #: dataField: `STAR_system.ccsds_spp_tf_structs_external.CCSDS_TF_M_PDU_DATA_FIELD_EXTERNAL` (see equivalent Structure member in `STAR_system.ccsds_spp_tf_structs_internal.CCSDS_TF_M_PDU_PACKET`)
        self.dataField = CCSDS_TF_M_PDU_DATA_FIELD_EXTERNAL()

        #: operationalControlField: int (see equivalent Structure member in `STAR_system.ccsds_spp_tf_structs_internal.CCSDS_TF_M_PDU_PACKET`)
        self.operationalControlField = 0

        #: frameErrorControlField: int (see equivalent Structure member in `STAR_system.ccsds_spp_tf_structs_internal.CCSDS_TF_M_PDU_PACKET`)
        self.frameErrorControlField = 0