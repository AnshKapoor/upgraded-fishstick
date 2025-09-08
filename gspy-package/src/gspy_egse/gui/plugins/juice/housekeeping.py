from PyQt6 import QtCore, QtWidgets, QtGui, uic
from pathlib import Path
from contextlib import suppress
from typing import *


from gspy_egse.gui.plugins.juice.spacewire import SpaceWireConnection
from gspy_egse.gui.utils.plugin import WidgetWithExtension, Setting
from gspy_egse.gui.utils.misc import Extendable, get_bit
from gspy_egse.gui.utils.widget import call_in_main_thread, delay_in_main_thread, async_in_main_thread, \
    select_file, ActivationListener
from gspy_egse.gui.hardware_modules.spacewire import SpaceWire
from gspy_egse.gui.hardware_modules.juice_lib.ramfs import RamFs
from gspy_egse.gui.hardware_modules.juice_lib.housekeeping import Housekeeping
from gspy_egse.gui.hardware_modules.juice_lib.commands import *

from importlib.resources import files, as_file  # stdlib, Python ≥3.9

pkg = "gspy_egse.gui.ui"
ui_name = "houseKeeping.ui"

class RequirePlugins(WidgetWithExtension):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, ext_cls=SpaceWireConnection, identifier="_", sub_exts=[
            Housekeeping
        ], **kwargs)


class HousekeepingWidget(WidgetWithExtension):
    """
    :type spw: SpaceWire | RamFs
    :type connection: SpaceWireConnection
    """

    def __init__(self, *args, **kwargs):
        self.spw, self.connection = (None,) * 2

        super().__init__(*args, plugin_name="SpaceWire", ext_cls=SpaceWireConnection, **kwargs)

    def _delay_init(self, extension=None, _=False):
        self.inherit_settings_from_parent(extension)
        self.connection = extension
        self.spw = self.connection.hardware
        self.spw.add_hk_listener(self.hk_listener)

        hk = None
        with suppress(Exception):
            hk = self.spw.hk
        
        ui_res = files(pkg).joinpath(ui_name)
        with as_file(ui_res) as ui_path:
            self.ui = uic.loadUi(str(ui_path), self)
        # self.ui = uic.loadUi("gspy_egse/gui/ui/houseKeeping.ui", self)
        if hk is not None:
            self.control_switches.set_value(hk["control_reg"])
        self.control_switches.set_names([
            "SOCW_RST_ERR_STAT",
            "_",
            "_",
            "ERROR_CNT_RST",
            "WDOG_CNT_RST",
            "_",
            "GR712_PWR_DOWN",
            "GR712_ERR_RST_EN",
            "GR712_WDOG_RST_EN",
            "_",
            "_",
            "CFPGA_PWR_EN",
            "CFPGA_RST",
            "PSM_EN_N",
            "CWICOM_RST",
            "CWICOM_PWR_EN",
            "NOR_FLASH_PWR_EN_N",
            "NOR_FLASH_RST_N",
            "NOR_FLASH_WP_N",
            "_",
            "NOR_FLASH_BIT1",
            "NOR_FLASH_BIT0"
        ], "ControlRegister")
        self.control_switches.set_listener(self.control_set)
        self.make_settings_btn(self.settings_btn)

        for l in [self.label_disconnect_err, self.label_timeout_err, self.label_address_err,
                  self.label_link_err, self.label_length_err]:
            f = l.font()
            f.setLetterSpacing(QtGui.QFont.PercentageSpacing, 150)
            l.setFont(f)

        if hk is not None:
            self.hk_listener(hk)

    def control_set(self, v, m):
        import struct
        v = struct.pack('>L', v)
        v += struct.pack('>L', m)

        self.spw.cmd(SpwCmdGrp.System, SystemCmds.SetControlRegister, v)

    def hk_listener(self, hk: Dict[str, Union[int, List[int]]]):
        self.label_sw_v.setText("%05d" % hk["sw_version"])
        self.label_hk_c.setText("#%03d" % hk["hk_count"])
        self.load_bar.setValue(hk["proc_load"] / 1000)
        self.label_fpga_time.setText("0x%08X" % hk["fpga_time"])

        self.control_box.setTitle("Control Register (0x%08X)" % hk["control_reg"])
        self.control_switches.set_value(hk["control_reg"])
        self.label_fw_v.setText("%03d.%02d.%01d.%01d.%05d" % (
            get_bit(hk["version_reg"], 24, 31),
            get_bit(hk["version_reg"], 20, 23),
            get_bit(hk["version_reg"], 19),
            get_bit(hk["version_reg"], 16, 18),
            get_bit(hk["version_reg"], 0, 15)))

        self.status_box.setTitle("Status Register (0x%08X)" % hk["status_reg"])
        self.label_err_c.setText("%03d" % get_bit(hk["status_reg"], 24, 31))
        self.label_wdog_c.setText("%03d" % get_bit(hk["status_reg"], 16, 23))

        try:
            self.label_disconnect_err.setText("%s" % format(get_bit(hk["socw_switch"], 0, 3), "04b"))
            self.label_timeout_err.setText("%s" % format(get_bit(hk["socw_switch"], 4, 7), "04b"))
            self.label_address_err.setText("%s" % format(get_bit(hk["socw_switch"], 8, 11), "04b"))
            self.label_link_err.setText("%s" % format(get_bit(hk["socw_switch"], 12, 15), "04b"))
            self.label_length_err.setText("%s" % format(get_bit(hk["socw_switch"], 16, 19), "04b"))
        except:
            import traceback
            traceback.print_exc()


VERSION = 1
NAME = "Housekeeping"
BACKGROUND_TASKS = [RequirePlugins]
