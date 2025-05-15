import sys
from time import sleep

sys.path.append("../gseos_qt")
try:
    from ..gseos_qt.hardware_modules.spacewire import SpaceWire
    from ..gseos_qt.hardware_modules.spacewire_gresb import SpaceWireBridgeGresb
    from ..gseos_qt.hardware_modules.juice_lib.ramfs import RamFs
    from ..gseos_qt.utils.misc import test_func
    from ...hardware_modules.juice_lib.commands import *
except (ValueError, ImportError):  # modules can be found from PATH
    from hardware_modules.spacewire import SpaceWire
    from hardware_modules.spacewire_gresb import SpaceWireBridgeGresb
    from hardware_modules.juice_lib.ramfs import RamFs
    from utils.misc import test_func
    from hardware_modules.juice_lib.commands import *


@test_func()
def open():
    """ Opening Connection """
    global s

    s = SpaceWire(SpaceWireBridgeGresb())
    s.cmd_substitute(SpwCmdGrp.RamFs, RamFsCmds.Open, 2048)
    s.cmd_substitute(SpwCmdGrp.RamFs, RamFsCmds.Close, 2049)
    s.cmd_substitute(SpwCmdGrp.RamFs, RamFsCmds.Delete, 2050)
    s.cmd_substitute(SpwCmdGrp.RamFs, RamFsCmds.PrintFileList, 2051)
    # s.cmd_substitute(SpwCmdGrp.RamFs, RamFsCmds._CONFIG, 2052)
    s.cmd_substitute(SpwCmdGrp.RamFs, RamFsCmds.Exists, 2053)
    s.cmd_substitute(SpwCmdGrp.RamFs, RamFsCmds.Format, 2055)
    s.cmd_substitute(SpwCmdGrp.RamFs, RamFsCmds.DownloadToGround, 2066)
    s.cmd_substitute(SpwCmdGrp.RamFs, RamFsCmds.DeleteOpen, 2073)


@test_func(exceptions=AttributeError)
def del_1():
    """ Trying to delete file """
    s.file_delete("tmp")


@test_func()
def add_1():
    """ Adding Module """
    RamFs(s, True)


@test_func(exceptions=ValueError)
def add_2():
    """ Adding Module """
    RamFs(s, True)


@test_func()
def del_2():
    """ Trying to delete file """
    s.file_delete("tmp")


@test_func()
def close():
    """ Closing Connection """
    s.close()


s = None
open()
del_1()
add_1()
add_2()
del_2()
close()
