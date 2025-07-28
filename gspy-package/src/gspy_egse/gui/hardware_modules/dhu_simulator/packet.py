import struct
from dataclasses import dataclass
from constants import *

@dataclass
class TCPacket:
    version: int
    type: int
    data_field_header: int
    apid: int
    seq_flags: int
    seq_count: int
    pus_version: int
    ack: int

def parse_tc_packet(data: bytes) -> TCPacket:
    """Parse 6-byte PUS Primary Header + 4-byte PUS Secondary Header + ACK"""
    if len(data) < 10:
        raise ValueError("TC packet too short")

    # First 6 bytes: PUS Primary Header
    (word1, word2, word3) = struct.unpack(">HHH", data[:6])
    version = (word1 >> 13) & 0b111
    type_ = (word1 >> 12) & 0b1
    data_field_header = (word1 >> 11) & 0b1
    apid = word1 & 0x07FF
    seq_flags = (word2 >> 14) & 0b11
    seq_count = word2 & 0x3FFF
    length = word3

    # Next: Secondary header (simplified)
    pus_version = data[6]
    ack = data[7]

    return TCPacket(
        version=version,
        type=type_,
        data_field_header=data_field_header,
        apid=apid,
        seq_flags=seq_flags,
        seq_count=seq_count,
        pus_version=pus_version,
        ack=ack
    )

def build_tm_packet(service_type, service_subtype, seq_count, step_id=None) -> bytes:
    """Construct a binary TM packet for TM[1,x]"""
    version = 0b000
    packet_type = 1  # TM
    data_field_header_flag = 1
    apid = APID_DHU_HK
    seq_flags = 0b11
    length = 6  # Secondary header (4) + payload (e.g., 1 or 2 bytes)

    word1 = (version << 13) | (packet_type << 12) | (data_field_header_flag << 11) | apid
    word2 = (seq_flags << 14) | (seq_count & 0x3FFF)
    word3 = length  # usLen field

    # Primary header
    header = struct.pack(">HHH", word1, word2, word3)

    # Secondary header (PUS version, etc.)
    pus_version = VALUE_PUS_VERSION
    service = service_type
    subtype = service_subtype
    spare = 0x00
    sec_header = struct.pack("BBBB", pus_version, service, subtype, spare)

    # Payload
    if service_subtype == PUS_SUBSERVICE_REQUEST_SUCCESSFUL_PROGRESS:
        payload = struct.pack("B", step_id or 0)
    else:
        payload = b''

    return header + sec_header + payload

def build_tc_packet(ack_flags=0x09, seq_count=1, step_id=None):
    version = 0b000
    packet_type = 0  # TC
    data_field_header_flag = 1
    apid = APID_DHU_TC
    seq_flags = 0b11
    length = 4  # secondary header only

    word1 = (version << 13) | (packet_type << 12) | (data_field_header_flag << 11) | apid
    word2 = (seq_flags << 14) | (seq_count & 0x3FFF)
    word3 = length

    header = struct.pack(">HHH", word1, word2, word3)

    # Secondary header (PUS version + ACK)
    sec_header = struct.pack("BBH", VALUE_PUS_VERSION, ack_flags, 0x0000)

    # You may later embed step_id into TC data if needed
    return header + sec_header



def parse_tm_packet(data: bytes):
    # Primary header
    word1, word2, word3 = struct.unpack(">HHH", data[:6])
    seq_count = word2 & 0x3FFF

    # Secondary header
    pus_ver, service, subservice, _ = struct.unpack("BBBB", data[6:10])

    payload = data[10:]
    result = {
        "version": (word1 >> 13) & 0b111,
        "seq_count": seq_count,
        "service": service,
        "subservice": subservice,
        "data": None
    }

    if subservice == PUS_SUBSERVICE_REQUEST_SUCCESSFUL_PROGRESS and len(payload) >= 1:
        result["data"] = {"step_id": payload[0]}
    else:
        result["data"] = payload.hex()

    return result
