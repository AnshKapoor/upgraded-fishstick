"""Contains common functions, to be accessed all throughout the STAR-System Python API.

Brief:\n
    Contains common functions, to be accessed all throughout the STAR-System Python API.

Copyright:\n
    2022 STAR-Dundee Ltd
"""

from ctypes import *
import numpy as np
import pickle
from gspy_egse.gui.STAR_system.STAR_exceptions import STARAPIError

class STARCommon:

    @staticmethod
    def restoreContextObject(pPickledContextObject):
        """This method should only be used/called from a completion listener callback function."""

        if type(pPickledContextObject) != int:
            return None

        # Cast the address value to ctype void pointer
        pVoidPickledContextObject = c_void_p(pPickledContextObject)

        # Cast the ctype void pointer to a pointer of bytes (c_uint8)
        pPickledContextObjectBytes = cast(pVoidPickledContextObject, POINTER(c_uint8))

        # The length of the pickled bytes object is saved as the first value
        try:
            pickledObjectDataLength = pPickledContextObjectBytes.contents.value
        except Exception:
            print("Could not retrieve first value from pickled context bytes contents.")
            return None

        # Retrieve the bytes that make up
        try:
            contextBytes = np.ctypeslib.as_array(
                (c_uint8 * (pickledObjectDataLength + 1)).from_address(
                    addressof(pPickledContextObjectBytes.contents))).tobytes()
        except Exception:
            print("Could not get bytes from ctype void pointer.")
            return None

        # Get rid of the first value (length of the byte stream of the pickled object)
        pickledContextObjectBytes = contextBytes[1:]

        # Unpickle contents (restore original object)
        try:
            originalContextObject = pickle.loads(pickledContextObjectBytes)
        except Exception:
            print("Could not unpickle contents.")
            return None

        return originalContextObject

    @staticmethod
    def saveContextObject(contextObjectToPickle):

        # If the context object is not going to be used (value of None, do nothing)
        if contextObjectToPickle is None:
            return None

        # Pickle the context object
        try:
            pickledContextObject = pickle.dumps(contextObjectToPickle)
        except Exception:
            raise STARAPIError("Could not pickle context object.")

        # We will need to know how many bytes to read in the completion listener
        # So we need to retrieve the length of the pickled object
        pickledPickledContextObjectLength = len(pickledContextObject)

        # Insert the length of the pickled context object at the beginning of the bytes stream
        pickledContextObject = bytes([pickledPickledContextObjectLength]) + pickledContextObject

        # Return the pickled context object
        return pickledContextObject