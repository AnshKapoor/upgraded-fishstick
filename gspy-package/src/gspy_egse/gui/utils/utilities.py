"""Utility functions that are being used throughout the example programs.

Brief:\n
    Common utilities used throughout the example programs.

Copyright:\n
    2022 STAR-Dundee Ltd.
"""

import os
import sys

module_path = os.path.abspath(os.path.join(os.path.dirname(__file__),'../'))
sys.path.append(module_path)

from typing import Optional, List

from gspy_egse.gui.STAR_system.STAR_system import STARSystem
from gspy_egse.gui.STAR_system.STAR_exceptions import STARAPIError
from gspy_egse.gui.STAR_system.device import Device

def getInt(prompt) -> int:
    """Gets and returns an integer as input from the user.

    Args:\n
        prompt (str): The prompt to ask the user for input.

    Raises:\n
        TypeError:\n
            prompt is not a str.
    """
    if type(prompt) != str:
        raise TypeError("prompt must be a str.")

    userInput = ""
    while type(userInput) != int:
        userInput = input(prompt)
        try:
            userInput = int(userInput)
        except ValueError:
            print("Input must be an integer. Please try again.")
    return userInput

def promptForDevice(transmitType) -> Optional[Device]:
    """Asks the user which device they would like to use. Returns the selected Device object or returns
    None if no valid device was chosen.

    Args:\n
        transmitType (str): Whether the device is being used for sending or 
            receiving packets. Used to display correct prompt messages. Valid
            values are "send" and "receive".

    Raises:\n
        TypeError:\n
            transmitType is not a str.
        ValueError:\n
            transmitType is not one of "send" and "receive".
    """

    if type(transmitType) != str:
        raise TypeError(f"transmitType must be str. Got {type(transmitType)}.")
    if transmitType not in ["send", "receive"]:
        errorMessage = "Invalid transmitType. Valid values are 'send' and 'receive'"
        raise ValueError(errorMessage)

    # Get the list of available SpaceWire devices.
    starSystem = STARSystem()

    try:
        devices = starSystem.getDeviceList()
    except (STARAPIError, TypeError, ValueError) as err:
        print("Could not get device list: " + str(err))
        devices = None

    # Check that at least one device is present.
    if devices is not None:

        # Print header statement.
        print("The following SpaceWire devices were detected: ")

        # For all devices found on system ...
        for index in range(len(devices)):
            # Get current device.
            device = devices[index]

            try:
                # Get current device name.
                deviceName = device.getDeviceName()

                # Get current device serial number.
                deviceSerial = device.getSerialNumber()
            except STARAPIError:
                print("Error getting device information.")
                deviceName = None
                deviceSerial = None

            if deviceName is not None and deviceSerial is not None:
                # Print current device.
                print(f"{index + 1}: {deviceName} (Serial Number: {deviceSerial})")

        # Send case
        if transmitType == "send":
            # Set transmit type string to "send out of".
            transmitTypeString = "send out of"
        # Receive case
        elif transmitType == "receive":
            # Set transmit type string to "receive into".
            transmitTypeString = "receive into"
        else:
            transmitTypeString = "unknown"

        # Ask which device to use with transmit type string.
        print()
        prompt = (
            "Please enter the number of the device that you would like to"
            f"{transmitTypeString}: "
        )
        try:
            selectedDeviceIndex = getInt(prompt)
        except TypeError as err:
            print("Could not get device index: " + str(err))
            selectedDeviceIndex = 0

        # Check that user input is valid.
        prompt = (
            "Invalid device number. Please enter a number between 1 and "
            f"{len(devices)}"
        )
        while selectedDeviceIndex < 1 or selectedDeviceIndex > len(devices):
            # Ask again.

            try:
                selectedDeviceIndex = getInt(prompt)
            except TypeError as err:
                print("Could not get device index: " + str(err))

        # Decrement selected device index.
        selectedDeviceIndex -= 1

        # Get selected device.
        selectedDevice = devices[selectedDeviceIndex]

        # Return selected device
        return selectedDevice

    return None


def getFirstDevice() -> Optional[Device]:
    """Gets the first device if there is one. Returns the first device available.
    Returns None if no devices are available.
    """
    
    # Get the list of available SpaceWire devices.
    starSystem = STARSystem()

    try:
        devices = starSystem.getDeviceList()
    except (STARAPIError, TypeError, ValueError):
        raise

    # If at least one device is present ...
    if len(devices) > 0:

        # Get first device.
        firstDevice = devices[0]

        # Return first device
        return firstDevice

    return None

def printPacketContents(packetContents):
    """Prints the packet contents as hex byte values separated by spaces.

    Args:\n
        packetContents (list of ints): The packet data to be printed.

    Raises:\n
        TypeError:\n
            packetContents was not a bytes object.
    """

    if isinstance(packetContents, list) is False:
        raise TypeError("packetContents must be a list.")

    # Print packet contents label.
    print(f"Received packet of length {len(packetContents)}, contents: ", end="")

    for packetByte in packetContents:
        print(hex(packetByte), end=" ")

    # Print full stop.
    print(".")

# here is probably still a error in it, because when i uncomment the function call in spacewire_brick_mk4.py there is an error with not founding the firstDevice variabel
def getDevice(self) -> Optional[List[str]]:

    # Get the list of available SpaceWire devices.
    starSystem = STARSystem()

    print("Entering in getDevice()")

    try:
        devices = starSystem.getDeviceList()
    except (STARAPIError, TypeError, ValueError) as err:
        print("Could not get device list: " + str(err))
        devices = None
        
    device_names = []

    # Check that at least one device is present.
    if devices is not None:

        # For all devices found on system ...
        for index in range(len(devices)):
            # Get current device.
            device = devices[index]

            try:
                # Get current device name.
                deviceName = device.getDeviceName()
                device_names.append(deviceName)
            except STARAPIError:
                print("Error getting device information.")

        # Return selected device
        return device_names

    return None
