from sophilib import Acquisition
from sophilib import TestVector

class Cmd_Acquisition():

	def __init__(self, spw):
                self.spw = spw
                self.acquisition = Acquisition(self.spw)

        def do_acq_capture(self, prm):
                p_list = prm.split()

                if(len(p_list) < 1):
                        num_frames = 1
                        num_iter = 1
                        num_acc = 1
                elif(len(p_list) < 2):
                        num_frames = int(p_list[0], 0)
                        num_iter = 1
                        num_acc = 1
                elif(len(p_list) < 3):
                        num_frames = int(p_list[0], 0)
                        num_iter = int(p_list[1], 0)
                        num_acc = 1
                else:
                        num_frames = int(p_list[0], 0)
                        num_iter = int(p_list[1], 0)
                        num_acc = int(p_list[2], 0)

                self.acquisition.capture(num_frames, num_iter, num_acc)
        
        def do_acq_readout(self, prm):
                p_list = prm.split()

                if(len(p_list) < 1):
                        num_frames = 1
                else:
                        num_frames = int(p_list[0], 0)

                self.acquisition.readout(num_frames)

        def do_acq_capture16(self, prm):
                p_list = prm.split()

                if(len(p_list) < 1):
                        num_frames = 1
                else:
                        num_frames = int(p_list[0], 0)

                self.acquisition.capture16(num_frames)

        def do_acq_readout16(self, prm):
                p_list = prm.split()

                if(len(p_list) < 1):
                        num_frames = 1
                else:
                        num_frames = int(p_list[0], 0)

                self.acquisition.readout16(num_frames)

        def do_acq_show(self, prm):
                data = self.spw.download_file('fimage.raw')
                tv = TestVector()
                tv.ret_image32(data)
             
