import struct

from SpaceWire import *
from Telecommand import *

class NandFs():

	def __init__(self, spw):
                self.spw = spw

        def nandfs_mount(self, part=1):
                """Mount NAND-Flash filesystem partition"""

                self.spw.events.NandFsMounted.clear()
                
                if(part != 1 and part != 2):
                        return
                payload = struct.pack('>B', part)
                self.spw.cmd(SpwCmdGrp.NandFs, NandFsCmds.Mount, payload)
                self.spw.events.NandFsMounted.wait(50)

        def nandfs_umount(self, part=1):
                """Umount NAND-Flash filesystem partition"""
                
                if(part != 1 and part != 2):
                        return
                payload = struct.pack('>B', part)
                self.spw.cmd(SpwCmdGrp.NandFs, NandFsCmds.Unmount, payload)

        def nandfs_format(self, part=1):
                """Format partition of NAND-Flash filesystem"""
                
                if(part != 1 and part != 2):
                        return
                payload = struct.pack('>B', part)
                self.spw.cmd(SpwCmdGrp.NandFs, NandFsCmds.Format, payload)

        def nandfs_clean(self, part=1):
                """Delete marked files on NAND-Flash filesystem partition"""
                
                if(part != 1 and part != 2):
                        return
                payload = struct.pack('>B', part)
                self.spw.cmd(SpwCmdGrp.NandFs, NandFsCmds.Clean, payload)
        
        def nandfs_exists(self, fileno, part=1):
                """Check if file exists on NAND-Flash filesystem partition"""
                
                if(part != 1 and part != 2):
                        return
                payload = struct.pack('>B', part)
                payload += struct.pack('>L', fileno)
                self.spw.cmd(SpwCmdGrp.NandFs, NandFsCmds.Exists, payload)

        def nandfs_delete(self, fileno, part=1):
                """Delete file on NAND-Flash filesystem partition"""
                
                if(part != 1 and part != 2):
                        return
                payload = struct.pack('>B', part)
                payload += '\x00\x00\x00'
                payload += struct.pack('>L', fileno)
                self.spw.cmd(SpwCmdGrp.NandFs, NandFsCmds.Erase, payload)

        def nandfs_list(self, part=1):
                """List files of NAND-Flash filesystem partition"""
                
                if(part != 1 and part != 2):
                        return
                payload = struct.pack('>B', part)
                self.spw.cmd(SpwCmdGrp.NandFs, NandFsCmds.PrintFiles, payload)

        def nandfs_printfat(self, part=1):
                """Print file allocation table of NAND-Flash filesystem partition"""
                
                if(part != 1 and part != 2):
                        return
                payload = struct.pack('>B', part)
                self.spw.cmd(SpwCmdGrp.NandFs, NandFsCmds.PrintFAT, payload)

        def nandfs_copy_from_ramfs(self, filename_dpu, fileno, part=1):
                """Copy file from SDRAM filesystem to NAND-Flash filesystem"""
                
                if(part != 1 and part != 2):
                        return
                payload = struct.pack('>B', part)
                payload += filename_dpu[:18].ljust(20, '\x00')
                payload += struct.pack('>L', fileno)
                self.spw.cmd(SpwCmdGrp.NandFs, NandFsCmds.WriteFromMMviaSoCWire, payload)

        def nandfs_copy_to_ramfs(self, filename_dpu, fileno, part=1):
                """Copy file from NAND-Flash filesystem to SDRAM filesystem"""
                
                if(part != 1 and part != 2):
                        return
                payload = struct.pack('>B', part)
                payload += filename_dpu[:18].ljust(20, '\x00')
                payload += struct.pack('>L', fileno)
        
                self.spw.events.SoCWRxDone.clear()
                self.spw.cmd(SpwCmdGrp.NandFs, NandFsCmds.ReadToMMviaSoCWire, payload)
                self.spw.events.SoCWRxDone.wait(60)

        
