from SpaceWire import *
from tests import *
from sophilib import Jtag
from sophilib import Nand
from sophilib import Preproc
from sophilib import RamFs

import numpy as np
import matplotlib.pyplot as plt
import scipy.misc as spy
import matplotlib.image as mpimg

class Test_NandFs():

	def __init__(self, spw):
                self.spw = spw
                self.jtag = Jtag(spw)
                self.nand = Nand(spw)
                self.preproc = Preproc(spw)
                self.ramfs = RamFs(spw)
                
        def test(self):
                part = 2
                file_start = 0
                set_count = 100
                
                self.jtag.config('bitfiles/preproc.bit', 2)
                self.nand.nandfs_mount(part)

                for i in range(2 * set_count):
                        self.nand.nandfs_delete(file_start + i, part)
                
                image1 = mpimg.imread('testdata/QM2.png')
                image1 = spy.imresize(image1, [512, 512])[:,:,0]
                image1 = np.floor(image1)
                image1 = np.int32(image1)
                payload = bytearray(image1)
                self.preproc.store_direct(payload, 0x00000000)
                
                image2 = mpimg.imread('testdata/etower.tif')
                image2 = np.floor(image2)
                image2 = np.int32(image2)
                payload = bytearray(image2)
                self.preproc.store_direct(payload, 0x00100000)
                
                for i in range(set_count):
                        self.preproc.load_to_nand(0x00000000, 0x000200, part, file_start + 2*i) # 0x020000
                        print('Small image done')
                        #self.preproc.load_to_nand(0x00100000, 0x200000, part, file_start + 2*i + 1)
                        #print('Large image done')
                        print(i)
                """
                # Short test:                
                data = self.preproc.load_direct(0x00100000, 0x200000)
                c = np.frombuffer(data, np.int32)
                c = c.reshape([2048, 2048])
                plt.imshow(c)
                plt.show()
                """

        def test_cpu(self):
                part = 2
                file_num = 1
                
                self.nand.nandfs_mount(part)
                image1 = mpimg.imread('testdata/QM2.png')
                image1 = spy.imresize(image1, [2048, 2048])[:,:,0]
                image1 = np.floor(image1)
                image1 = np.int32(image1)
                payload = bytearray(image1)
                self.spw.upload_data('store.raw', payload)

                self.nand.nandfs_copy_from_ramfs('store.raw', file_num, part)

        def test_cpu_eval(self, file_num):
                part = 2
                #file_num = 0
                
                self.nand.nandfs_mount(part)
                self.nand.nandfs_copy_to_ramfs('store.raw', file_num, part)

                data = self.spw.download_file('store.raw')
                self.ramfs.delete('store.raw')
                c = np.frombuffer(data, np.int32)
                c = c.reshape([2048, 2048])
                #c = c.reshape([512, 512])
                plt.imshow(c)
                plt.show()

        def test_delete_all(self):
                part = 2
                self.nand.nandfs_mount(part)

                for i in range(1000):
                        self.nand.nandfs_delete(i, part)
                
                
