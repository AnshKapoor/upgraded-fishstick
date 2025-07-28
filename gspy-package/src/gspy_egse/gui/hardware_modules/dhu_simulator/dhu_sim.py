import socket
import struct
from packet import parse_tc_packet
from service1 import generate_tm_responses

def handle_connection(conn, addr):
    print(f"[DHU] Connected from {addr}")
    try:
        while True:
            length_prefix = conn.recv(2)
            if not length_prefix:
                break
            (tc_len,) = struct.unpack(">H", length_prefix)
            tc_data = conn.recv(tc_len)
            if not tc_data:
                break

            print(f"[DHU] Received TC ({tc_len} bytes)")
            try:
                tc = parse_tc_packet(tc_data)
                print(f"[DHU] Parsed TC: APID={tc.apid}, ACK={bin(tc.ack)}, Seq={tc.seq_count}")
                tm_packets = generate_tm_responses(tc)
                for tm in tm_packets:
                    tm_len = len(tm)
                    conn.sendall(struct.pack(">H", tm_len) + tm)
                    print(f"[DHU] Sent TM[{tm[7]},{tm[8]}] ({tm_len} bytes)")
            except Exception as e:
                print(f"[DHU] Error: {e}")

    finally:
        conn.close()
        print(f"[DHU] Disconnected: {addr}")


def run_dhu_server(host='0.0.0.0', port=5000):
    print(f"[DHU] Starting DHU Simulator on {host}:{port}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((host, port))
        server.listen()
        while True:
            conn, addr = server.accept()
            handle_connection(conn, addr)


if __name__ == "__main__":
    run_dhu_server()
