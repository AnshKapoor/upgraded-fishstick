import time

from gspy_egse.gui.STAR_system.STAR_system import STARSystem
from gspy_egse.gui.STAR_system.STAR_exceptions import STARAPIError
from gspy_egse.gui.STAR_system.common import STARCommon
from gspy_egse.gui.STAR_system.channel import Channel
from gspy_egse.gui.STAR_system.channel_listener import ChannelListener
from gspy_egse.gui.STAR_system.STAR_enums import STAR_CHANNEL_DIRECTION

# from Examples.common.helper_functions import HelperFunctions

# Class defined by the user - this can be tailored to one's specific needs
class ChannelListenerUserData:

    def __init__(self, dummyValue):
        self._intMember = dummyValue

def channelCallback(channelListenerIdentifier, driverIdentifier, deviceIdentifier,
                    channelIdentifier, channelOpened, channelNumber, pContextObject):

    print()

    print(f"Channel listener ID: {channelListenerIdentifier}, Driver ID: {driverIdentifier}, Device ID: {deviceIdentifier}")
    print(f"Channel ID: {channelIdentifier}, Channel opened: {bool(channelOpened)}, Channel number: {channelNumber}")
    originalContextObject = STARCommon.restoreContextObject(pContextObject)

    print(f"Original object: {originalContextObject}")

    if originalContextObject is not None:
        print("User-defined data instance fields: " + str(vars(originalContextObject)))

    print()

# This example assumes that you have 1 device connected that is capable to receive SpW traffic
# The first device that is found will be used to receive data and exemplify the transfer completion listener callback function
# It is the user's responsibility to transmit SpW data to the receiving device (using another device, etc.)
def main():

    # Initialize and get first (and only) device attached.
    starSystem = STARSystem()

    try:
        devices = starSystem.getDeviceList()
    except (STARAPIError, TypeError, ValueError):
        print("Could not retrieve list of available devices.")
        exit(-1)

    if len(devices) > 0:
        starDevice = devices[0]
    else:
        # No devices found, exit
        print("No devices found.")
        exit(-1)

    # Enable interface mode
    try:
        deviceChannels = starDevice.getChannels()
        deviceChannelNumbers = [deviceChannel.channelNumber for deviceChannel in deviceChannels]
    except STARAPIError:
        print("Could not get channels.")
        exit(-1)

    try:
        callbackUserData = ChannelListenerUserData(100)
        channelListener = ChannelListener(channelCallback, starDevice.deviceID, None, callbackUserData)
    except (STARAPIError, TypeError, ValueError):
        print("Could not create (receive) Channel object.")
        exit(-1)

    try:
        while True:

            time.sleep(0.5)

            print("Available channels to work with: " + str(deviceChannelNumbers))

            channelNumberChoice = input("Please select which channel to work with: ")

            if channelNumberChoice == "":
                print("ERROR: No value specified.")
                continue

            try:
                channelNumberChoice = HelperFunctions.validateInt(channelNumberChoice, "Invalid choice.")
            except (TypeError, ValueError) as e:
                print("Error occurred during choosing channel number: " + str(e))
                break

            if channelNumberChoice not in deviceChannelNumbers:
                print("Please select a valid channel.")
                continue

            operationChoice = input("Input 1 if you wish to open the channel, input 2 if you wish to close the channel.")

            if operationChoice == "":
                print("ERROR: No value specified.")
                continue

            try:
                operationChoice = HelperFunctions.validateInt(operationChoice, "Invalid choice.")
            except (TypeError, ValueError) as e:
                print("Error occurred during choosing channel number: " + str(e))
                break

            if operationChoice not in [1, 2]:
                print("Please select a valid value.")
                continue

            # Channel to work with
            channel = deviceChannels[channelNumberChoice]

            if operationChoice == 1:
                try:
                    channel.openChannelToDevice(STAR_CHANNEL_DIRECTION.INOUT)
                except (STARAPIError, TypeError):
                    print("Could not open channel.")
                    continue

            elif operationChoice == 2:
                try:
                    channel.close()
                except (STARAPIError, TypeError):
                    print("Could not close channel.")
                    continue
            else:
                print("Invalid choice.")

    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()