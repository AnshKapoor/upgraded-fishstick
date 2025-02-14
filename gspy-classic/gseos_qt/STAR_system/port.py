"""Represents a port on a device.

Brief:\n
    Represents a port on a device.

Copyright:\n
    2022 STAR-Dundee Ltd
"""
import os
from ctypes import *

from STAR_system import CONFIG_LIB, STAR_CONFIG_API_LIB_LOAD_ERROR_STR
from STAR_system.STAR_exceptions import STARAPIError, StatusCode
from STAR_system.STAR_enums import STAR_CONFIG_OP_RESULT, STAR_CFG_PORT_TYPE

StatusCodes = StatusCode()

# Load C API
systemType = os.name
if systemType == ("nt" or "WINDOWS_NT"):
    try:
        config_lib = windll.LoadLibrary(CONFIG_LIB)
    except Exception:
        config_lib = None
        print(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

elif systemType == "posix":
    try:
        config_lib = cdll.LoadLibrary(CONFIG_LIB)
    except Exception:
        config_lib = None
        print(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)


class Port(object):
    """Represents a port on a device.
    
    Attributes:\n
        owningDeviceID (int): The ID of the device which owns the port.
        portNumber (int): The port number.
    """

    def __init__(self, owningDeviceID, portNumber):
        """Constructor:\n
            Initialises a `STAR_system.port.Port` object.

        Args:\n
            owningDeviceID (int): The ID of the device which owns the port.
            portNumber (int): The port number.

        Raises:\n
            TypeError:\n
                owningDeviceID is not an int.\n
                portNumber is not an int.\n
            ValueError:\n
                owningDeviceID is negative.\n
                portNumber is negative.\n
        """

        if type(owningDeviceID) != int:
            raise TypeError("owningDeviceID must be int.")
        if type(portNumber) != int:
            raise TypeError("portNumber must be int.")
        if owningDeviceID < 0:
            raise ValueError("owningDeviceID cannot be negative.")
        if portNumber < 0:
            raise ValueError("portNumber cannot be negative.")

        self.owningDeviceID = owningDeviceID
        self.portNumber = portNumber

    def disableIdentifySourceOnPort(self):
        """Disables source port identification for the port.

        This method is compatible with all devices.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to disable source port identification.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        config_lib.CFG_disableIdentifySourceOnPort.argtypes = [c_uint32, c_uint8]
        config_lib.CFG_disableIdentifySourceOnPort.restype = c_int32

        status = config_lib.CFG_disableIdentifySourceOnPort(c_uint32(self.owningDeviceID),
                                                            c_uint8(self.portNumber))
        
        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

    def disableInterfaceModeOnPort(self):
        """Selectively disables interface mode on the port.\n

        When interface mode is disabled, the device operates in routing mode.
        This method is compatible with all devices.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to disable interface mode.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        config_lib.CFG_disableInterfaceModeOnPort.argtypes = [c_uint32, c_uint8]
        config_lib.CFG_disableInterfaceModeOnPort.restype = c_int32

        status = config_lib.CFG_disableInterfaceModeOnPort(c_uint32(self.owningDeviceID),
                                                           c_uint8(self.portNumber))

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

    def enableIdentifySourceOnPort(self):
        """Enables identification of the source port of a received packet on the
        port, when in interface mode.\n

        Interface mode (`STAR_system.device_config.DeviceConfig.enableInterfaceMode`) and identify source
        (`STAR_system.device_config.DeviceConfig.enableIdentifySource`) must be enabled globally for this to have
        an effect.\n

        This method is compatible with all devices.\n

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to enable source port identification.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        config_lib.CFG_enableIdentifySourceOnPort.argtypes = [c_uint32, c_uint8]
        config_lib.CFG_enableIdentifySourceOnPort.restype = c_int32

        status = config_lib.CFG_enableIdentifySourceOnPort(c_uint32(self.owningDeviceID),
                                                           c_uint8(self.portNumber))
        
        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

    def getIdentifySourceOnPortEnabled(self) -> bool:
        """Gets whether identify source is enabled for a specific port.
        This method is compatible with all devices.\n

        Returns True if identify source on port is enabled, False otherwise.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to determine whether or not source port identification is enabled.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Create pointer to int to be used in function call as argument
        enabled = c_int32(0)
        pEnabled = pointer(enabled)

        # Set argument types and return type of the C function
        config_lib.CFG_getIdentifySourceOnPortEnabled.argtypes = [c_uint32, c_uint8, POINTER(c_int32)]
        config_lib.CFG_getIdentifySourceOnPortEnabled.restype = c_int32

        status = config_lib.CFG_getIdentifySourceOnPortEnabled(c_uint32(self.owningDeviceID),
                                                               c_uint8(self.portNumber), pEnabled)

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

        return bool(enabled.value)

    def enableInterfaceModeOnPort(self):
        """Selectively enables interface mode on the port.

        Interface mode must be enabled globally (`STAR_system.device_config.DeviceConfig.enableInterfaceMode`)
        for interface mode on a port to be enabled.\n

        This method is compatible with all devices.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to enable interface mode.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        config_lib.CFG_enableInterfaceModeOnPort.argtypes = [c_uint32, c_uint8]
        config_lib.CFG_enableInterfaceModeOnPort.restype = c_int32

        status = config_lib.CFG_enableInterfaceModeOnPort(c_uint32(self.owningDeviceID),
                                                          c_uint8(self.portNumber))
        
        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

    def getInterfaceModeOnPortEnabled(self) -> bool:
        """Gets whether interface mode is enabled for the port.

        This method is compatible with all devices.\n

        Returns True if interface mode is enabled on port, False otherwise.\n

        PCI Mk2 and PCIe devices prior to version 1.07 have a bug which 
        means that the value returned in pEnabled is always 0.\n

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to determine whether interface mode is enabled or not.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Create pointer to int to be used in function call as argument
        enabled = c_int32(0)
        pEnabled = pointer(enabled)

        # Set argument types and return type of the C function
        config_lib.CFG_getInterfaceModeOnPortEnabled.argtypes = [c_uint32, c_uint8, POINTER(c_int32)]
        config_lib.CFG_getInterfaceModeOnPortEnabled.restype = c_int32

        status = config_lib.CFG_getInterfaceModeOnPortEnabled(c_uint32(self.owningDeviceID),
                                                              c_uint8(self.portNumber), pEnabled)

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

        return bool(enabled.value)

    def setPortRoutingAddress(self, address):
        """Sets the address a packet received on the port should be routed to 
        when interface mode is enabled.\n

        This is an advanced feature and not necessary for normal usage. Changing the
        port routing address for the config port on a device means that you will
        no longer be able to access any config information.\n

        This method is compatible with all devices.

        Args:\n
            address (int): The new port routing address.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to set the port routing address.\n
            TypeError:\n
                address was not an int.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        if type(address) != int:
            raise TypeError("address must be int.")

        # Set argument types and return type of the C function
        config_lib.CFG_setPortRoutingAddress.argtypes = [c_uint32, c_uint8, c_uint8]
        config_lib.CFG_setPortRoutingAddress.restype = c_int32

        status = config_lib.CFG_setPortRoutingAddress(c_uint32(self.owningDeviceID),
                                                      c_uint8(self.portNumber), c_uint8(address))

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

    def getPortRoutingAddress(self) -> int:
        """Gets and returns the address that a packet received on the port should be routed
        to when interface mode is enabled.\n

        This is an advanced feature and not necessary for normal usage.
        This is compatible with all devices.\n

        PCI Mk2 and PCIe devices prior to version 1.07 have a bug which 
        means that the value returned in pAddress is always 0.
        
        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to get the port routing address.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Create pointer to int to be used in function call as argument
        address = c_uint8(0)
        pAddress = pointer(address)

        # Set argument types and return type of the C function
        config_lib.CFG_getPortRoutingAddress.argtypes = [c_uint32, c_uint8, POINTER(c_uint8)]
        config_lib.CFG_getPortRoutingAddress.restype = c_int32

        status = config_lib.CFG_getPortRoutingAddress(c_uint32(self.owningDeviceID),
                                                      c_uint8(self.portNumber), pAddress)

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

        return address.value

    def clearPortErrors(self):
        """Clears all errors on the port.\n

        Errors on a port are latched until cleared with this function.
        This method is compatible with all devices.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to clear port errors.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Set argument types and return type of the C function
        config_lib.CFG_clearPortErrors.argtypes = [c_uint32, c_uint8]
        config_lib.CFG_clearPortErrors.restype = c_int32

        status = config_lib.CFG_clearPortErrors(c_uint32(self.owningDeviceID),
                                                c_uint8(self.portNumber))

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

    def getPortConnection(self) -> int:
        """Identifies and returns the output port (number) to which the source port is currently
        connected whilst routing its operation.\n

        This method is compatible with all devices.\n

        The output port connected will have a value of 31 if there is no current port connected.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                Could not get port status control.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        try:
            portStatusControl = self.getPortStatusControl()
        except STARAPIError:
            raise

        # Set argument types and return type of the C function
        config_lib.CFG_getPortConnection.argtypes = [c_uint32]
        config_lib.CFG_getPortConnection.restype = c_uint8

        port = config_lib.CFG_getPortConnection(c_uint32(portStatusControl))

        return port

    def getPortStatusControl(self) -> int:
        """Gets and returns the value of a port or link's status/control register.\n
        This method is used by various methods such as `STAR_system.port.Port.getPortType` and
        `STAR_system.port.Port.getPortConnection`.\n

        This method is compatible with all devices.\n
         
        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                The C API failed to get port status control info.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        # Create pointer variable to be used as function argument
        portStatusControl = c_uint32(0)
        pPortStatusControl = pointer(portStatusControl)

        # Set argument types and return type of the C function
        config_lib.CFG_getPortStatusControl.argtypes = [c_uint32, c_uint8, POINTER(c_uint32)]
        config_lib.CFG_getPortStatusControl.restype = c_int32

        status = config_lib.CFG_getPortStatusControl(c_uint32(self.owningDeviceID),
                                                     c_uint8(self.portNumber), pPortStatusControl)

        if status < STAR_CONFIG_OP_RESULT.STAR_SUCCESS.value:
            raise STARAPIError(StatusCodes.getMessage(status))

        return portStatusControl.value

    def getPortType(self) -> STAR_CFG_PORT_TYPE:
        """ Identifies and returns the type of the port.\n

        This method is compatible with all devices.

        Raises:\n
            STARAPIError:\n
                The STAR-Config API library could not be loaded.\n
                Could not get port status control.\n
        """

        # Make sure to protect against invalid STAR-API library
        if config_lib is None:
            raise STARAPIError(STAR_CONFIG_API_LIB_LOAD_ERROR_STR)

        try:
            portStatusControl = self.getPortStatusControl()
        except STARAPIError:
            raise

        # Set argument types and return type of the C function
        config_lib.CFG_getPortType.argtypes = [c_uint32]
        config_lib.CFG_getPortType.restype = STAR_CFG_PORT_TYPE

        portType = config_lib.CFG_getPortType(c_uint32(portStatusControl))

        return portType
