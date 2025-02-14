"""Represents a link state event.

Brief:\n
    Represents a link state event.

Copyright:\n
    2021 STAR-Dundee Ltd
"""

class LinkStateEvent(object):
    """Represents events that can occur which affect the state of the SpaceWire link.\n
    
    Not all devices support this item type, and receiving these types may need to be
    enabled separately.\n

    Attributes:\n
        count (int): The number of times that the event(s) has occurred.
        receiveCreditError (bool): Whether or not a receive credit error has occurred.
        transmitCreditError (bool): Whether or not a transmit credit error has occurred.
        escapeError (bool): Whether or not an escape error has occurred.
        parityError (bool): Whether or not a parity error has occurred.
        disconnectError (bool): Whether or not a disconnect error has occurred.
        linkRunning (bool): Whether or not the link is running.
        port (int): The port on which the event occurred.
    """

    def __init__(self, count, receiveCreditError, transmitCreditError, escapeError,
                 parityError, disconnectError, linkRunning, port):
        """Constructor:\n
            Initialises a `STAR_system.link_state_event.LinkStateEvent` object.

        Args:\n
            See `STAR_system.link_state_event.LinkStateEvent` class attributes.

        Raises:\n
            TypeError:\n
                count is not an int.\n
                Any other argument is not a bool.\n
            ValueError:\n
                count is negative.\n
        """

        if type(count) != int:
            raise TypeError("count must be int.")
        if type(receiveCreditError) != bool:
            raise TypeError("receiveCreditError must be bool.")
        if type(transmitCreditError) != bool:
            raise TypeError("transmitCreditError must be bool.")
        if type(escapeError) != bool:
            raise TypeError("escapeError must be bool.")
        if type(parityError) != bool:
            raise TypeError("parityError must be bool.")
        if type(disconnectError) != bool:
            raise TypeError("disconnectError must be bool.")
        if type(linkRunning) != bool:
            raise TypeError("linkRunning must be bool.")
        if type(port) != int:
            raise TypeError("port must be an int.")

        if count < 0:
            raise ValueError("Count cannot be negative.")

        self.count = count
        self.receiveCreditError = receiveCreditError
        self.transmitCreditError = transmitCreditError
        self.escapeError = escapeError
        self.parityError = parityError
        self.disconnectError = disconnectError
        self.linkRunning = linkRunning
        self.port = port
