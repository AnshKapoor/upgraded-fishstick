# pus_ccsds.py
import struct

PUS_VERSION = 2

# CCSDS Space Packet primary header pack/unpack ------------------------------

def pack_primary_header(pkt_type_tm0_tc1: int, sec_hdr_flag: int, apid: int,
                        seq_flags: int, seq_count: int, pkt_len: int) -> bytes:
    """
    pkt_type_tm0_tc1: 0=TM, 1=TC
    sec_hdr_flag: usually 1 (PUS always uses a secondary header)
    seq_flags: 0b11 for standalone packets
    pkt_len: number of octets after the first 6 bytes, minus 1
    """
    version = 0  # CCSDS version 0
    assert 0 <= apid <= 0x7FF
    assert 0 <= seq_count <= 0x3FFF
    assert 0 <= seq_flags <= 0x3
    first_2 = (version << 13) | (pkt_type_tm0_tc1 << 12) | (sec_hdr_flag << 11) | apid
    second_2 = (seq_flags << 14) | seq_count
    return struct.pack(">HHH", first_2, second_2, pkt_len)

def unpack_primary_header(hdr6: bytes):
    first_2, second_2, pkt_len = struct.unpack(">HHH", hdr6)
    version   = (first_2 >> 13) & 0x7
    pkt_type  = (first_2 >> 12) & 0x1   # 0=TM, 1=TC
    sec_hdr   = (first_2 >> 11) & 0x1
    apid      =  first_2        & 0x7FF
    seq_flags = (second_2 >> 14) & 0x3
    seq_count =  second_2        & 0x3FFF
    return dict(version=version, pkt_type=pkt_type, sec_hdr=sec_hdr, apid=apid,
                seq_flags=seq_flags, seq_count=seq_count, pkt_len=pkt_len)

# PUS-C TC secondary header (no time) ----------------------------------------

def build_pus_tc_sec_hdr(service: int, subservice: int, ack_nibble: int, source_id: int) -> bytes:
    """
    ack_nibble: 4 bits (bit0 acceptance, bit1 start, bit2 progress, bit3 completion)
    """
    b0 = ((PUS_VERSION & 0xF) << 4) | (ack_nibble & 0xF)
    return struct.pack(">BBBH", b0, service & 0xFF, subservice & 0xFF, source_id & 0xFFFF)

def parse_pus_tc_sec_hdr(sec: bytes):
    b0, service, subservice, source_id = struct.unpack(">BBBH", sec[:5])
    pus_ver = (b0 >> 4) & 0xF
    ack     = b0 & 0xF
    return dict(pus_ver=pus_ver, service=service, subservice=subservice,
                ack=ack, source_id=source_id), sec[5:]

# PUS-C TM secondary header (no time) ----------------------------------------

def build_pus_tm_sec_hdr(service: int, subservice: int, dest_id: int) -> bytes:
    b0 = ((PUS_VERSION & 0xF) << 4) | 0  # spare=0
    return struct.pack(">BBBH", b0, service & 0xFF, subservice & 0xFF, dest_id & 0xFFFF)

def parse_pus_tm_sec_hdr(sec: bytes):
    b0, service, subservice, dest_id = struct.unpack(">BBBH", sec[:5])
    pus_ver = (b0 >> 4) & 0xF
    return dict(pus_ver=pus_ver, service=service, subservice=subservice,
                dest_id=dest_id), sec[5:]

# High-level builders ---------------------------------------------------------

def build_pus_tc(apid: int, seq: int, service: int, subservice: int,
                 ack_nibble: int, source_id: int, app_data: bytes=b"") -> bytes:
    """
    Returns a full CCSDS+PUS TC packet (without outer TCP 4-byte framing).
    """
    sec = build_pus_tc_sec_hdr(service, subservice, ack_nibble, source_id)
    data = sec + app_data
    pkt_len = len(data) - 1  # CCSDS rule
    pri = pack_primary_header(pkt_type_tm0_tc1=1, sec_hdr_flag=1, apid=apid,
                              seq_flags=0b11, seq_count=seq, pkt_len=pkt_len)
    return pri + data

def build_pus_tm(apid: int, seq: int, service: int, subservice: int,
                 dest_id: int, app_data: bytes=b"") -> bytes:
    sec = build_pus_tm_sec_hdr(service, subservice, dest_id)
    data = sec + app_data
    pkt_len = len(data) - 1
    pri = pack_primary_header(pkt_type_tm0_tc1=0, sec_hdr_flag=1, apid=apid,
                              seq_flags=0b11, seq_count=seq, pkt_len=pkt_len)
    return pri + data

# High-level parsers ----------------------------------------------------------

def parse_ccsds_pus(packet: bytes):
    """
    Generic parser that returns:
    {
      'primary': {...},
      'pus': {...},   # TC: ack present; TM: dest_id present
      'app_data': b'...'
    }
    """
    if len(packet) < 6:
        return None
    pri = unpack_primary_header(packet[:6])
    total_after_primary = pri["pkt_len"] + 1
    if len(packet) < 6 + total_after_primary:
        # allow partial; in production you'd loop-recv until full
        return None

    sec = packet[6:11]  # 5 bytes
    app = packet[11:6+total_after_primary]

    if pri["pkt_type"] == 1:  # TC
        pus, app_data = parse_pus_tc_sec_hdr(sec + app[:0])  # sec is 5, app starts after
        # We already sliced sec=5, so app is fine
        return {"primary": pri, "pus": pus, "app_data": app}
    else:  # TM
        pus, app_data_ignored = parse_pus_tm_sec_hdr(sec + app[:0])
        return {"primary": pri, "pus": pus, "app_data": app}
