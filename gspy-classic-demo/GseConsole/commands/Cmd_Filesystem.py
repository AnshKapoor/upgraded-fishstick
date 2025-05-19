# import os
# import time
# import sys
# import struct

# from SpaceWire import *


class Cmd_Filesystem(object):
    def __init__(self, spw):
        self.spw = spw

    def do_filelist(self, prm):
        self.spw.cmd(7, 1)

    def do_delete(self, prm):
        p_list = prm.split()

        if len(p_list) < 1:
            print('Invalid parameter')
            return False

        self.spw.cmd(7, 5, p_list[0] + '\x00')

    def do_download(self, prm):
        p_list = prm.split()

        if len(p_list) < 2:
            print('Invalid parameter')
            return False

        self.spw.download_file(p_list[0], p_list[1])

    def do_upload(self, prm):
        p_list = prm.split()

        if len(p_list) < 2:
            print('Invalid parameter')
            return False

        self.spw.upload_file(p_list[0], p_list[1])
