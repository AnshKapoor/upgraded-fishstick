#!/usr/bin/python

import sys
from PyQt4.QtCore import pyqtSlot
from PyQt4.QtCore import QObject, pyqtSignal
from PyQt4.QtGui import *
from SpaceWire import *
from Telecommand import *
from SpaceWire_Gresb import *
from SpaceWire_Shimafuji import *

class BootUtility(QWidget):
    trigger = pyqtSignal(str)
        
    def __init__(self):
        QWidget.__init__(self)
        
        self.setWindowTitle('SoPhi Bootloader Utility')
        self.setFixedSize(1000, 240)

        self.bridge = SpaceWire_Shimafuji('134.169.116.99', tcp_port=10030)
        #self.bridge = SpaceWireBridgeGresb('134.169.116.205')
        self.spw = SpaceWire(self.bridge, spw_dest_addr=1)
        self.spw.boot.soft_filename = './dpu_software/SOPHI_DPU.bin'

        # Create a button in the window
        self.btn1 = QPushButton('Select Binary', self)
        self.btn1.setToolTip('Select binary for DPU boot')
        self.btn1.move(10, 205)

        self.btn2 = QPushButton('Reboot', self)
        self.btn2.move(120, 205)
        
        self.btn3 = QPushButton('Test NAND', self)
        self.btn3.move(220, 205)

        self.msgLog = QTextEdit(self)
        self.msgLog.setReadOnly(True)
        self.msgLog.resize(1000, 200)

        self.spw.print_handler = self.print_handler

        # connect the signals to the slots
        self.btn1.clicked.connect(self.selBinary_click)
        self.btn2.clicked.connect(self.reboot_click)
        self.btn3.clicked.connect(self.testNand_click)
        self.trigger.connect(self.msgLog_update)
        
    def print_handler(self, s, fmt='i'):
        color = 'black'
        if fmt == 'i':
            color = 'darkblue'
        elif fmt == 's':
            color = 'darkgreen'
        elif fmt == 'e':
            color = 'darkred'
        elif fmt == 'w':
            color = 'darkorange'
        self.trigger.emit('<br><tt style="color:' + color + ';font-size:12px;">' + s + '</tt>')

    # Create the actions
    @pyqtSlot()
    def selBinary_click(self):
        self.spw.boot.soft_filename = QFileDialog.getOpenFileName(self, 'Select Binary', './dpu_software', '*.bin')

    @pyqtSlot()
    def reboot_click(self):
        self.msgLog.clear()
        payload = struct.pack('>L', 0x8000)
        self.spw.cmd(SpwCmdGrp.System, SystemCmds.SetControlRegister, payload)
        
    @pyqtSlot()
    def testNand_click(self):
        self.spw.cmd(SpwCmdGrp.Nand, NandCmds.ReadUId)
        
    @pyqtSlot(str)
    def msgLog_update(self, msg):
        self.msgLog.insertHtml(msg)
        self.msgLog.ensureCursorVisible()
    
# create our window
app = QApplication(sys.argv)
w = BootUtility()
w.show()
app.exec_()
