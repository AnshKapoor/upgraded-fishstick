"""
PUS Telemetry Packet Parser
---------------------------

This module provides utilities to decode CCSDS + PUS telemetry (TM) packets
into Python dataclasses. It complements the `_build_tm_packet()` function from
the BrickMk4 Service 1 plugin by performing the reverse operation — parsing
telemetry received from the hardware or simulator.

Standards:
    - CCSDS 133.0-B-1: Space Packet Protocol
    - ECSS-E-ST-70-41C: Packet Utilisation Standard (PUS-C)

Main Components:
    • `parse_ccsds_primary_header()` — Extracts the 6-byte CCSDS Primary Header.
    • `parse_pus_tm_header()` — Extracts the 4-byte PUS TM Header.
    • `parse_tm_packet()` — High-level parser that combines both and
      interprets Service 1 (Request Verification) telemetry packets.

Used by:
    The `displayResults()` method in `BrickMk4_Plugin_service1.py` calls
    `parse_tm_packet()` to decode raw telemetry received via SpaceWire
    and present human-readable summaries like "TM[1,5] Progress".
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, List

# --------------------------------------------------------------------------
# PUS constants and bit masks
# --------------------------------------------------------------------------

ACK_ACCEPTANCE  = 0b0001
ACK_START       = 0b0010
ACK_PROGRESS    = 0b0100
ACK_COMPLETION  = 0b1000

PUS_SERVICE_REQUEST_VERIFICATION = 1

SUBSERVICE_ACK_SUCCESSFUL            = 1  # TM[1,1]
SUBSERVICE_START_SUCCESSFUL          = 3  # TM[1,3]
SUBSERVICE_SUCCESSFUL_PROGRESS       = 5  # TM[1,5]
SUBSERVICE_SUCCESSFUL_COMPLETION     = 7  # TM[1,7]

# --------------------------------------------------------------------------
# Data classes for structured representation
# --------------------------------------------------------------------------

@dataclass
class CCSDSPrimaryHeader:
    """
    Represents the 6-byte CCSDS Primary Header of a TM packet.

    Fields:
        version (int): 3-bit CCSDS version number (usually 0).
        pkt_type (int): 1-bit type flag (0=Telemetry, 1=Telecommand).
        sec_hdr_flag (int): 1-bit flag indicating presence of a secondary header.
        apid (int): 11-bit Application Process ID (identifies subsystem).
        seq_flags (int): 2-bit segmentation flags (e.g., 3=standalone).
        seq_count (int): 14-bit sequence counter.
        pkt_length (int): Total length of the remaining packet data minus one.
    """
    version: int           # 3 bits
    pkt_type: int          # 1 bit (0=TM, 1=TC)
    sec_hdr_flag: int      # 1 bit
    apid: int              # 11 bits
    seq_flags: int         # 2 bits
    seq_count: int         # 14 bits
    pkt_length: int        # 16 bits (total data bytes - 1)

@dataclass
class PUSTMHeader:
    """
    Represents the 4-byte PUS Telemetry Header.

    Fields:
        pus_version (int): PUS version identifier (1 = PUS-C).
        service_type (int): Main PUS service (e.g., 1 = Request Verification).
        service_subtype (int): Subservice ID (e.g., 1, 3, 5, or 7).
        source_id (int): Identifier of the packet's origin subsystem.
    """
    pus_version: int       # 1 (PUS-C)
    service_type: int      # e.g. 1
    service_subtype: int   # e.g. 1/3/5/7
    source_id: int         # 1 byte

@dataclass
class ParsedTM:
    """
    High-level structure combining CCSDS and PUS headers with the packet payload.

    Fields:
        primary (CCSDSPrimaryHeader): Decoded CCSDS header.
        pus (PUSTMHeader): Decoded PUS TM header.
        payload (bytes): Raw payload data following the headers.
        step_id (Optional[int]): Optional step counter (for TM[1,5] Progress).
        summary (Optional[str]): Human-readable description (e.g., "TM[1,3] Start").
    """
    primary: CCSDSPrimaryHeader
    pus: PUSTMHeader
    payload: bytes
    step_id: Optional[int] = None
    summary: Optional[str] = None

# --------------------------------------------------------------------------
# Utility and parsing functions
# --------------------------------------------------------------------------

def _u16_be(b0: int, b1: int) -> int:
    """Return a 16-bit big-endian integer from two bytes."""
    return (b0 << 8) | b1

def parse_ccsds_primary_header(buf: List[int]) -> CCSDSPrimaryHeader:
    """
    Parse the CCSDS Primary Header (first 6 bytes) from a telemetry packet.

    Args:
        buf (List[int]): List of bytes representing the full packet.

    Returns:
        CCSDSPrimaryHeader: Object with decoded header fields.

    Raises:
        ValueError: If the input buffer is shorter than 6 bytes.
    """
    if len(buf) < 6:
        raise ValueError("buffer too short for CCSDS primary header")

    # Split the first 6 bytes
    b0, b1, b2, b3, b4, b5 = buf[0:6]

    # Extract fields from the two 16-bit header words
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
        version=version, 
        pkt_type=pkt_type, 
        sec_hdr_flag=sec_hdr_flag,
        apid=apid, 
        seq_flags=seq_flags, 
        seq_count=seq_count, 
        pkt_length=pkt_length
    )

def parse_pus_tm_header(buf: List[int], start: int = 6) -> PUSTMHeader:
    """
    Parse the PUS Telemetry Header starting at a given byte offset.

    Args:
        buf (List[int]): Complete packet data.
        start (int): Starting index for PUS header (default = 6, right after CCSDS).

    Returns:
        PUSTMHeader: Object containing decoded PUS header fields.

    Raises:
        ValueError: If fewer than 4 bytes are available after the start index.
    """
    if len(buf) < start + 4:
        raise ValueError("buffer too short for PUS TM header")

    v = buf[start]

    # Accept direct values (0,1,2) or extract version nibble
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
    """
    Parse a complete CCSDS + PUS telemetry packet into structured data.

    This function is the inverse of `_build_tm_packet()` used in the DHU Simulator.
    It decodes the binary telemetry packet received from the SpaceWire interface
    into a `ParsedTM` dataclass, making it easy to interpret and display its contents.

    Args:
        raw (List[int]): List of integer byte values representing the TM packet.

    Returns:
        ParsedTM: Object containing decoded headers, payload, and textual summary.

    Behavior:
        1. Extracts CCSDS and PUS headers.
        2. Determines payload start (byte 10 by default: 6 + 4).
        3. Interprets Service 1 (Request Verification) subservices:
            - TM[1,1] Acceptance successful
            - TM[1,3] Start successful
            - TM[1,5] Progress (includes optional step ID)
            - TM[1,7] Completion successful
        4. For unknown subservices, creates a generic summary string.

    Example:
        >>> raw = [0, 49, 192, 1, 0, 4, 1, 1, 5, 1, 12]
        >>> pkt = parse_tm_packet(raw)
        >>> pkt.summary
        'TM[1,5] Progress'

    Raises:
        ValueError: If the buffer is too short for expected header sections.
    """
    # --- Parse primary and secondary headers ---
    primary = parse_ccsds_primary_header(raw)
    pus = parse_pus_tm_header(raw, start=6)

    # Determine start of payload (after 10 bytes)
    payload_start = 10
    if len(raw) < payload_start:
        payload = b""
    else:
        payload = bytes(raw[payload_start:])

    # Create parsed TM structure
    parsed = ParsedTM(primary=primary, pus=pus, payload=payload)

    # --- Interpret Service 1 packets (Request Verification) ---
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
