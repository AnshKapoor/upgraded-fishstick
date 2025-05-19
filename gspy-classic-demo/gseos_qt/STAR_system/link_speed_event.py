"""Represents a link speed change event.

Brief:\n
    Represents a link speed change event.

Copyright:\n
    2021 STAR-Dundee Ltd
"""


class LinkSpeedEvent(object):
    """Represents a link speed change event.
    
    Not all devices support this item type, and receiving these types may
    need to be enabled separately.\n
    
    Attributes:\n
        linkSpeed (int): The new link speed which has been adopted, represented
            in bit/s. Note that this value is approximate.
        port (int): The port on which the link speed event occurred.
    """

    def __init__(self, linkSpeed, port):
        """Constructor:\n
            Initialises a `STAR_system.link_speed_event.LinkSpeedEvent` object.

        Args:\n
            See `STAR_system.link_speed_event.LinkSpeedEvent` class attributes.

        Raises:\n
            TypeError:\n
                linkSpeed was not a number (int, float).\n
                port was not an int.\n
            ValueError:\n
                linkSpeed was negative.\n
                port was negative.\n
        """

        if type(linkSpeed) not in [int, float]:
            raise TypeError("linkSpeed must be an int or float.")
        if linkSpeed < 0:
            raise ValueError("linkSpeed cannot be negative.")

        if type(port) != int:
            raise TypeError("port must be an int.")
        if port < 0:
            raise ValueError("port cannot be negative.")

        self.linkSpeed = int(linkSpeed)
        self.port = port
