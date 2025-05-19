"""Contains functions to operate the SPI interface of the Onyx device.
The functions to control the SPi device originate from the Onyx.Net.dll, which is a .NET assembly.
The Onyx.Net.dll depends on the FTDI2XX.dll and System.dll assemblies.
The FTDI2XX.dll is a library that provides the driver for the FTDI USB to SPI converter.

To have a more detailed understanding into the Onyx.Net.dll, please use a dll decompiler, such as dnSpy, IlSpy, or dotPeek.
Or you can use Microsoft's Visual Studio to open the OnyxAPI_NET.dll and see the classes and functions in the object browser, by passing the
OnyxAPI_NET.dll as an dependency to your project.

The clr module is used to add the .NET assemblies as references and to import the classes and functions from the OnyxAPI_NET.dll.

Brief:\n
    Functions to operate the SPI interface of the Onyx device.

Copyright:\n
    DEICO Mühendislik A.Ş.
"""

# import clr
import sys
import os
import time

try:
    from ...utils.misc import WrappedMessageHandler
except (ValueError, ImportError):
    from utils.misc import WrappedMessageHandler

# Add the path to the OnyxAPI_NET.dll
module_path = os.path.abspath(os.path.join(os.path.dirname(__file__),'./'))
sys.path.append(module_path)


# Add references to the .NET assemblies
# clr.AddReference('Onyx.NET')
# clr.AddReference('FTDI2XX')
# clr.AddReference("System")

# from onyx_dotnet_api import DeviceInformation, OperationMode, SPI_Polarity, SPI_Phase, SPI_Speed, Status, AvailableAsyncData


class SPIConsole:
    
    def __init__(self, master_mode=True):
        self.Master = master_mode

        self.myDevice = None
        self.onyxStatus = None
        self.rxBytes = []
        self.exchangedByteCount = 0
        self.messageHandler = WrappedMessageHandler(None, "SPIConsole")

        if not self.find_and_connect_device('DC000024A'):
            return
        self.configure_device()

    def find_and_connect_device(self, serial_number):
        deviceList = [] # DeviceInformation.ListDevices()   s
        self.myDevice = next((device for device in deviceList if device.SerialNumber == serial_number), None)
        
        if self.myDevice is None:
            self.messageHandler.error(f"Device with serial number {serial_number} not found")
            return False

        self.myDevice.Connect()
        return True

    def configure_device(self):
        if self.myDevice:
            self.onyxStatus = self.myDevice.SetOperationMode(OperationMode.SPI_GPIO)
            if(self.onyxStatus == Status.ONYX_OK):
                self.operationMode = OperationMode.SPI_GPIO
            else:
                self.messageHandler.error("Failed to set operation mode")
                self.close()

            if self.Master:
                self.master_device()
            else:             
                self.slave_device()
            
    def spi_Master_Write(self, txBytes):
        dummyValueRxBytes = []
        dummyValueExchangedByteCount = 0
        self.onyxStatus, self.rxBytes, self.exchangedByteCount = self.myDevice.SPI.MasterExchange(0, txBytes, dummyValueRxBytes, len(txBytes), dummyValueExchangedByteCount)    
    
    def master_device(self):
        self.messageHandler.info("SPI as Master device")

        self.onyxStatus = self.myDevice.SPI.SetConfig(SPI_Polarity.POLARITY_RISING_FALLING, SPI_Phase.PHASE_SAMPLE_SETUP)
        if(self.onyxStatus == Status.ONYX_OK):
            pass
        else:
            self.messageHandler.error("Failed to set config")
            self.close()

        dummy_Set_Speed = SPI_Speed(195000) # has no real value, it is just a dummy value to fulfill the function prototype
        SPI_Speed_set = SPI_Speed(195000)
        self.onyxStatus, self.actual_Set_Speed = self.myDevice.SPI.SetSpeed(SPI_Speed_set, dummy_Set_Speed)
        if(self.onyxStatus == Status.ONYX_OK):
            pass
        else:
            self.messageHandler.error("Failed to set speed")
            self.close()

    def slave_device(self):
        self.messageHandler.info("SPI as Slave device")
        
        self.myDevice.SPI.SlaveEnable()
        slaveResponse = [0x00, 0xff, 0xff]
        setSlaveResponseLengthDummy = 0
        slaveStatus, setSlaveResponseLength = self.myDevice.SPI.SlaveSetResponse(slaveResponse, setSlaveResponseLengthDummy)
        if(slaveStatus == Status.ONYX_OK):
            pass
        else:
            self.messageHandler.error("Failed to set slave response")
            self.close()        

    def slave_read(self):

        availableAsyncData = AvailableAsyncData()
        dummyAvailableAsyncData = AvailableAsyncData()

        while not availableAsyncData.AnyData():
            print("Waiting for data...")
            self.onyxStatus, availableAsyncData = self.myDevice.AsyncPoll(dummyAvailableAsyncData)
            time.sleep(100)

        slaveReceivedByteCount = availableAsyncData.AvailableSPIsReadBytes

        if (slaveReceivedByteCount > 0):
            dummySlaveRxBytes = []
            dummyActualReadByteCount = 0
            self.onyxStatus, self.rxBytes, self.exchangedByteCount = self.myDevice.SPI.SlaveRead(slaveReceivedByteCount, dummySlaveRxBytes, dummyActualReadByteCount)

    def disableSlaveDevice(self):
        self.myDevice.SPI.SlaveDisable()

    def close(self):
        self.myDevice.Disconnect()
        return