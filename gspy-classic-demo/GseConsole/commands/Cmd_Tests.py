from SpaceWire import *
from tests import *

class Cmd_Tests():

	def __init__(self, spw):
                self.test_nandfs = Test_NandFs(spw)
                self.test_preproc = Test_Preproc(spw)

        def do_test_nandfs(self, prm):
		p_list = prm.split()
		
                self.test_nandfs.test()

        def do_test_preproc(self, prm):
		p_list = prm.split()
		
                self.test_preproc.test()
