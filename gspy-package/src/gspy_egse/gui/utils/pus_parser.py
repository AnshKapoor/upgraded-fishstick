from dataclasses import dataclass
from typing import Dict, Any, Optional, List

ACK_ACCEPTANCE  = 0b0001
ACK_START       = 0b0010
ACK_PROGRESS    = 0b0100
ACK_COMPLETION  = 0b1000

PUS_SERVICE_REQUEST_VERIFICATION = 1

SUBSERVICE_ACK_SUCCESSFUL            = 1  # TM[1,1]
SUBSERVICE_START_SUCCESSFUL          = 3  # TM[1,3]
SUBSERVICE_SUCCESSFUL_PROGRESS       = 5  # TM[1,5]
SUBSERVICE_SUCCESSFUL_COMPLETION     = 7  # TM[1,7]

@dataclass
class CCSDSPrimaryHeader:
    version: int           # 3 bits
    pkt_type: int          # 1 bit (0=TM, 1=TC)
    sec_hdr_flag: int      # 1 bit
    apid: int              # 11 bits
    seq_flags: int         # 2 bits
    seq_count: int         # 14 bits
    pkt_length: int        # 16 bits (total data bytes - 1)

@dataclass
class PUSTMHeader:
    pus_version: int       # 1 (PUS-C)
    service_type: int      # e.g. 1
    service_subtype: int   # e.g. 1/3/5/7
    source_id: int         # 1 byte

@dataclass
class ParsedTM:
    primary: CCSDSPrimaryHeader
    pus: PUSTMHeader
    payload: bytes
    step_id: Optional[int] = None
    summary: Optional[str] = None

def _u16_be(b0: int, b1: int) -> int:
    return (b0 << 8) | b1

def parse_ccsds_primary_header(buf: List[int]) -> CCSDSPrimaryHeader:
    if len(buf) < 6:
        raise ValueError("buffer too short for CCSDS primary header")

    b0, b1, b2, b3, b4, b5 = buf[0:6]

    first16 = _u16_be(b0, b1)
    version      = (first16 >> 13) & 0b111
    pkt_type     = (first16 >> 12) & 0b1
    sec_hdr_flag = (first16 >> 11) & 0b1
    apid         =  first16        & 0x07FF

    second16  = _u16_be(b2, b3)
    seq_flags = (second16 >> 14) & 0b11
    seq_count =  second16        & 0x3FFF

    pkt_length = _u16_be(b4, b5)

    return CCSDSPrimaryHeader(
        version=version, pkt_type=pkt_type, sec_hdr_flag=sec_hdr_flag,
        apid=apid, seq_flags=seq_flags, seq_count=seq_count, pkt_length=pkt_length
    )

def parse_pus_tm_header(buf: List[int], start: int = 6) -> PUSTMHeader:

    if len(buf) < start + 4:
        raise ValueError("buffer too short for PUS TM header")

    v = buf[start]

    pus_version = v if v in (0, 1, 2) else ((v >> 4) & 0x0F)

    service_type    = buf[start + 1]
    service_subtype = buf[start + 2]
    source_id       = buf[start + 3]

    return PUSTMHeader(
        pus_version=pus_version,
        service_type=service_type,
        service_subtype=service_subtype,
        source_id=source_id
    )

def parse_tm_packet(raw: List[int]) -> ParsedTM:

    primary = parse_ccsds_primary_header(raw)
    pus = parse_pus_tm_header(raw, start=6)

    payload_start = 10
    if len(raw) < payload_start:
        payload = b""
    else:
        payload = bytes(raw[payload_start:])

    parsed = ParsedTM(primary=primary, pus=pus, payload=payload)

    if pus.service_type == PUS_SERVICE_REQUEST_VERIFICATION:
        if   pus.service_subtype == SUBSERVICE_ACK_SUCCESSFUL:
            parsed.summary = "TM[1,1] Acceptance successful"
        elif pus.service_subtype == SUBSERVICE_START_SUCCESSFUL:
            parsed.summary = "TM[1,3] Start of execution successful"
        elif pus.service_subtype == SUBSERVICE_SUCCESSFUL_PROGRESS:
            parsed.summary = "TM[1,5] Progress"

            parsed.step_id = payload[0] if len(payload) >= 1 else None
        elif pus.service_subtype == SUBSERVICE_SUCCESSFUL_COMPLETION:
            parsed.summary = "TM[1,7] Completion successful"
        else:
            parsed.summary = f"TM[1,{pus.service_subtype}] (unhandled subtype)"
    else:
        parsed.summary = f"TM[{pus.service_type},{pus.service_subtype}]"

    return parsed
