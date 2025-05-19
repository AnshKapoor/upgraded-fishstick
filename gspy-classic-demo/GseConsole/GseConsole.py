#!/usr/bin/python

import cmd 
import os

from spw_drv import *
from SpaceWire import *
from commands import *

class GseConsole(cmd.Cmd, Cmd_Boot, Cmd_Filesystem, Cmd_SoCWire,\
                 Cmd_Jtag, Cmd_NorFs, Cmd_Nand, Cmd_NandFs, Cmd_Preproc,\
                 Cmd_Acquisition, Cmd_Tests):
        
        def __init__(self, ipython=False): 
                cmd.Cmd.__init__(self)
                #self.bridge = SpaceWireBridgeShimafuji('134.169.116.99', tcp_port=10030)
                #self.bridge = SpaceWireBridgeGresb('134.169.116.224', tcp_port=3004)
                self.bridge = SpaceWireBridgeGresb('134.169.116.205', tcp_port=3000)
                #self.bridge = SpaceWireBridgeGresb('127.0.0.1', tcp_port=3002)
                self.spw = SpaceWire(self.bridge, spw_dest_addr=0x45, ipython=ipython)
        
                self.prompt = ":> "

                Cmd_Boot.__init__(self, self.spw)
                Cmd_Filesystem.__init__(self, self.spw)
                Cmd_SoCWire.__init__(self, self.spw)
                Cmd_Jtag.__init__(self, self.spw)
                Cmd_NorFs.__init__(self, self.spw)
                Cmd_Nand.__init__(self, self.spw)
                Cmd_NandFs.__init__(self, self.spw)
                Cmd_Preproc.__init__(self, self.spw)
                Cmd_Acquisition.__init__(self, self.spw)
                Cmd_Tests.__init__(self, self.spw)

        def __del__(self):
                del self.spw

        def try_exec(self, pycmd):
                try:
                        exec(pycmd)
                except Exception, e:
                        print(str(e))

        def do_shell(self, s):
                os.system(s)
                
        def help_shell(self):
                print("Execute shell commands")

        def do_exec(self, prm):
                if(prm == ''):
                        while True:
                                pycmd = raw_input('>>> ')
                                if(pycmd == 'exit()' or pycmd == 'exit'):
                                        break
                                else:
                                        self.try_exec(pycmd)
                else:
                        self.try_exec(prm)

        def help_exec(self):
                print('Execute Python commands')

        def do_exit(self, prm): 
                return True

        def help_exit(self):
                print('Really?')



parameters = sys.argv
parameters.pop(0)

if(len(parameters) > 0):
        ipython = (parameters[0] == '-ipython')
        if(ipython):
                parameters.pop(0)
else:
        ipython = False
        
parameter_str = ' '.join(parameters)

interpreter = GseConsole(ipython) 
l = interpreter.precmd(parameter_str)
r = interpreter.onecmd(l)
r = interpreter.postcmd(r, l)
if(len(parameters) > 0):
        if(parameters[0] != 'boot'):
                sys.exit()
if not r:
    if ipython:
        from IPython.core.display import display, HTML
        #from IPython import *
        #start_ipython(argv=["notebook"], user_ns={'test':'interpreter'})
        display(HTML('<h1>SoPhi IPython EGSE</h1><hr><p>Commands can be executed using <tt>gse()</tt> within IPython cell</p>'))
             
    else:
        interpreter.cmdloop('SoPhi command line EGSE')

def gse(prm):
        l = interpreter.precmd(prm)
        r = interpreter.onecmd(l)
        r = interpreter.postcmd(r, l)
