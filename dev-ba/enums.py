from enum import Enum


class Ptype(Enum):
    """Enum class for better payload type readability"""
    HELLO = 0
    CONFIG = 10
    DATA = 20
    STATUS = 30
    BUSY = 40
    HEARTBEAT = 50
    BYE = 60
