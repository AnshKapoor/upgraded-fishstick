import socket
import struct
from packet import build_tc_packet, parse_tm_packet
from constants import *

def send_tc_and_receive_tm(sock, ack_flags, seq_count, step_id=1):
    # 构造 TC Packet with custom ACK and Seq
    tc_packet = build_tc_packet(ack_flags=ack_flags, seq_count=seq_count, step_id=step_id)

    # 添加长度前缀
    packet_len = len(tc_packet)
    framed_tc = struct.pack(">H", packet_len) + tc_packet

    sock.sendall(framed_tc)
    print(f"\n[SC] Sent TC#{seq_count} with ACK={bin(ack_flags)}")

    # 接收所有 TM 回复（最大 4 个）
    tm_count = bin(ack_flags).count('1')
    for i in range(tm_count):
        length_bytes = sock.recv(2)
        if not length_bytes:
            break
        (tm_len,) = struct.unpack(">H", length_bytes)
        tm_bytes = sock.recv(tm_len)
        if not tm_bytes:
            break

        parsed = parse_tm_packet(tm_bytes)
        print(f"[SC] Received TM[{parsed['service']},{parsed['subservice']}] seq={parsed['seq_count']}, data={parsed['data']}")

def run_batch_test():
    # 定义 ACK 测试组合（你可自由增减）
    ack_list = [
        ACK_ACCEPTANCE,               # Only 1
        ACK_ACCEPTANCE | ACK_START,  # 1 + 3
        ACK_ACCEPTANCE | ACK_PROGRESS,       # 1 + 5
        ACK_ACCEPTANCE | ACK_COMPLETION,     # 1 + 7
        ACK_ACCEPTANCE | ACK_PROGRESS | ACK_COMPLETION,  # 1 + 5 + 7
        0x0F  # All
    ]

    with socket.create_connection(('127.0.0.1', 5000)) as sock:
        for i, ack in enumerate(ack_list, start=1):
            step_id = i  # 自定义 step_id 与 TC 编号相同
            send_tc_and_receive_tm(sock, ack_flags=ack, seq_count=i, step_id=step_id)

if __name__ == "__main__":
    run_batch_test()
