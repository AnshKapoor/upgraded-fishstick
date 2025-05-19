import os
import sys
import struct
from Telecommand import *


class Acquisition():

	def __init__(self, spw):
                self.spw = spw

        def capture(self, num_frames=1, num_iter=1, num_acc=1):
                payload = struct.pack('>B', num_frames)
                payload += struct.pack('>B', num_iter)
                payload += struct.pack('>B', num_acc)
                self.spw.cmd(SpwCmdGrp.Acquisition, AcquisitionCmds.ChlinkRecord, payload)

        def readout(self, num_frames=1):
                payload = struct.pack('>B', num_frames)
                self.spw.events.SoCWRxDone.clear()
                self.spw.cmd(SpwCmdGrp.Acquisition, AcquisitionCmds.ChlinkReadout, payload)
                self.spw.events.SoCWRxDone.wait(60.0)

        def capture16(self, num_frames=1):
                payload = struct.pack('>B', num_frames)
                self.spw.cmd(SpwCmdGrp.Acquisition, AcquisitionCmds.ChlinkRecord16, payload)

        def readout16(self, num_frames=1):
                payload = struct.pack('>B', num_frames)
                self.spw.events.SoCWRxDone.clear()
                self.spw.cmd(SpwCmdGrp.Acquisition, AcquisitionCmds.ChlinkReadout16, payload)
                self.spw.events.SoCWRxDone.wait(60.0)

        def compare(self, data, filename):
                size = os.path.getsize(filename)
                file = open(filename, 'rb')
                n, last_part = divmod(size, 512)

                for i in range(0, n, 1):
                        ref_data = file.read(512)
                        if(data[i*512:(i+1)*512] != ref_data):
                                file.close()
                                return False
                        
                if last_part > 0:
                        ref_data = file.read(last_part)
                        if(data[n*512:n*512+last_part] != ref_data):
                                file.close()
                                return False
        
                file.close()
                return True

