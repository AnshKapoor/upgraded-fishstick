from ..spacewire import *
from .commands import *
import threading

class BrickMk4:
    """_summary_
    The BrickMk4 class is the connector to the base class SpaceWire(Extendable)
    from the module hardware_modules/spacewire.py
    It is the actual class which stands for the hardware implementation,
    so the higher modules can get access to the hardware.
    """
    
    def __init__(self, spw: SpaceWire, check_for_module=False):
        if not isinstance(spw, SpaceWire):
            spw = spw.hardware  # type: SpaceWire

        if spw.has_extension(self):
            if check_for_module:
                raise ValueError("SpaceWire Object already has %s extension!" % self.__class__.__name__)
            return
        self.spw = spw
        spw.add_extension(self, extend_methods=True)
                
    def spw_send(self, packetData: list[int], address: list[int]):
        self.spw.set_spw_dest_addr(address)
        self.spw.send(packetData)
    '''
    reveice function: call_async(self.receive_thread) of hardware_modules.spacewire.py will be called asynchronously when any data arrives
    '''
    def getDeviceName(self) -> List[str]:
        deviceName = self.spw.spw_raw.firstDevice.getDeviceName()
        return deviceName
        
    def spw_resetDevice(self):
        threading.Thread(self._spw_resetDevice()).start()
        
    def _spw_resetDevice(self):
        self.spw.spw_raw.reset_Spw_Device()

    def spw_setTransmitSignallingRate(self, bitRateMbitSec, linkNum):
        self.spw.spw_raw.spw_raw_setTransmitSignallingRate(bitRateMbitSec, linkNum)
    
    def spw_getTransmitSignallingRate(self):
        transmitClockLink_1, transmitClockLink_2 = self.spw.spw_raw.spw_raw_getTransmitSignallingRate()
        return  transmitClockLink_1, transmitClockLink_2
    
    def spw_set_transmit_receive_channel_number(self, transmitChannelNumber, receiveChannelNumber):
        if(transmitChannelNumber != self.spw.spw_raw.prevTransmitChannel):
            self.spw.spw_raw.transmitChannel =  transmitChannelNumber
            self.spw.spw_raw.prevTransmitChannel = self.spw.spw_raw.transmitChannel
            self.spw.spw_raw.receiveChannel =  receiveChannelNumber
            self.spw.spw_raw.prevReceiveChannel = self.spw.spw_raw.receiveChannel

    def spw_setMultiplePacket(self, boolState):
        if(boolState == True):
            self.spw.spw_raw.setMultiplePacket(True)
        else:
            self.spw.spw_raw.setMultiplePacket(False)

    def spw_waitEvent(self):
        self.spw.spw_raw.waitEvent()
