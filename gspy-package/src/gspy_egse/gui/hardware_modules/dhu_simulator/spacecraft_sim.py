# mock_spw_server_pus.py
import socket, threading, struct, time
from public import build_pus_tm, parse_ccsds_pus

ACK_ACCEPTANCE = 0b0001
ACK_START      = 0b0010
ACK_PROGRESS   = 0b0100
ACK_COMPLETION = 0b1000

last_tc = {"apid":0, "seq":0, "ack":0, "steps":0, "src":0}
tc_event = threading.Event()

def tcp_send_packet(conn, packet: bytes):
    conn.sendall(struct.pack(">I", len(packet)) + packet)

def handle_tx(conn):
    global last_tc
    try:
        while True:
            hdr = conn.recv(4)
            if not hdr: break
            while len(hdr) < 4:
                more = conn.recv(4 - len(hdr))
                if not more: break
                hdr += more
            if len(hdr) < 4: break
            length = struct.unpack(">I", hdr)[0]
            data = b""
            while len(data) < length:
                chunk = conn.recv(length - len(data))
                if not chunk: break
                data += chunk
            if len(data) < 6:
                continue

            parsed = parse_ccsds_pus(data)
            if not parsed:
                print("[Server TX] Parse failed")
                continue

            pri = parsed["primary"]
            pus = parsed["pus"]
            app = parsed["app_data"]
            if pri["pkt_type"] != 1 or pus["service"] != 1:
                print("[Server TX] Not a PUS TC Svc1")
                continue

            steps = app[0] if len(app) >= 1 else 0
            last_tc = dict(apid=pri["apid"], seq=pri["seq_count"],
                           ack=pus["ack"], steps=steps, src=pus["source_id"])
            print(f"[Server TX] TC Svc1: apid={pri['apid']} seq={pri['seq_count']} ack={pus['ack']:04b} steps={steps}")
            tc_event.set()
    finally:
        conn.close()

def handle_rx(conn):
    try:
        tm_seq = 0
        while True:
            tc_event.wait()
            tc_event.clear()
            apid = last_tc["apid"]
            steps = last_tc["steps"]
            ack  = last_tc["ack"]
            dest = last_tc["src"]  # echo back source_id as destination_id

            if ack & ACK_ACCEPTANCE:
                tm = build_pus_tm(apid, tm_seq, 1, 1, dest)
                tcp_send_packet(conn, tm); tm_seq += 1
                print("[Server RX] TM[1,1]")

            if ack & ACK_START:
                tm = build_pus_tm(apid, tm_seq, 1, 3, dest)
                tcp_send_packet(conn, tm); tm_seq += 1
                print("[Server RX] TM[1,3]")

            if ack & ACK_PROGRESS:
                n = max(1, steps)
                for step in range(1, n+1):
                    tm = build_pus_tm(apid, tm_seq, 1, 5, dest, app_data=bytes([step & 0xFF]))
                    tcp_send_packet(conn, tm); tm_seq += 1
                    print(f"[Server RX] TM[1,5] step={step}")
                    time.sleep(0.03)

            if ack & ACK_COMPLETION:
                tm = build_pus_tm(apid, tm_seq, 1, 7, dest)
                tcp_send_packet(conn, tm); tm_seq += 1
                print("[Server RX] TM[1,7]")
    finally:
        conn.close()

def start_server():
    print("Starting PUS-C Service 1 mock server...")
    tx_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    rx_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    for s, port in ((tx_sock, 3000), (rx_sock, 3001)):
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("127.0.0.1", port))
        s.listen(1)

    print("Listening on 127.0.0.1:3000 (TX) and 3001 (RX)")
    tx_conn, _ = tx_sock.accept(); print("[Server] TX accepted")
    rx_conn, _ = rx_sock.accept(); print("[Server] RX accepted")

    threading.Thread(target=handle_tx, args=(tx_conn,), daemon=True).start()
    threading.Thread(target=handle_rx, args=(rx_conn,), daemon=True).start()
    threading.Event().wait()

if __name__ == "__main__":
    start_server()
