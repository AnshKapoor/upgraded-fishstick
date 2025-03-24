# python code for core/client
from gspynext.core.core import Core
import time
from gspynext.common.enums import Ptype
from gspynext.common.enums import Timeouts

c =  Core()

time.sleep(1)

# test of all available packet types
time.sleep(2)
c.dataHandler.sendQueue.put([0, Ptype.DATA.value, b'\x01\x00\xff'])
print("sent \\x01\\x00\\xff, with 1 being the send channel")
time.sleep(2)
c.dataHandler.sendQueue.put([0, Ptype.CONFIG.value, b'\x01\x64'])
time.sleep(2)
c.dataHandler.sendQueue.put([0, Ptype.RESET.value, b'\x00'])
time.sleep(2)
c.dataHandler.sendQueue.put([0, Ptype.STATUS.value, b'\x00'])
time.sleep(2)
c.dataHandler.sendQueue.put([0, Ptype.BYE.value, b'\x00'])
