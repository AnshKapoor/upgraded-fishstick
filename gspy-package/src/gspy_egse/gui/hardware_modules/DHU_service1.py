ACK_ACCEPTANCE = 0b0001
ACK_START = 0b0010
ACK_PROGRESS = 0b0100
ACK_COMPLETION = 0b1000

import struct

class TCPacket:
    def __init__(self, raw_bytes):
        self.raw = raw_bytes
        self.version_type_df, self.apid = struct.unpack(">H", raw_bytes[0:2])[0] >> 13, raw_bytes[0:2][0] & 0x07FF
        self.seq_flags, self.seq_count = (raw_bytes[2] >> 6), ((raw_bytes[2] & 0x3F) << 8) | raw_bytes[3]
        self.service_type = raw_bytes[6]
        self.service_subtype = raw_bytes[7]
        self.source_id = raw_bytes[8]
        self.ack_flags = raw_bytes[9]  # Assumed for this use-case
        self.app_data = raw_bytes[10:]

class TMPacket:
    def __init__(self, tc_packet: TCPacket, subtype: int, extra_data: bytes = b''):
        self.service_type = 1  # Always Service 1 for this simulation
        self.subtype = subtype
        self.source_id = tc_packet.source_id
        self.version_type_df = tc_packet.version_type_df
        self.apid = tc_packet.apid
        self.seq_flags = tc_packet.seq_flags
        self.seq_count = tc_packet.seq_count
        self.extra_data = extra_data

    def build(self):
        # Header (simplified)
        primary_header = struct.pack(">H", (self.version_type_df << 13) | self.apid)
        primary_header += struct.pack(">H", (self.seq_flags << 14) | self.seq_count)
        length = 3 + len(self.extra_data)
        primary_header += struct.pack(">H", length)

        # Data field
        data = struct.pack("BBB", self.service_type, self.subtype, self.source_id)
        data += self.extra_data
        return primary_header + data

class DHUSimulator:
    def __init__(self):
        self.tm_sent = []

    def parse_and_respond(self, raw_tc: bytes):
        tc = TCPacket(raw_tc)
        if tc.ack_flags & ACK_ACCEPTANCE:
            self.send_tm(tc, subtype=1)
        if tc.ack_flags & ACK_START:
            self.send_tm(tc, subtype=3)
        if tc.ack_flags & ACK_PROGRESS:
            step_id = tc.app_data[0] if tc.app_data else 0
            self.send_tm(tc, subtype=5, extra_data=bytes([step_id]))
        if tc.ack_flags & ACK_COMPLETION:
            self.send_tm(tc, subtype=7)

    def send_tm(self, tc_packet, subtype, extra_data=b''):
        tm = TMPacket(tc_packet, subtype=subtype, extra_data=extra_data)
        packet = tm.build()
        self.tm_sent.append(packet)
        print(f"[TM Sent] Subtype {subtype}, Bytes: {packet.hex()}")
