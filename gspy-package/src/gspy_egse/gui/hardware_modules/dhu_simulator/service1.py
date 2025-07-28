from constants import *
from packet import build_tm_packet

def is_ack_flag_set(flags, flag):
    return (flags & flag) != 0

def generate_tm_responses(tc):
    tm_packets = []

    # TM[1,1] - Acknowledgement of receipt
    if is_ack_flag_set(tc.ack, ACK_ACCEPTANCE):
        tm_packets.append(
            build_tm_packet(
                PUS_SERVICE_REQUEST_VERIFICATION,
                PUS_SUBSERVICE_REQUEST_ACK_SUCCESSFUL,
                tc.seq_count
            )
        )

    # TM[1,3] - Successful start of execution
    if is_ack_flag_set(tc.ack, ACK_START):
        tm_packets.append(
            build_tm_packet(
                PUS_SERVICE_REQUEST_VERIFICATION,
                PUS_SUBSERVICE_REQUEST_START_SUCCESSFUL,
                tc.seq_count
            )
        )

    # TM[1,5] - Progress report (step ID = 1)
    if is_ack_flag_set(tc.ack, ACK_PROGRESS):
        tm_packets.append(
            build_tm_packet(
                PUS_SERVICE_REQUEST_VERIFICATION,
                PUS_SUBSERVICE_REQUEST_SUCCESSFUL_PROGRESS,
                tc.seq_count,
                step_id=1
            )
        )

    # TM[1,7] - Successful completion
    if is_ack_flag_set(tc.ack, ACK_COMPLETION):
        tm_packets.append(
            build_tm_packet(
                PUS_SERVICE_REQUEST_VERIFICATION,
                PUS_SUBSERVICE_REQUEST_SUCCESSFUL_COMPLETION,
                tc.seq_count
            )
        )

    return tm_packets
