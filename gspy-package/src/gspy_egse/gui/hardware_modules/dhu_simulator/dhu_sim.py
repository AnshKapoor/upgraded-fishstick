# test_client_pus.py
import struct, time
from gspy_egse.gui.hardware_modules.spacewire_gresb import SpaceWireBridgeGresb
from pus_ccsds import build_pus_tc, parse_ccsds_pus

ACK_ACCEPTANCE = 0b0001
ACK_START      = 0b0010
ACK_PROGRESS   = 0b0100
ACK_COMPLETION = 0b1000

def tcp_send_with_len(bridge: SpaceWireBridgeGresb, payload: bytes):
    bridge.send(payload)

def main():
    bridge = SpaceWireBridgeGresb("127.0.0.1", 3000)
    bridge.open()
    if not bridge.is_open:
        print("Bridge open failed")
        return

    apid = 0x0042
    seq  = 1
    src  = 0x1234
    steps = 3
    ack = ACK_ACCEPTANCE | ACK_START | ACK_PROGRESS | ACK_COMPLETION

    tc = build_pus_tc(apid, seq, service=1, subservice=0,
                      ack_nibble=ack, source_id=src, app_data=bytes([steps]))
    print(f"[Client] Send PUS TC Svc1: apid={apid} seq={seq} ack={ack:04b} steps={steps}")
    tcp_send_with_len(bridge, tc)

    expected = []
    if ack & ACK_ACCEPTANCE: expected.append(1)
    if ack & ACK_START:      expected.append(3)
    if ack & ACK_PROGRESS:   expected.extend([5]*max(1, steps))
    if ack & ACK_COMPLETION: expected.append(7)

    deadline = time.time() + 5.0
    while expected and time.time() < deadline:
        tm = bridge.receive()
        if not tm:
            continue
        parsed = parse_ccsds_pus(tm)
        if not parsed or parsed["primary"]["pkt_type"] != 0:
            print("[Client] Non-TM or parse fail"); continue
        pri, pus, app = parsed["primary"], parsed["pus"], parsed["app_data"]
        sub = pus["subservice"]
        if sub == 5 and app:
            print(f"[Client] TM[1,5] step={app[0]}")
        else:
            print(f"[Client] TM[1,{sub}]")

        if expected and expected[0] == sub:
            expected.pop(0)
        elif sub == 5 and 5 in expected:
            expected.remove(5)

    if not expected:
        print("[Client] Service 1 flow complete ✅")
    else:
        print("[Client] Missing:", expected)

    bridge.close()

if __name__ == "__main__":
    main()
