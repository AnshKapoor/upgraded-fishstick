from ..spacewire import *
from .commands import *
from typing import *
from pathlib import Path
import os

try:
    from ...utils.misc import iter_unpack, iter_unpack_list
except (ValueError, ImportError):
    from utils.misc import iter_unpack, iter_unpack_list


class Housekeeping:
    def __init__(self, spw: SpaceWire, check_for_module=False):
        if not isinstance(spw, SpaceWire):
            spw = spw.hardware  # type: SpaceWire

        if spw.has_extension(self):
            if check_for_module:
                raise ValueError("SpaceWire Object already has %s extension!" % self.__class__.__name__)
            return
        self.spw = spw
        self.hk = None
        spw.add_extension(self, extend_methods=True)
        spw.add_decode_listener(self._spw_listener_hk)
        self.listeners: List[Callable[[Dict[str, Union[int, List[int]]]], None]] = []

    def add_hk_listener(self, listener: Callable[[Dict[str, Union[int, List[int]]]], None]):
        self.listeners.append(listener)

    def remove_hk_listener(self, listener: Callable[[Dict[str, Union[int, List[int]]]], None]):
        self.listeners.remove(listener)

    def _spw_listener_hk(self, message):
        # Housekeeping?
        if message[0] == 0xaa:
            message = bytearray(message)[1:]
            self.hk = {
                'hk_count': iter_unpack(message, 'UCHAR'),
                'rsvd1': iter_unpack(message, 'UCHAR'),
                'rsvd2': iter_unpack(message, 'UCHAR'),
                'version_reg': iter_unpack(message, 'ULONG'),
                'sw_version': iter_unpack(message, 'ULONG'),
                'control_reg': iter_unpack(message, 'ULONG'),
                'status_reg': iter_unpack(message, 'ULONG'),
                'fpga_time': iter_unpack(message, 'ULONG'),
                'socw_switch': iter_unpack(message, 'ULONG'),
                'socw_ifs': iter_unpack(message, 'ULONG'),
                'proc_load': iter_unpack(message, 'ULONG'),
                'auc_socp_nodes': iter_unpack_list(message, 12 * 8, 'UCHAR', length_in_bits=True),
                'sefi_far_count': iter_unpack(message, 'ULONG'),
                'sefi_ctlstat_count': iter_unpack(message, 'ULONG'),
                'seu_cleared_count': iter_unpack(message, 'ULONG'),
                'seu_sticky_count': iter_unpack(message, 'ULONG'),
                'auc': iter_unpack_list(message, len(message), 'UCHAR')
            }

            to_delete = []
            for l in self.listeners:
                try:
                    l(self.hk)
                except (Exception,):
                    to_delete.append(l)
            for l in to_delete:
                self.remove_hk_listener(l)

            message = bytes()  # message[148:]
            return message
