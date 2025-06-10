"""RMAP Packet Library functions.

Brief:\n
	RMAP Packet Library functions.

Copyright:\n
	2022 STAR-Dundee Ltd
"""

from ctypes import *
from enum import IntEnum
import os
from typing import Tuple, Optional

import numpy as np

from gspy_egse.gui.STAR_system import RMAP_API_LIB_LOAD_ERROR_STR, RMAP_LIB
from gspy_egse.gui.STAR_system.STAR_exceptions import STARAPIError

sysType = os.name
if sysType == ("nt" or "WINDOWS_NT"):
	try:
		dll_rmap = windll.LoadLibrary(RMAP_LIB)
	except Exception:
		dll_rmap = None
		print(RMAP_API_LIB_LOAD_ERROR_STR)
elif sysType == "posix":
	try:
		dll_rmap = cdll.LoadLibrary(RMAP_LIB)
	except Exception:
		dll_rmap = None
		print(RMAP_API_LIB_LOAD_ERROR_STR)


class RMAP_PACKET(Structure):
	"""A structure representing an RMAP packet.

		Attributes:\n
			packetType: (int / int) Packet type value. See `STAR_system.rmap_packet_library.RMAP_PACKET_TYPE` for valid values.\n
			pTargetAddress: (void * / int) A pointer to the target address in the packet, or NULL if the target address
										   could not be identified.\n
			targetAddressLength: (long / int) The length of the target address in the packet.\n
			pReplyAddress: (void * / int) A pointer to the reply address in the packet, or NULL if the reply address
										  could not be identified.\n
			replyAddressLength: (long / int) The length of the reply address in the packet.\n
			pProtocolIdentifier: (void * / int) A pointer to the protocol identifier byte in the packet, or NULL if the
												field could not be identified.\n
			pInstruction: (void * / int) A pointer to the instruction byte in the packet, or NULL if the field
										 could not be identified.\n
			verifyBeforeWrite: (char / 1-character bytes object) Whether verify before write is enabled in the
																 instruction byte in the packet.\n
			acknowledge: (char / 1-character bytes object) Whether acknowledgement is enabled in the instruction byte
														   in the packet.\n
			incrementAddress: (char / 1-character bytes object) Whether incrementing of memory addresses is enabled
																in the instruction in the packet.\n
			pKey: (void * / int) A pointer to the key byte in the packet, if present, otherwise NULL.\n
			pTransactionIdentifier: (void * / int) A pointer to the two byte transaction identifier field in the packet,
												   or NULL if the field could not be identified.\n
			pReadWriteAddress: (void * / int) A pointer to the four byte read or write memory address field in the
											  packet, if present, otherwise NULL.\n
			pExtendedReadWriteAddress: (void * / int) A pointer to the extended read or write memory address byte in the
													  packet, if present, otherwise NULL.\n
			pStatus: (void * / int) A pointer to the status byte in the packet, if present, otherwise NULL.\n
			pHeader: (void * / int) A pointer to the header in the packet, starting from the last byte
									in the address at the start of the packet.\n
			headerLength: (long / int) The length of the header.\n
			pHeaderCRC: (void * / int) A pointer to the header CRC byte in the packet, or NULL if the field could not
									   be identified.\n
			pData: (void * / int) A pointer to the data field in the packet, if present, otherwise NULL.\n
			pDataLength: (void * / int) A pointer to the three byte data length field in the packet, if present,
										otherwise NULL.\n
			dataLength: (unsigned int / int) The length of the data field in the packet, if present, otherwise 0.
											 Note: If the packet is read modify write command packet,
											 then this value will be different from the data length field in the packet,
											 which is the total length of both the data and mask fields.\n
			pDataCRC: (void * / int) A pointer to the data CRC byte in the packet, if present, otherwise NULL.\n
			pMask: (void * / int) A pointer to the mask field in the packet, if present, otherwise NULL.\n
			maskLength: (unsigned int / int) The length of the mask field in the packet, if present, otherwise 0.\n
			pRawPacket: (void * / int) A pointer to the raw packet.\n
			rawPacketLength: (long / int) The length of the raw packet.\n
	"""

	_fields_ = [
		("packetType", c_int32),
		("pTargetAddress", c_void_p),
		("targetAddressLength", c_long),
		("pReplyAddress", c_void_p),
		("replyAddressLength", c_long),
		("pProtocolIdentifier", c_void_p),
		("pInstruction", c_void_p),
		("verifyBeforeWrite", c_char),
		("acknowledge", c_char),
		("incrementAddress", c_char),
		("pKey", c_void_p),
		("pTransactionIdentifier", c_void_p),
		("pReadWriteAddress", c_void_p),
		("pExtendedReadWriteAddress", c_void_p),
		("pStatus", c_void_p),
		("pHeader", c_void_p),
		("headerLength", c_long),
		("pHeaderCRC", c_void_p),
		("pData", c_void_p),
		("pDataLength", c_void_p),
		("dataLength", c_uint32),
		("pDataCRC", c_void_p),
		("pMask", c_void_p),
		("maskLength", c_uint32),
		("pRawPacket", c_void_p),
		("rawPacketLength", c_long)]

class RMAP_STATUS(IntEnum):
	"""Possible values for the status of RMAP operations (function calls)."""

	RMAP_SUCCESS = 0x00
	"""The status value indicating success."""

	RMAP_GENERAL_ERROR = 0x01
	"""The status value indicating that the detected error does not fit into the other error cases."""

	RMAP_UNUSED_PACKET_TYPE_OR_COMMAND_CODE = 0x02
	"""The status value indicating the packet type is reserved or the command is not used by the RMAP protocol."""

	RMAP_INVALID_KEY = 0x03
	"""The status value indicating the key did not match that expected by the target user application."""

	RMAP_INVALID_DATA_CRC = 0x04
	"""The status value indicating there was an error in the data CRC."""

	RMAP_EARLY_EOP = 0x05
	"""The status value indicating an EOP was detected before the end of the data."""

	RMAP_TOO_MUCH_DATA = 0x06
	"""The status value indicating there was more data than was expected."""

	RMAP_EEP = 0x07
	"""The status value indicating that an EEP was encountered in the packet after the header."""

	RMAP_VERIFY_BUFFER_OVERRUN = 0x09
	"""The status value indicating that verify before write was enabled in the
	   command but not enough buffer space was available to receive the full
	   command."""

	RMAP_COMMAND_NOT_IMPLEMENTED_OR_AUTHORISED = 0x0A
	"""The status value indicating the target user application did not authorise the requested operation."""

	RMAP_RMW_DATA_LENGTH_ERROR = 0x0B
	"""The status value indicating the amount of data in a read/modify/write command is invalid."""

	RMAP_INVALID_TARGET_LOGICAL_ADDRESS = 0x0C
	"""The status value indicating the target logical address was not the value expected by the target."""

	RMAP_INVALID_STATUS = 0xFF
	"""The status value indicating that an invalid status value was encountered,
	   or the status could not be determined.
	   Note that this is not a standard RMAP error."""

	@classmethod
	def from_param(cls, obj):
		"""Function needed for marshalling purposes between Python and the C API."""
		return int(obj)

class RMAP_PACKET_TYPE(IntEnum):
	"""Possible values for the RMAP packet type."""

	RMAP_WRITE_COMMAND = 0x40 | 0x20
	"""The write command packet type."""

	RMAP_WRITE_REPLY = 0x20
	"""The write reply packet type."""

	RMAP_READ_COMMAND = 0x40
	"""The read command packet type."""

	RMAP_READ_REPLY = 0
	"""The read reply packet type."""

	RMAP_READ_MODIFY_WRITE_COMMAND = 0x40 | 0x10
	"""The read/modify/write command packet type."""

	RMAP_READ_MODIFY_WRITE_REPLY = 0x10
	"""The read/modify/write reply packet type."""

	RMAP_INVALID_PACKET_TYPE = 0xff
	"""The packet type used when a valid packet type cannot be determined."""

	@classmethod
	def from_param(cls, obj):
		"""Function needed for marshalling purposes between Python and the C API."""
		return int(obj)

class RMAP_PACKET_EXTERNAL():
	"""Class used to represent the contents of an `STAR_system.rmap_packet_library.RMAP_PACKET` structure externally.
	This means that this is the class that should ALWAYS be used by the user.

	Attributes:\n
		Same as the fields of the `STAR_system.rmap_packet_library.RMAP_PACKET` structure, the type of each field
		being the Python equivalent.

   """

	def __init__(self):

		#: packetType: `STAR_system.rmap_packet_library.RMAP_PACKET_TYPE` (see equivalent Structure member in `STAR_system.rmap_packet_library.RMAP_PACKET`)
		self.packetType = RMAP_PACKET_TYPE.RMAP_WRITE_COMMAND

		#: targetAddress: list (see equivalent Structure member in `STAR_system.rmap_packet_library.RMAP_PACKET`)
		self.targetAddress = []

		#: targetAddressLength: int (see equivalent Structure member in `STAR_system.rmap_packet_library.RMAP_PACKET`)
		self.targetAddressLength = 0

		#: replyAddress: list (see equivalent Structure member in `STAR_system.rmap_packet_library.RMAP_PACKET`)
		self.replyAddress = []

		#: replyAddressLength: int (see equivalent Structure member in `STAR_system.rmap_packet_library.RMAP_PACKET`)
		self.replyAddressLength = 0

		#: protocolIdentifier: int (see equivalent Structure member in `STAR_system.rmap_packet_library.RMAP_PACKET`)
		self.protocolIdentifier = 0

		#: instruction: int (see equivalent Structure member in `STAR_system.rmap_packet_library.RMAP_PACKET`)
		self.instruction = 0

		#: verifyBeforeWrite: bool (see equivalent Structure member in `STAR_system.rmap_packet_library.RMAP_PACKET`)
		self.verifyBeforeWrite = False

		#: acknowledge: bool (see equivalent Structure member in `STAR_system.rmap_packet_library.RMAP_PACKET`)
		self.acknowledge = False

		#: incrementAddress: bool (see equivalent Structure member in `STAR_system.rmap_packet_library.RMAP_PACKET`)
		self.incrementAddress = False

		#: key: int (see equivalent Structure member in `STAR_system.rmap_packet_library.RMAP_PACKET`)
		self.key = 0

		#: transactionIdentifier: int (see equivalent Structure member in `STAR_system.rmap_packet_library.RMAP_PACKET`)
		self.transactionIdentifier = 0

		#: readWriteAddress: int (see equivalent Structure member in `STAR_system.rmap_packet_library.RMAP_PACKET`)
		self.readWriteAddress = 0

		#: extendedReadWriteAddress: int (see equivalent Structure member in `STAR_system.rmap_packet_library.RMAP_PACKET`)
		self.extendedReadWriteAddress = 0

		#: status: `STAR_system.rmap_packet_library.RMAP_STATUS` (see equivalent Structure member in `STAR_system.rmap_packet_library.RMAP_PACKET`)
		self.status = RMAP_STATUS.RMAP_SUCCESS

		#: header: list (see equivalent Structure member in `STAR_system.rmap_packet_library.RMAP_PACKET`)
		self.header = []

		#: headerLength: int (see equivalent Structure member in `STAR_system.rmap_packet_library.RMAP_PACKET`)
		self.headerLength = 0

		#: headerCRC: int (see equivalent Structure member in `STAR_system.rmap_packet_library.RMAP_PACKET`)
		self.headerCRC = 0

		#: data: list (see equivalent Structure member in `STAR_system.rmap_packet_library.RMAP_PACKET`)
		self.data = []

		#: dataLengthBytes: list (see equivalent Structure member in `STAR_system.rmap_packet_library.RMAP_PACKET`)
		self.dataLengthBytes = []

		#: dataLength: int (see equivalent Structure member in `STAR_system.rmap_packet_library.RMAP_PACKET`)
		self.dataLength = 0

		#: dataCRC: int (see equivalent Structure member in `STAR_system.rmap_packet_library.RMAP_PACKET`)
		self.dataCRC = 0

		#: mask: list (see equivalent Structure member in `STAR_system.rmap_packet_library.RMAP_PACKET`)
		self.mask = []

		#: maskLength: int (see equivalent Structure member in `STAR_system.rmap_packet_library.RMAP_PACKET`)
		self.maskLength = 0

		#: rawPacket: list (see equivalent Structure member in `STAR_system.rmap_packet_library.RMAP_PACKET`)
		self.rawPacket = []

		#: rawPacketLength: int (see equivalent Structure member in `STAR_system.rmap_packet_library.RMAP_PACKET`)
		self.rawPacketLength = 0

def PopulateExternalRMAPStructure(packetStructInternal) -> RMAP_PACKET_EXTERNAL:
	"""Populates and returns an `STAR_system.rmap_packet_library.RMAP_PACKET_EXTERNAL` object with the contents of the
	`STAR_system.rmap_packet_library.RMAP_PACKET` structure that is passed in as a parameter.

	Args:\n
		packetStructInternal (STAR_system.rmap_packet_library.RMAP_PACKET): The internal representation of the RMAP packet.

	Raises:\n
		STARAPIError:\n
			Could not get target address bytes from the internal RMAP_PACKET structure.\n
			Could not get reply address bytes from the internal RMAP_PACKET structure.\n
			Could not get header bytes from the internal RMAP_PACKET structure.\n
			Could not get data length bytes from the internal RMAP_PACKET structure.\n
			Could not get data bytes from the internal RMAP_PACKET structure.\n
			Could not get mask bytes from the internal RMAP_PACKET structure.\n
			Could not get raw packet bytes from the internal RMAP_PACKET structure.\n
	"""

	# Create external RMAP packet structure
	packetStruct = RMAP_PACKET_EXTERNAL()

	# Packet type
	packetStruct.packetType = RMAP_PACKET_TYPE(packetStructInternal.packetType)

	# Target address length
	packetStruct.targetAddressLength = packetStructInternal.targetAddressLength

	# Target address bytes
	if packetStruct.targetAddressLength > 0 and packetStructInternal.pTargetAddress is not None:

		# Get target address (void) pointer and cast it to byte ptr
		targetAddressPtr = cast(packetStructInternal.pTargetAddress, POINTER(c_uint8))

		# Get the values as list
		try:
			packetStruct.targetAddress = list(np.ctypeslib.as_array(targetAddressPtr,
																	(packetStruct.targetAddressLength,)).tobytes())
		except TypeError as err:
			raise STARAPIError("Could not get target address bytes from internal RMAP_PACKET structure: " + str(err))

	# Reply address length
	packetStruct.replyAddressLength = packetStructInternal.replyAddressLength

	# Reply address bytes
	if packetStruct.replyAddressLength > 0 and packetStructInternal.pReplyAddress is not None:

		# Get reply address (void) pointer and cast it to byte ptr
		replyAddressPtr = cast(packetStructInternal.pReplyAddress, POINTER(c_uint8))

		# Get the values as list
		try:
			packetStruct.replyAddress = list(np.ctypeslib.as_array(replyAddressPtr,
																   (packetStruct.replyAddressLength,)).tobytes())
		except TypeError as err:
			raise STARAPIError("Could not get reply address bytes from internal RMAP_PACKET structure: " + str(err))

	# Protocol identifier
	if packetStructInternal.pProtocolIdentifier is not None:
		protocolIdPtr = cast(packetStructInternal.pProtocolIdentifier, POINTER(c_uint8))
		packetStruct.protocolIdentifier = protocolIdPtr[0]

	# Instruction byte
	if packetStructInternal.pInstruction is not None:
		instructionPtr = cast(packetStructInternal.pInstruction, POINTER(c_uint8))
		packetStruct.instruction = instructionPtr[0]

	# Verify before write
	verifyBeforeWriteChar = packetStructInternal.verifyBeforeWrite

	# Check that 1 char value was returned
	if len(verifyBeforeWriteChar) == 1:

		# Convert this value to bool
		packetStruct.verifyBeforeWrite = bool(list(verifyBeforeWriteChar)[0])

	# Acknowledge
	acknowledgeChar = packetStructInternal.acknowledge

	# Check that 1 char value was returned
	if len(acknowledgeChar) == 1:

		# Convert this value to bool
		packetStruct.acknowledge = bool(list(acknowledgeChar)[0])

	# Increment address
	incrementAddressChar = packetStructInternal.incrementAddress

	# Check that 1 char value was returned
	if len(incrementAddressChar) == 1:

		# Convert this value to bool
		packetStruct.incrementAddress = bool(list(incrementAddressChar)[0])

	# Key
	if packetStructInternal.pKey is not None:
		keyPtr = cast(packetStructInternal.pKey, POINTER(c_uint8))
		packetStruct.key = keyPtr[0]

	# Transaction identifier
	if packetStructInternal.pTransactionIdentifier is not None:
		transactionIdPtr = cast(packetStructInternal.pTransactionIdentifier, POINTER(c_uint8))
		transactionIdMSB = int(transactionIdPtr[0])
		transactionIdLSB = int(transactionIdPtr[1])
		packetStruct.transactionIdentifier = (transactionIdMSB << 8) + transactionIdLSB

	# Read/write address
	if packetStructInternal.pReadWriteAddress is not None:
		readWriteAddressPtr = cast(packetStructInternal.pReadWriteAddress, POINTER(c_uint8))
		readWriteAddressByte0 = int(readWriteAddressPtr[0])
		readWriteAddressByte1 = int(readWriteAddressPtr[1])
		readWriteAddressByte2 = int(readWriteAddressPtr[2])
		readWriteAddressByte3 = int(readWriteAddressPtr[3])
		packetStruct.readWriteAddress = (readWriteAddressByte0 << 24) + (readWriteAddressByte1 << 16) +\
										(readWriteAddressByte2 << 8) + readWriteAddressByte3

	# Extended read/write address
	if packetStructInternal.pExtendedReadWriteAddress is not None:
		extReadWriteAddressPtr = cast(packetStructInternal.pExtendedReadWriteAddress, POINTER(c_uint8))
		packetStruct.extendedReadWriteAddress = extReadWriteAddressPtr[0]

	# Status
	if packetStructInternal.pStatus is not None:
		statusPtr = cast(packetStructInternal.pStatus, POINTER(c_uint8))
		packetStruct.status = RMAP_STATUS(statusPtr[0])

	# Header length
	packetStruct.headerLength = packetStructInternal.headerLength

	# Header bytes
	if packetStruct.headerLength > 0 and packetStructInternal.pHeader is not None:

		# Get header (void) pointer and cast it to byte ptr
		headerPtr = cast(packetStructInternal.pHeader, POINTER(c_uint8))

		# Get the values as list
		try:
			packetStruct.header = list(np.ctypeslib.as_array(headerPtr,
															 (packetStruct.headerLength,)).tobytes())
		except TypeError as err:
			raise STARAPIError("Could not get header bytes from internal RMAP_PACKET structure: " + str(err))

	# Header CRC byte
	if packetStructInternal.pHeaderCRC is not None:
		headerCRCPtr = cast(packetStructInternal.pHeaderCRC, POINTER(c_uint8))
		packetStruct.headerCRC = headerCRCPtr[0]

	# Data length
	packetStruct.dataLength = packetStructInternal.dataLength

	# Data length bytes
	if packetStructInternal.pDataLength is not None:

		dataLengthPtr = cast(packetStructInternal.pDataLength, POINTER(c_uint8))

		# Get the values as list
		try:
			packetStruct.dataLengthBytes = list(np.ctypeslib.as_array(dataLengthPtr, (3,)).tobytes())
		except TypeError as err:
			raise STARAPIError("Could not get data length bytes from internal RMAP_PACKET structure: " + str(err))

	# Get data bytes
	if packetStruct.dataLength > 0 and packetStructInternal.pData is not None:

		# Get data (void) pointer and cast it to byte ptr
		dataPtr = cast(packetStructInternal.pData, POINTER(c_uint8))

		# Get the values as list
		try:
			packetStruct.data = list(np.ctypeslib.as_array(dataPtr, (packetStruct.dataLength,)).tobytes())
		except TypeError as err:
			raise STARAPIError("Could not get data bytes from internal RMAP_PACKET structure: " + str(err))

	# Header CRC byte
	if packetStructInternal.pDataCRC is not None:
		dataCRCPtr = cast(packetStructInternal.pDataCRC, POINTER(c_uint8))
		packetStruct.dataCRC = dataCRCPtr[0]

	# Mask length
	packetStruct.maskLength = packetStructInternal.maskLength

	# Mask bytes
	if packetStruct.maskLength > 0 and packetStructInternal.pMask is not None:

		# Get mask (void) pointer and cast it to byte ptr
		maskPtr = cast(packetStructInternal.pMask, POINTER(c_uint8))

		# Get the values as list
		try:
			packetStruct.mask = list(np.ctypeslib.as_array(maskPtr, (packetStruct.maskLength,)).tobytes())
		except TypeError as err:
			raise STARAPIError("Could not get mask bytes from internal RMAP_PACKET structure: " + str(err))

	# Raw packet length
	packetStruct.rawPacketLength = packetStructInternal.rawPacketLength

	# Raw packet bytes
	if packetStruct.rawPacketLength > 0 and packetStructInternal.pRawPacket is not None:

		# Get raw packet bytes (void) pointer and cast it to byte ptr
		rawPacketBytesPtr = cast(packetStructInternal.pRawPacket, POINTER(c_uint8))

		# Get the values as list
		try:
			packetStruct.rawPacket = list(np.ctypeslib.as_array(rawPacketBytesPtr,
																(packetStruct.rawPacketLength,)).tobytes())
		except TypeError as err:
			raise STARAPIError("Could not get raw packet bytes from internal RMAP_PACKET structure: " + str(err))

	return packetStruct

def RMAP_BuildReadCommandPacket(targetAddress, replyAddress, incrementAddress, key, transactionIdentifier, readAddress,
								extendedReadAddress, dataLength, alignment) -> Tuple[list, RMAP_PACKET_EXTERNAL]:
	""" Builds an RMAP read command packet which can be transmitted to perform an RMAP read command.\n
		Returns a tuple: a list containing the packet bytes and an `STAR_system.rmap_packet_library.RMAP_PACKET_EXTERNAL` object
						 containing the RMAP packet contents.

		Args:\n
			targetAddress (list of ints): List containing the target address bytes.
			replyAddress (list of ints): List containing the reply address bytes.
			incrementAddress (bool): Whether the target read address should be
									 incremented when reading or not.
			key (int): The key (value) expected by the destination device.
			transactionIdentifier (int): An identifier for the transaction.
			readAddress (int): The memory address at the destination to read from.
			extendedReadAddress (int): The extended memory address at the destination to read from.
			dataLength (int): The length of data to read, which is a 24-bit number and so should be at most 0xFFFFFF.
			alignment (int): The word size used by the device sending the packet, normally 1.

		Raises:\n
			STARAPIError:\n
				The RMAP packet library could not be loaded.\n
				RMAP Build Read Command Packet failed.\n
				Could not populate external RMAP packet structure.\n

			TypeError:\n
				targetAddress must be a list.\n
				at least one element in targetAddress was not an int.\n
				replyAddress must be a list.\n
				at least one element in replyAddress was not an int.\n
				incrementAddress was not a bool.\n
				key was not an int.\n
				transactionIdentifier must be an int.\n
				readAddress must be an int.\n
				extendedReadAddress must be an int.\n
				dataLength must be an int.\n
				alignment must be an int.\n

			ValueError:\n
				every element in targetAddress must be between 0 and 255.\n
				every element in replyAddress must be between 0 and 255.\n
				key must be between 0 and 255.\n
				transactionIdentifier must be between 0 and 65535.\n
				extendedReadAddress must be between 0 and 255.\n
				dataLength must be between 0 and 0xFFFFFF.\n
				alignment must be between 0 and 127.\n
	"""

	# Protect against invalid RMAP packet library
	if dll_rmap is None:
		raise STARAPIError(RMAP_API_LIB_LOAD_ERROR_STR)

	# Handle type errors and value errors
	if isinstance(targetAddress, list) is False:
		raise TypeError("targetAddress must be a list.")

	for targetAddressByte in targetAddress:
		if type(targetAddressByte) != int:
			raise TypeError("every element in targetAddress must be an int.")
		if targetAddressByte < 0 or targetAddressByte > 255:
			raise ValueError("each target address byte must be between 0 and 255.")

	if isinstance(replyAddress, list) is False:
		raise TypeError("replyAddress must be a list.")

	for replyAddressByte in replyAddress:
		if type(replyAddressByte) != int:
			raise TypeError("every element in replyAddress must be an int.")
		if replyAddressByte < 0 or replyAddressByte > 255:
			raise ValueError("each reply address byte must be between 0 and 255.")

	if type(incrementAddress) != bool:
		raise TypeError("incrementAddress must be a bool.")

	if type(key) != int:
		raise TypeError("key must be an int.")

	if key < 0 or key > 255:
		raise ValueError("key must be between 0 and 255.")

	if type(transactionIdentifier) != int:
		raise TypeError("transactionIdentifier must be an int.")

	if transactionIdentifier < 0 or transactionIdentifier > 65535:
		raise ValueError("transactionIdentifier must be between 0 and 65535.")

	if type(readAddress) != int:
		raise TypeError("readAddress must be an int.")

	if type(extendedReadAddress) != int:
		raise TypeError("extendedReadAddress must be an int.")

	if extendedReadAddress < 0 or extendedReadAddress > 255:
		raise ValueError("extendedReadAddress must be between 0 and 255.")

	if type(dataLength) != int:
		raise TypeError("dataLength must be an int.")

	if dataLength < 0 or dataLength > 0xFFFFFF:
		raise ValueError("dataLength must be between 0 and 0xFFFFFF.")

	if type(alignment) != int:
		raise TypeError("alignment must be an int.")

	if alignment < 0 or alignment > 127:
		raise ValueError("alignment must be between 0 and 127.")

	# Get the length of the target address
	targetAddressLength = len(targetAddress)

	# Get the length of the reply address
	replyAddressLength = len(replyAddress)

	# Set up an array holding the target address bytes
	cTargetArray = (c_uint8 * targetAddressLength)()

	# Assign the target address byte values
	for i in range(0, targetAddressLength):
		cTargetArray[i] = targetAddress[i]

	# Set up an array holding the reply address bytes
	cReplyArray = (c_uint8 * replyAddressLength)()

	# Assign the reply address byte values
	for j in range(0, replyAddressLength):
		cReplyArray[j] = replyAddress[j]

	# Cast to pointers (for marshalling purposes)
	cTargetArrayPointer = pointer(cTargetArray)
	cReplyArrayPointer = pointer(cReplyArray)

	# Variable holding the length of the raw packet
	rawPacketLength = c_ulong(0)
	pRawPacketLength = pointer(rawPacketLength)

	# Create packet structure pointer
	packetStructInternal = RMAP_PACKET()
	packetStructInternalPtr = pointer(packetStructInternal)

	# Set argument types and return type of the C function
	dll_rmap.RMAP_BuildReadCommandPacket.argtypes = [
		POINTER(c_uint8 * targetAddressLength), c_ulong, POINTER(c_uint8 * replyAddressLength), c_ulong,
		c_char, c_uint8, c_uint16, c_uint32, c_uint8, c_uint32, POINTER(c_ulong), POINTER(RMAP_PACKET), c_char]
	dll_rmap.RMAP_BuildReadCommandPacket.restype = c_void_p

	packet = dll_rmap.RMAP_BuildReadCommandPacket(cTargetArrayPointer, c_ulong(targetAddressLength), cReplyArrayPointer,
												  c_ulong(replyAddressLength), c_char(incrementAddress), c_uint8(key),
												  c_uint16(transactionIdentifier), c_uint32(readAddress),
												  c_uint8(extendedReadAddress), c_uint32(dataLength),
												  pRawPacketLength, packetStructInternalPtr, c_char(alignment))

	if packet is None or rawPacketLength.value == 0:
		raise STARAPIError("RMAP Build Read Command Packet failed.")

	# Create packet structure object for external use
	try:
		packetStruct = PopulateExternalRMAPStructure(packetStructInternal)
	except STARAPIError:
		raise

	# Cast packet to a pointer of bytes
	packetPtr = cast(packet, POINTER(c_ubyte))

	packetByteList = []
	for i in range(0, rawPacketLength.value):
		packetByteList.append(packetPtr[i])

	# Free packet
	RMAP_FreeBuffer(packet)

	return packetByteList, packetStruct

def RMAP_BuildReadModifyWriteCommandPacket(targetAddress, replyAddress, key, transactionIdentifier,
										   readModifyWriteAddress, extendedReadModifyWriteAddress, data, mask,
										   alignment) -> Tuple[list, RMAP_PACKET_EXTERNAL]:
	""" Builds an RMAP read-modify-write command packet which can be transmitted to
		perform an RMAP read/modify/write command.\n

		Returns a tuple: a list containing the packet bytes and an `STAR_system.rmap_packet_library.RMAP_PACKET_EXTERNAL` object
						 containing the RMAP packet contents.

		Args:\n
			targetAddress (list of ints): List containing the target address bytes.
			replyAddress (list of ints): List containing the reply address bytes.
			key (int): The key (value) expected by the destination device.
			transactionIdentifier (int): An identifier for the transaction.
			readModifyWriteAddress (int): The memory address at the destination to read from and write to.
			extendedReadModifyWriteAddress (int): The extended memory address at the destination to read from and write to.
			data (list of ints): The data to be written.
			mask (list of ints): The mask to be applied to the data.
			alignment (int): The word size used by the device sending the packet, normally 1.

		Raises:\n
			STARAPIError:\n
				The RMAP packet library could not be loaded.\n
				Length of data list and length of mask list were not equal.\n
				RMAP Build Read/Modify/Write Command Packet failed.\n
				Could not populate external RMAP packet structure.\n

			TypeError:\n
				targetAddress must be a list.\n
				at least one element in targetAddress was not an int.\n
				replyAddress must be a list.\n
				at least one element in replyAddress was not an int.\n
				key was not an int.\n
				transactionIdentifier must be an int.\n
				readModifyWriteAddress must be an int.\n
				extendedReadModifyWriteAddress must be an int.\n
				data must be a list.\n
				at least one element in data was not an int.\n
				mask must be a list.\n
				at least one element in mask was not an int.\n
				alignment must be an int.\n

			ValueError:\n
				every element in targetAddress must be between 0 and 255.\n
				every element in replyAddress must be between 0 and 255.\n
				key must be between 0 and 255.\n
				transactionIdentifier must be between 0 and 65535.\n
				extendedReadModifyWriteAddress must be between 0 and 255.\n
				each data byte must be between 0 and 255.\n
				each mask byte must be between 0 and 255.\n
				alignment must be between 0 and 127.\n
	"""

	# Protect against invalid RMAP packet library
	if dll_rmap is None:
		raise STARAPIError(RMAP_API_LIB_LOAD_ERROR_STR)

	# Handle type errors and value errors
	if isinstance(targetAddress, list) is False:
		raise TypeError("targetAddress must be a list.")

	for targetAddressByte in targetAddress:
		if type(targetAddressByte) != int:
			raise TypeError("every element in targetAddress must be an int.")
		if targetAddressByte < 0 or targetAddressByte > 255:
			raise ValueError("each target address byte must be between 0 and 255.")

	if isinstance(replyAddress, list) is False:
		raise TypeError("replyAddress must be a list.")

	for replyAddressByte in replyAddress:
		if type(replyAddressByte) != int:
			raise TypeError("every element in replyAddress must be an int.")
		if replyAddressByte < 0 or replyAddressByte > 255:
			raise ValueError("each reply address byte must be between 0 and 255.")

	if type(key) != int:
		raise TypeError("key must be an int.")

	if key < 0 or key > 255:
		raise ValueError("key must be between 0 and 255.")

	if type(transactionIdentifier) != int:
		raise TypeError("transactionIdentifier must be an int.")

	if transactionIdentifier < 0 or transactionIdentifier > 65535:
		raise ValueError("transactionIdentifier must be between 0 and 65535.")

	if type(readModifyWriteAddress) != int:
		raise TypeError("readModifyWriteAddress must be an int.")

	if type(extendedReadModifyWriteAddress) != int:
		raise TypeError("extendedReadModifyWriteAddress must be an int.")

	if extendedReadModifyWriteAddress < 0 or extendedReadModifyWriteAddress > 255:
		raise ValueError("extendedReadModifyWriteAddress must be between 0 and 255.")

	for dataByte in data:
		if type(dataByte) != int:
			raise TypeError("every element in data must be an int.")
		if dataByte < 0 or dataByte > 255:
			raise ValueError("each data byte must be between 0 and 255.")

	for maskByte in mask:
		if type(maskByte) != int:
			raise TypeError("every element in mask must be an int.")
		if maskByte < 0 or maskByte > 255:
			raise ValueError("each mask byte must be between 0 and 255.")

	if type(alignment) != int:
		raise TypeError("alignment must be an int.")

	if alignment < 0 or alignment > 127:
		raise ValueError("alignment must be between 0 and 127.")

	# Get the length of the target address
	targetAddressLength = len(targetAddress)

	# Get the length of the reply address
	replyAddressLength = len(replyAddress)

	# Set up an array holding the target address bytes
	cTargetArray = (c_uint8 * targetAddressLength)()

	# Assign the target address byte values
	for i in range(0, targetAddressLength):
		cTargetArray[i] = targetAddress[i]

	# Set up an array holding the reply address bytes
	cReplyArray = (c_uint8 * replyAddressLength)()

	# Assign the reply address byte values
	for j in range(0, replyAddressLength):
		cReplyArray[j] = replyAddress[j]

	# Cast to pointers (for marshalling purposes)
	cTargetArrayPointer = pointer(cTargetArray)
	cReplyArrayPointer = pointer(cReplyArray)

	# Get the length of the data
	dataLength = len(data)

	# Get the length of the mask
	maskLength = len(mask)

	# Check that the two lengths are equal
	if dataLength != maskLength:
		raise STARAPIError("Length of data list and length of mask list must be equal.")

	# Combine the two lengths (data + mask)
	dataAndMaskLength = dataLength + maskLength

	# Set up array that holds the data bytes
	cDataArray = (c_uint8 * dataLength)()

	# Assign the data byte values
	for i in range(0, dataLength):
		cDataArray[i] = data[i]

	# Cast to pointer (for marshalling purposes)
	cDataArrayPointer = pointer(cDataArray)

	# Set up array that holds the mask bytes
	cMaskArray = (c_uint8 * maskLength)()

	# Assign the mask byte values
	for i in range(0, maskLength):
		cMaskArray[i] = mask[i]

	# Cast to pointer (for marshalling purposes)
	cMaskArrayPointer = pointer(cMaskArray)

	# Variable holding the raw packet length
	rawPacketLength = c_ulong(0)
	pRawPacketLength = pointer(rawPacketLength)

	# Create packet structure pointer
	packetStructInternal = RMAP_PACKET()
	packetStructInternalPtr = pointer(packetStructInternal)

	# Set argument types and return type of the C function
	dll_rmap.RMAP_BuildReadModifyWriteCommandPacket.argtypes = [
		POINTER(c_uint8 * targetAddressLength), c_ulong, POINTER(c_uint8 * replyAddressLength), c_ulong,
		c_uint8, c_uint16, c_uint32, c_uint8, c_uint8, POINTER(c_uint8 * dataLength), POINTER(c_uint8 * maskLength),
		POINTER(c_ulong), POINTER(RMAP_PACKET), c_char]
	dll_rmap.RMAP_BuildReadModifyWriteCommandPacket.restype = c_void_p

	packet = dll_rmap.RMAP_BuildReadModifyWriteCommandPacket(cTargetArrayPointer, c_ulong(targetAddressLength),
															 cReplyArrayPointer, c_ulong(replyAddressLength), c_uint8(key),
															 c_uint16(transactionIdentifier),
															 c_uint32(readModifyWriteAddress),
															 c_uint8(extendedReadModifyWriteAddress),
															 c_uint8(dataAndMaskLength), cDataArrayPointer,
															 cMaskArrayPointer, pRawPacketLength,
															 packetStructInternalPtr, c_char(alignment))

	if packet is None or rawPacketLength.value == 0:
		raise STARAPIError("RMAP Build Read/Modify/Write Command Packet failed.")

	# Create packet structure object for external use
	try:
		packetStruct = PopulateExternalRMAPStructure(packetStructInternal)
	except STARAPIError:
		raise

	# Cast from void * to unsigned char *
	packetPtr = cast(packet, POINTER(c_ubyte))

	packetByteList = []
	for i in range(0, rawPacketLength.value):
		packetByteList.append(packetPtr[i])

	# Free packet
	RMAP_FreeBuffer(packet)

	return packetByteList, packetStruct

def RMAP_BuildReadModifyWriteRegisterPacket(targetAddress, replyAddress, key, transactionIdentifier,
											readModifyWriteAddress, extendedReadModifyWriteAddress, registerValue,
											mask, alignment) -> Tuple[list, RMAP_PACKET_EXTERNAL]:
	""" Builds an RMAP read-modify-write command packet which can be transmitted to
		perform an RMAP read-modify-write command on a 4 byte register.

		Returns a tuple: a list containing the packet bytes and an `STAR_system.rmap_packet_library.RMAP_PACKET_EXTERNAL` object
						 containing the RMAP packet contents.

		Args:\n
			targetAddress (list of ints): List containing the target address bytes.
			replyAddress (list of ints): List containing the reply address bytes.
			key (int): The key (value) expected by the destination device.
			transactionIdentifier (int): An identifier for the transaction.
			readModifyWriteAddress (int): The memory address at the destination to read from and write to.
			extendedReadModifyWriteAddress (int): The extended memory address at the destination to read from and write to.
			registerValue (int): The value to be written to the register.
			mask (int): The mask to be applied to the register.
			alignment (int): The word size used by the device sending the packet, normally 1.

		Raises:\n
			STARAPIError:\n
				The RMAP packet library could not be loaded.\n
				RMAP Build Read/Modify/Write Command on Register Packet failed.\n
				Could not populate external RMAP packet structure.\n

			TypeError:\n
				targetAddress must be a list.\n
				at least one element in targetAddress was not an int.\n
				replyAddress must be a list.\n
				at least one element in replyAddress was not an int.\n
				key was not an int.\n
				transactionIdentifier must be an int.\n
				readModifyWriteAddress must be an int.\n
				extendedReadModifyWriteAddress must be an int.\n
				registerValue must be an int.\n
				mask must be an int.\n
				alignment must be an int.\n

			ValueError:\n
				every element in targetAddress must be between 0 and 255.\n
				every element in replyAddress must be between 0 and 255.\n
				key must be between 0 and 255.\n
				transactionIdentifier must be between 0 and 65535.\n
				extendedReadModifyWriteAddress must be between 0 and 255.\n
				alignment must be between 0 and 127.\n
		"""

	# Protect against invalid RMAP packet library
	if dll_rmap is None:
		raise STARAPIError(RMAP_API_LIB_LOAD_ERROR_STR)

	# Handle type errors and value errors
	if isinstance(targetAddress, list) is False:
		raise TypeError("targetAddress must be a list.")

	for targetAddressByte in targetAddress:
		if type(targetAddressByte) != int:
			raise TypeError("every element in targetAddress must be an int.")
		if targetAddressByte < 0 or targetAddressByte > 255:
			raise ValueError("each target address byte must be between 0 and 255.")

	if isinstance(replyAddress, list) is False:
		raise TypeError("replyAddress must be a list.")

	for replyAddressByte in replyAddress:
		if type(replyAddressByte) != int:
			raise TypeError("every element in replyAddress must be an int.")
		if replyAddressByte < 0 or replyAddressByte > 255:
			raise ValueError("each reply address byte must be between 0 and 255.")

	if type(key) != int:
		raise TypeError("key must be an int.")

	if key < 0 or key > 255:
		raise ValueError("key must be between 0 and 255.")

	if type(transactionIdentifier) != int:
		raise TypeError("transactionIdentifier must be an int.")

	if transactionIdentifier < 0 or transactionIdentifier > 65535:
		raise ValueError("transactionIdentifier must be between 0 and 65535.")

	if type(readModifyWriteAddress) != int:
		raise TypeError("readModifyWriteAddress must be an int.")

	if type(extendedReadModifyWriteAddress) != int:
		raise TypeError("extendedReadModifyWriteAddress must be an int.")

	if extendedReadModifyWriteAddress < 0 or extendedReadModifyWriteAddress > 255:
		raise ValueError("extendedReadModifyWriteAddress must be between 0 and 255.")

	if type(registerValue) != int:
		raise TypeError("registerValue must be an int.")

	if type(mask) != int:
		raise TypeError("mask must be an int.")

	if type(alignment) != int:
		raise TypeError("alignment must be an int.")

	if alignment < 0 or alignment > 127:
		raise ValueError("alignment must be between 0 and 127.")

	# Get the length of the target address
	targetAddressLength = len(targetAddress)

	# Get the length of the reply address
	replyAddressLength = len(replyAddress)

	# Set up array that holds the target address bytes
	cTargetArray = (c_uint8 * targetAddressLength)()

	# Assign target address byte values
	for i in range(0, targetAddressLength):
		cTargetArray[i] = targetAddress[i]

	# Set up array that holds the reply address bytes
	cReplyArray = (c_uint8 * replyAddressLength)()

	# Assign reply address byte values
	for j in range(0, replyAddressLength):
		cReplyArray[j] = replyAddress[j]

	# Cast to pointer (for marshalling purposes)
	cTargetArrayPointer = pointer(cTargetArray)
	cReplyArrayPointer = pointer(cReplyArray)

	# Variable holding the raw packet length
	rawPacketLength = c_ulong(0)
	pRawPacketLength = pointer(rawPacketLength)

	# Create packet structure pointer
	packetStructInternal = RMAP_PACKET()
	packetStructInternalPtr = pointer(packetStructInternal)

	# Set argument types and return type of the C function
	dll_rmap.RMAP_BuildReadModifyWriteRegisterPacket.argtypes = [
		POINTER(c_uint8 * targetAddressLength), c_ulong, POINTER(c_uint8 * replyAddressLength), c_ulong, c_uint8,
		c_uint16, c_uint32, c_uint8, c_uint32, c_uint32, POINTER(c_ulong), POINTER(RMAP_PACKET), c_char]
	dll_rmap.RMAP_BuildReadModifyWriteRegisterPacket.restype = c_void_p

	packet = dll_rmap.RMAP_BuildReadModifyWriteRegisterPacket(cTargetArrayPointer, c_ulong(targetAddressLength),
															  cReplyArrayPointer, c_ulong(replyAddressLength),
															  c_uint8(key), c_uint16(transactionIdentifier),
															  c_uint32(readModifyWriteAddress),
															  c_uint8(extendedReadModifyWriteAddress),
															  c_uint32(registerValue),
															  c_uint32(mask), pRawPacketLength, packetStructInternalPtr,
															  c_char(alignment))

	if packet is None or rawPacketLength.value == 0:
		raise STARAPIError("RMAP Build Read/Modify/Write Command on Register Packet failed.")

	# Create packet structure object for external use
	try:
		packetStruct = PopulateExternalRMAPStructure(packetStructInternal)
	except STARAPIError:
		raise

	# Cast void * to unsigned char *
	packetPtr = cast(packet, POINTER(c_ubyte))

	packetByteList = []
	for i in range(0, rawPacketLength.value):
		packetByteList.append(packetPtr[i])

	# Free packet
	RMAP_FreeBuffer(packet)

	return packetByteList, packetStruct

def RMAP_BuildReadModifyWriteReplyPacket(initiatorAddress, targetAddress, status,
										 transactionIdentifier, data, alignment) -> Tuple[list, RMAP_PACKET_EXTERNAL]:
	""" Builds an RMAP read-modify-write reply packet which can be transmitted to respond
		to an RMAP read/modify/write command.

		Returns a tuple: a list containing the packet bytes and an `STAR_system.rmap_packet_library.RMAP_PACKET_EXTERNAL` object
						 containing the RMAP packet contents.

		Args:\n
			initiatorAddress (list of ints): List containing the logical address bytes
											 of the device to which the reply should be sent.
			targetAddress (int): The SpaceWire logical address bytes of the device that sent the
								 command being responded to.
			status (STAR_system.rmap_packet_library.RMAP_STATUS): The status of the read operation.
			transactionIdentifier (int): An identifier for the transaction.
			data (list of ints): The data read.
			alignment (int): The word size used by the device sending the packet, normally 1.

		Raises:\n
			STARAPIError:\n
				The RMAP packet library could not be loaded.\n
				RMAP Build Read/Modify/Write Reply Packet failed.\n
				Could not populate external RMAP packet structure.\n

			TypeError:\n
				initiatorAddress must be a list.\n
				at least one element in initiatorAddress was not an int.\n
				targetAddress must be an int.\n
				transactionIdentifier must be an int.\n
				data must be a list.\n
				at least one element in data was not an int.\n
				alignment must be an int.\n

			ValueError:\n
				every element in initiatorAddress must be between 0 and 255.\n
				targetAddress must be between 0 and 255.\n
				transactionIdentifier must be between 0 and 65535.\n
				every element in data must be between 0 and 255.\n
				alignment must be between 0 and 127.\n
	"""

	# Protect against invalid RMAP packet library
	if dll_rmap is None:
		raise STARAPIError(RMAP_API_LIB_LOAD_ERROR_STR)

	# Handle type errors and value errors
	if isinstance(initiatorAddress, list) is False:
		raise TypeError("initiatorAddress must be a list.")

	for initiatorAddressByte in initiatorAddress:
		if type(initiatorAddressByte) != int:
			raise TypeError("every element in initiatorAddress must be an int.")
		if initiatorAddressByte < 0 or initiatorAddressByte > 255:
			raise ValueError("each initiator address byte must be between 0 and 255.")

	if type(targetAddress) != int:
		raise TypeError("targetAddress must be an int.")

	if targetAddress < 0 or targetAddress > 255:
		raise ValueError("targetAddress must be between 0 and 255.")

	if type(transactionIdentifier) != int:
		raise TypeError("transactionIdentifier must be an int.")

	if transactionIdentifier < 0 or transactionIdentifier > 65535:
		raise ValueError("transactionIdentifier must be between 0 and 65535.")

	for dataByte in data:
		if type(dataByte) != int:
			raise TypeError("every element in data must be an int.")
		if dataByte < 0 or dataByte > 255:
			raise ValueError("each data byte must be between 0 and 255.")

	if type(alignment) != int:
		raise TypeError("alignment must be an int.")

	if alignment < 0 or alignment > 127:
		raise ValueError("alignment must be between 0 and 127.")

	# Get the length of the initiator address
	initiatorAddressLength = len(initiatorAddress)

	# Set up array holding the initiator address bytes
	cInitiatorArray = (c_uint8 * initiatorAddressLength)()

	# Assign the initiator address bytes to the array
	for i in range(0, initiatorAddressLength):
		cInitiatorArray[i] = initiatorAddress[i]

	# Cast to pointer (for marshalling purposes)
	cInitiatorArrayPointer = pointer(cInitiatorArray)

	# Get the data length
	dataLength = len(data)

	# Set up an array holding the data bytes
	cDataArray = (c_uint8 * dataLength)()

	# Assign the data byte values
	for i in range(0, dataLength):
		cDataArray[i] = data[i]

	# Cast to pointer (for marshalling purposes)
	cDataArrayPointer = pointer(cDataArray)

	# Variable holding the length of the raw packet (to be built)
	rawPacketLength = c_ulong(0)
	pRawPacketLength = pointer(rawPacketLength)

	# Create packet structure pointer
	packetStructInternal = RMAP_PACKET()
	packetStructInternalPtr = pointer(packetStructInternal)

	# Set argument types and return type of the C function
	dll_rmap.RMAP_BuildReadModifyWriteReplyPacket.argtypes = [
		POINTER(c_uint8 * initiatorAddressLength), c_ulong, c_uint8, RMAP_STATUS, c_uint16, c_ulong,
		POINTER(c_uint8 * dataLength), POINTER(c_ulong), POINTER(RMAP_PACKET), c_char]
	dll_rmap.RMAP_BuildReadModifyWriteReplyPacket.restype = c_void_p

	packet = dll_rmap.RMAP_BuildReadModifyWriteReplyPacket(cInitiatorArrayPointer, c_ulong(initiatorAddressLength),
														   c_uint8(targetAddress), status,
														   c_uint16(transactionIdentifier), c_ulong(dataLength),
														   cDataArrayPointer, pRawPacketLength,
														   packetStructInternalPtr, c_char(alignment))

	if packet is None or rawPacketLength.value == 0:
		raise STARAPIError("RMAP Build Read/Modify/Write Reply Packet failed.")

	# Create packet structure object for external use
	try:
		packetStruct = PopulateExternalRMAPStructure(packetStructInternal)
	except STARAPIError:
		raise

	# Cast packet to a pointer of bytes
	packetPtr = cast(packet, POINTER(c_ubyte))

	packetByteList = []
	for i in range(0, rawPacketLength.value):
		packetByteList.append(packetPtr[i])

	# Free packet
	RMAP_FreeBuffer(packet)

	return packetByteList, packetStruct

def RMAP_BuildReadRegisterPacket(targetAddress, replyAddress, incrementAddress, key,
								 transactionIdentifier, readAddress, extendedReadAddress, alignment) ->\
		Tuple[list, RMAP_PACKET_EXTERNAL]:
	""" Builds an RMAP read command packet which can be transmitted to perform an RMAP
		read command on a 4-byte register.

		Returns a tuple: a list containing the packet bytes and an `STAR_system.rmap_packet_library.RMAP_PACKET_EXTERNAL` object
						 containing the RMAP packet contents.

		Args:\n
			targetAddress (list of ints): List containing the target address bytes.
			replyAddress (list of ints): List containing the reply address bytes.
			incrementAddress (bool): Whether the target read address should be
									 incremented when reading or not.
			key (int): The key (value) expected by the destination device.
			transactionIdentifier (int): An identifier for the transaction.
			readAddress (int): The memory address at the destination to read from.
			extendedReadAddress (int): The extended memory address at the destination to read from.
			alignment (int): The word size used by the device sending the packet, normally 1.

		Raises:\n
			STARAPIError:\n
				The RMAP packet library could not be loaded.\n
				RMAP Build Read Register Packet failed.\n
				Could not populate external RMAP packet structure.\n

			TypeError:\n
				targetAddress must be a list.\n
				at least one element in targetAddress was not an int.\n
				replyAddress must be a list.\n
				at least one element in replyAddress was not an int.\n
				incrementAddress was not a bool.\n
				key was not an int.\n
				transactionIdentifier must be an int.\n
				readAddress must be an int.\n
				extendedReadAddress must be an int.\n
				alignment must be an int.\n

			ValueError:\n
				every element in targetAddress must be between 0 and 255.\n
				every element in replyAddress must be between 0 and 255.\n
				key must be between 0 and 255.\n
				transactionIdentifier must be between 0 and 65535.\n
				extendedReadAddress must be between 0 and 255.\n
				alignment must be between 0 and 127.\n
	"""

	# Protect against invalid RMAP packet library
	if dll_rmap is None:
		raise STARAPIError(RMAP_API_LIB_LOAD_ERROR_STR)

	# Handle type errors and value errors
	if isinstance(targetAddress, list) is False:
		raise TypeError("targetAddress must be a list.")

	for targetAddressByte in targetAddress:
		if type(targetAddressByte) != int:
			raise TypeError("every element in targetAddress must be an int.")
		if targetAddressByte < 0 or targetAddressByte > 255:
			raise ValueError("each target address byte must be between 0 and 255.")

	if isinstance(replyAddress, list) is False:
		raise TypeError("replyAddress must be a list.")

	for replyAddressByte in replyAddress:
		if type(replyAddressByte) != int:
			raise TypeError("every element in replyAddress must be an int.")
		if replyAddressByte < 0 or replyAddressByte > 255:
			raise ValueError("each reply address byte must be between 0 and 255.")

	if type(incrementAddress) != bool:
		raise TypeError("incrementAddress must be a bool.")

	if type(key) != int:
		raise TypeError("key must be an int.")

	if key < 0 or key > 255:
		raise ValueError("key must be between 0 and 255.")

	if type(transactionIdentifier) != int:
		raise TypeError("transactionIdentifier must be an int.")

	if transactionIdentifier < 0 or transactionIdentifier > 65535:
		raise ValueError("transactionIdentifier must be between 0 and 65535.")

	if type(readAddress) != int:
		raise TypeError("readAddress must be an int.")

	if type(extendedReadAddress) != int:
		raise TypeError("extendedReadAddress must be an int.")

	if extendedReadAddress < 0 or extendedReadAddress > 255:
		raise ValueError("extendedReadAddress must be between 0 and 255.")

	if type(alignment) != int:
		raise TypeError("alignment must be an int.")

	if alignment < 0 or alignment > 127:
		raise ValueError("alignment must be between 0 and 127.")

	# Get the length of the target address
	targetAddressLength = len(targetAddress)

	# Get the length of the reply address
	replyAddressLength = len(replyAddress)

	# Set up an array holding the target address bytes
	cTargetArray = (c_uint8 * targetAddressLength)()

	# Assign the target address bytes
	for i in range(0, targetAddressLength):
		cTargetArray[i] = targetAddress[i]

	# Set up an array holding the reply address bytes
	cReplyArray = (c_uint8 * replyAddressLength)()

	# Assign the reply address bytes
	for j in range(0, replyAddressLength):
		cReplyArray[j] = replyAddress[j]

	# Cast to pointers (for marshalling purposes)
	cTargetArrayPointer = pointer(cTargetArray)
	cReplyArrayPointer = pointer(cReplyArray)

	# Variable holding the length of the raw packet (to be created)
	rawPacketLength = c_ulong(0)
	pRawPacketLength = pointer(rawPacketLength)

	# Create packet structure pointer
	packetStructInternal = RMAP_PACKET()
	packetStructInternalPtr = pointer(packetStructInternal)

	# Set argument types and return type of the C function
	dll_rmap.RMAP_BuildReadRegisterPacket.argtypes = [
		POINTER(c_uint8 * targetAddressLength), c_ulong, POINTER(c_uint8 * replyAddressLength), c_ulong,
		c_char, c_uint8, c_uint16, c_uint32, c_uint8, POINTER(c_ulong), POINTER(RMAP_PACKET), c_char]
	dll_rmap.RMAP_BuildReadRegisterPacket.restype = c_void_p

	packet = dll_rmap.RMAP_BuildReadRegisterPacket(cTargetArrayPointer, c_ulong(targetAddressLength), cReplyArrayPointer,
												   c_ulong(replyAddressLength), c_char(incrementAddress), c_uint8(key),
												   c_uint16(transactionIdentifier), c_uint32(readAddress),
												   c_uint8(extendedReadAddress), pRawPacketLength, packetStructInternalPtr,
												   c_char(alignment))

	if packet is None or rawPacketLength.value == 0:
		raise STARAPIError("RMAP Build Read Register Packet failed.")

	# Create packet structure object for external use
	try:
		packetStruct = PopulateExternalRMAPStructure(packetStructInternal)
	except STARAPIError:
		raise

	# Cast packet to a pointer of bytes
	packetPtr = cast(packet, POINTER(c_ubyte))

	packetByteList = []
	for i in range(0, rawPacketLength.value):
		packetByteList.append(packetPtr[i])

	# Free packet
	RMAP_FreeBuffer(packet)

	return packetByteList, packetStruct

def RMAP_BuildReadReplyPacket(initiatorAddress, targetAddress, incrementAddress, status,
							  transactionIdentifier, data, alignment) -> Tuple[list, RMAP_PACKET_EXTERNAL]:
	""" Builds an RMAP read reply packet which can be transmit to respond to an RMAP read command.

		Returns a tuple: a list containing the packet bytes and an `STAR_system.rmap_packet_library.RMAP_PACKET_EXTERNAL` object
						 containing the RMAP packet contents.

		Args:\n
			initiatorAddress (list of ints): List containing the logical address bytes
											 of the device to which the reply should be sent.
			targetAddress (int): The SpaceWire logical address bytes of the device that sent the
								 command being responded to.
			incrementAddress (bool): Whether the target read address should be
									 incremented when reading or not.
			status (STAR_system.rmap_packet_library.RMAP_STATUS): The status of the read operation.
			transactionIdentifier (int): An identifier for the transaction.
			data (list of ints): The data read.
			alignment (int): The word size used by the device sending the packet, normally 1.

		Raises:\n
			STARAPIError:\n
				The RMAP packet library could not be loaded.\n
				RMAP Build Read Reply Packet failed.\n
				Could not populate external RMAP packet structure.\n

			TypeError:\n
				initiatorAddress must be a list.\n
				at least one element in initiatorAddress was not an int.\n
				targetAddress must be an int.\n
				transactionIdentifier must be an int.\n
				data must be a list.\n
				at least one element in data was not an int.\n
				alignment must be an int.\n

			ValueError:\n
				every element in initiatorAddress must be between 0 and 255.\n
				targetAddress must be between 0 and 255.\n
				transactionIdentifier must be between 0 and 65535.\n
				every element in data must be between 0 and 255.\n
				alignment must be between 0 and 127.\n
	"""

	# Protect against invalid RMAP packet library
	if dll_rmap is None:
		raise STARAPIError(RMAP_API_LIB_LOAD_ERROR_STR)

	# Handle type errors and value errors
	if isinstance(initiatorAddress, list) is False:
		raise TypeError("initiatorAddress must be a list.")

	for initiatorAddressByte in initiatorAddress:
		if type(initiatorAddressByte) != int:
			raise TypeError("every element in initiatorAddress must be an int.")
		if initiatorAddressByte < 0 or initiatorAddressByte > 255:
			raise ValueError("each initiator address byte must be between 0 and 255.")

	if type(targetAddress) != int:
		raise TypeError("targetAddress must be an int.")

	if targetAddress < 0 or targetAddress > 255:
		raise ValueError("targetAddress must be between 0 and 255.")

	if type(incrementAddress) != bool:
		raise TypeError("incrementAddress must be a bool.")

	if type(transactionIdentifier) != int:
		raise TypeError("transactionIdentifier must be an int.")

	if transactionIdentifier < 0 or transactionIdentifier > 65535:
		raise ValueError("transactionIdentifier must be between 0 and 65535.")

	for dataByte in data:
		if type(dataByte) != int:
			raise TypeError("every element in data must be an int.")
		if dataByte < 0 or dataByte > 255:
			raise ValueError("each data byte must be between 0 and 255.")

	if type(alignment) != int:
		raise TypeError("alignment must be an int.")

	if alignment < 0 or alignment > 127:
		raise ValueError("alignment must be between 0 and 127.")

	# Get the length of the initiator address
	initiatorAddressLength = len(initiatorAddress)

	# Set up an array holding the initiator address bytes
	cInitiatorArray = (c_uint8 * initiatorAddressLength)()

	# Assign initiator address byte values
	for i in range(0, initiatorAddressLength):
		cInitiatorArray[i] = initiatorAddress[i]

	# Cast to pointer (for marshalling purposes)
	cInitiatorArrayPointer = pointer(cInitiatorArray)

	# Get the data length
	dataLength = len(data)

	# Set up an array holding the data bytes
	cDataArray = (c_uint8 * dataLength)()

	# Assign the data byte values
	for i in range(0, dataLength):
		cDataArray[i] = data[i]

	# Cast to pointer (for marshalling purposes)
	cDataArrayPointer = pointer(cDataArray)

	# Variable holding the length of the raw packet
	rawPacketLength = c_ulong(0)
	pRawPacketLength = pointer(rawPacketLength)

	# Create packet structure pointer
	packetStructInternal = RMAP_PACKET()
	packetStructInternalPtr = pointer(packetStructInternal)

	# Set argument types and return type of the C function
	dll_rmap.RMAP_BuildReadReplyPacket.argtypes = [
		POINTER(c_uint8 * initiatorAddressLength), c_ulong, c_uint8, c_char, RMAP_STATUS, c_uint16,
		POINTER(c_uint8 * dataLength), c_uint32, POINTER(c_ulong), POINTER(RMAP_PACKET), c_char]
	dll_rmap.RMAP_BuildReadReplyPacket.restype = c_void_p

	packet = dll_rmap.RMAP_BuildReadReplyPacket(cInitiatorArrayPointer, c_ulong(initiatorAddressLength),
												c_uint8(targetAddress), c_char(incrementAddress), status,
												c_uint16(transactionIdentifier), cDataArrayPointer,
												c_uint32(dataLength), pRawPacketLength, packetStructInternalPtr,
												c_char(alignment))

	if packet is None or rawPacketLength.value == 0:
		raise STARAPIError("RMAP Build Read Reply Packet failed.")

	# Create packet structure object for external use
	try:
		packetStruct = PopulateExternalRMAPStructure(packetStructInternal)
	except STARAPIError:
		raise

	# Cast packet to a pointer of bytes
	packetPtr = cast(packet, POINTER(c_ubyte))

	packetByteList = []
	for i in range(0, rawPacketLength.value):
		packetByteList.append(packetPtr[i])

	# Free packet
	RMAP_FreeBuffer(packet)

	return packetByteList, packetStruct

def RMAP_BuildWriteCommandPacket(targetAddress, replyAddress, verifyBeforeWrite, acknowledge, incrementAddress, key,
								 transactionIdentifier, writeAddress, extendedWriteAddress, data, alignment) ->\
		Tuple[list, RMAP_PACKET_EXTERNAL]:
	""" Builds an RMAP write command packet which can be transmitted to perform an RMAP write command.

		Returns a tuple: a list containing the packet bytes and an `STAR_system.rmap_packet_library.RMAP_PACKET_EXTERNAL` object
						 containing the RMAP packet contents.

		Args:\n
			targetAddress (list of ints): List containing the target address bytes.
			replyAddress (list of ints): List containing the reply address bytes.
			verifyBeforeWrite (bool): Whether or not the data should be verified before writing.
			acknowledge (bool): Whether or not the command should be acknowledged.
			incrementAddress (bool): Whether the target read address should be
									 incremented when reading or not.
			key (int): The key (value) expected by the destination device.
			transactionIdentifier (int): An identifier for the transaction.
			writeAddress (int): The memory address at the destination to write to.
			extendedWriteAddress (int): The extended memory address at the destination to read from
			data (list of ints): The data to write.
			alignment (int): The word size used by the device sending the packet, normally 1.

		Raises:\n
			STARAPIError:\n
				The RMAP packet library could not be loaded.\n
				RMAP Build Write Command Packet failed.\n
				Could not populate external RMAP packet structure.\n

			TypeError:\n
				targetAddress must be a list.\n
				at least one element in targetAddress was not an int.\n
				replyAddress must be a list.\n
				at least one element in replyAddress was not an int.\n
				incrementAddress was not a bool.\n
				key was not an int.\n
				transactionIdentifier must be an int.\n
				readAddress must be an int.\n
				extendedWriteAddress must be an int.\n
				alignment must be an int.\n

			ValueError:\n
				every element in targetAddress must be between 0 and 255.\n
				every element in replyAddress must be between 0 and 255.\n
				key must be between 0 and 255.\n
				transactionIdentifier must be between 0 and 65535.\n
				extendedWriteAddress must be between 0 and 255.\n
				alignment must be between 0 and 127.\n
	"""

	# Protect against invalid RMAP packet library
	if dll_rmap is None:
		raise STARAPIError(RMAP_API_LIB_LOAD_ERROR_STR)

	# Handle type errors and value errors
	if isinstance(targetAddress, list) is False:
		raise TypeError("targetAddress must be a list.")

	for targetAddressByte in targetAddress:
		if type(targetAddressByte) != int:
			raise TypeError("every element in targetAddress must be an int.")
		if targetAddressByte < 0 or targetAddressByte > 255:
			raise ValueError("each target address byte must be between 0 and 255.")

	if isinstance(replyAddress, list) is False:
		raise TypeError("replyAddress must be a list.")

	for replyAddressByte in replyAddress:
		if type(replyAddressByte) != int:
			raise TypeError("every element in replyAddress must be an int.")
		if replyAddressByte < 0 or replyAddressByte > 255:
			raise ValueError("each reply address byte must be between 0 and 255.")

	if type(verifyBeforeWrite) != bool:
		raise TypeError("verifyBeforeWrite must be a bool.")

	if type(acknowledge) != bool:
		raise TypeError("acknowledge must be a bool.")

	if type(incrementAddress) != bool:
		raise TypeError("incrementAddress must be a bool.")

	if type(key) != int:
		raise TypeError("key must be an int.")

	if key < 0 or key > 255:
		raise ValueError("key must be between 0 and 255.")

	if type(transactionIdentifier) != int:
		raise TypeError("transactionIdentifier must be an int.")

	if transactionIdentifier < 0 or transactionIdentifier > 65535:
		raise ValueError("transactionIdentifier must be between 0 and 65535.")

	if type(writeAddress) != int:
		raise TypeError("writeAddress must be an int.")

	if type(extendedWriteAddress) != int:
		raise TypeError("extendedWriteAddress must be an int.")

	if extendedWriteAddress < 0 or extendedWriteAddress > 255:
		raise ValueError("extendedWriteAddress must be between 0 and 255.")

	if type(alignment) != int:
		raise TypeError("alignment must be an int.")

	if alignment < 0 or alignment > 127:
		raise ValueError("alignment must be between 0 and 127.")

	# Get length of target address
	targetAddressLength = len(targetAddress)

	# Get length of reply address
	replyAddressLength = len(replyAddress)

	# Set up array to hold the target address bytes
	cTargetArray = (c_uint8 * targetAddressLength)()

	# Assign the target address bytes
	for i in range(0, targetAddressLength):
		cTargetArray[i] = targetAddress[i]

	# Set up array to hold the reply address bytes
	cReplyArray = (c_uint8 * replyAddressLength)()

	# Assign the reply address bytes
	for j in range(0, replyAddressLength):
		cReplyArray[j] = replyAddress[j]

	# Cast to pointer types
	cTargetArrayPointer = pointer(cTargetArray)
	cReplyArrayPointer = pointer(cReplyArray)

	# Get the length of the data
	dataLength = len(data)

	# Set up array to hold the data bytes
	cDataArray = (c_uint8 * dataLength)()

	# Assign the data bytes
	for i in range(0, dataLength):
		cDataArray[i] = data[i]

	# Cast to pointer type
	cDataArrayPointer = pointer(cDataArray)

	# Variable to hold the length of the raw packet
	rawPacketLength = c_ulong(0)
	pRawPacketLength = pointer(rawPacketLength)

	# Create packet structure pointer
	packetStructInternal = RMAP_PACKET()
	packetStructInternalPtr = pointer(packetStructInternal)

	# Set argument types and return type of the C function
	dll_rmap.RMAP_BuildWriteCommandPacket.argtypes = [POINTER(c_uint8 * targetAddressLength), c_ulong,
													  POINTER(c_uint8 * replyAddressLength), c_ulong,
													  c_char, c_char, c_char, c_uint8, c_uint16, c_uint32, c_uint8,
													  POINTER(c_uint8 * dataLength), c_uint32, POINTER(c_ulong),
													  POINTER(RMAP_PACKET), c_char]
	dll_rmap.RMAP_BuildWriteCommandPacket.restype = c_void_p

	packet = dll_rmap.RMAP_BuildWriteCommandPacket(cTargetArrayPointer, c_ulong(targetAddressLength), cReplyArrayPointer,
												   c_ulong(replyAddressLength), c_char(verifyBeforeWrite),
												   c_char(acknowledge), c_char(incrementAddress),
												   c_uint8(key), c_uint16(transactionIdentifier), c_uint32(writeAddress),
												   c_uint8(extendedWriteAddress), cDataArrayPointer,
												   c_uint32(dataLength), pRawPacketLength, packetStructInternalPtr, c_char(alignment))

	if packet is None or rawPacketLength.value == 0:
		raise STARAPIError("RMAP Build Write Command Packet failed.")

	# Create packet structure object for external use
	try:
		packetStruct = PopulateExternalRMAPStructure(packetStructInternal)
	except STARAPIError:
		raise

	# Cast packet to a pointer of bytes
	packetPtr = cast(packet, POINTER(c_ubyte))

	packetByteList = []
	for i in range(0, rawPacketLength.value):
		packetByteList.append(packetPtr[i])

	# Free packet
	RMAP_FreeBuffer(packet)

	return packetByteList, packetStruct

def RMAP_BuildWriteRegisterPacket(targetAddress, replyAddress, verifyBeforeWrite, acknowledge,
								  incrementAddress, key, transactionIdentifier, writeAddress,
								  extendedWriteAddress, registerValue, alignment) -> Tuple[list, RMAP_PACKET_EXTERNAL]:
	""" Builds an RMAP write command packet which can be transmitted to perform an RMAP
		write command on a 4-byte register.

		Returns a tuple: a list containing the packet bytes and an `STAR_system.rmap_packet_library.RMAP_PACKET_EXTERNAL` object
						 containing the RMAP packet contents.

		Args:\n
			targetAddress (list of ints): List containing the target address bytes.
			replyAddress (list of ints): List containing the reply address bytes.
			verifyBeforeWrite (bool): Whether or not the data should be verified before writing.
			acknowledge (bool): Whether or not the command should be acknowledged.
			incrementAddress (bool): Whether the target read address should be
									 incremented when reading or not.
			key (int): The key (value) expected by the destination device.
			transactionIdentifier (int): An identifier for the transaction.
			writeAddress (int): The memory address at the destination to write to.
			extendedWriteAddress (int): The extended memory address at the destination to write to.
			registerValue (int): The value to be written to the register.
			alignment (int): The word size used by the device sending the packet, normally 1.

		Raises:\n
			STARAPIError:\n
				The RMAP packet library could not be loaded.\n
				RMAP Build Write Register Packet failed.\n
				Could not populate external RMAP packet structure.\n

			TypeError:\n
				targetAddress must be a list.\n
				at least one element in targetAddress was not an int.\n
				replyAddress must be a list.\n
				at least one element in replyAddress was not an int.\n
				verifyBeforeWrite was not a bool.\n
				acknowledge was not a bool.\n
				incrementAddress was not a bool.\n
				key was not an int.\n
				transactionIdentifier must be an int.\n
				writeAddress must be an int.\n
				extendedWriteAddress must be an int.\n
				registerValue must be an int.\n
				alignment must be an int.\n

			ValueError:\n
				every element in targetAddress must be between 0 and 255.\n
				every element in replyAddress must be between 0 and 255.\n
				key must be between 0 and 255.\n
				transactionIdentifier must be between 0 and 65535.\n
				extendedWriteAddress must be between 0 and 255.\n
				alignment must be between 0 and 127.\n
		"""

	# Protect against invalid RMAP packet library
	if dll_rmap is None:
		raise STARAPIError(RMAP_API_LIB_LOAD_ERROR_STR)

	# Handle type errors and value errors
	if isinstance(targetAddress, list) is False:
		raise TypeError("targetAddress must be a list.")

	for targetAddressByte in targetAddress:
		if type(targetAddressByte) != int:
			raise TypeError("every element in targetAddress must be an int.")
		if targetAddressByte < 0 or targetAddressByte > 255:
			raise ValueError("each target address byte must be between 0 and 255.")

	if isinstance(replyAddress, list) is False:
		raise TypeError("replyAddress must be a list.")

	for replyAddressByte in replyAddress:
		if type(replyAddressByte) != int:
			raise TypeError("every element in replyAddress must be an int.")
		if replyAddressByte < 0 or replyAddressByte > 255:
			raise ValueError("each reply address byte must be between 0 and 255.")

	if type(verifyBeforeWrite) != bool:
		raise TypeError("verifyBeforeWrite must be a bool.")

	if type(acknowledge) != bool:
		raise TypeError("acknowledge must be a bool.")

	if type(incrementAddress) != bool:
		raise TypeError("incrementAddress must be a bool.")

	if type(key) != int:
		raise TypeError("key must be an int.")

	if key < 0 or key > 255:
		raise ValueError("key must be between 0 and 255.")

	if type(transactionIdentifier) != int:
		raise TypeError("transactionIdentifier must be an int.")

	if transactionIdentifier < 0 or transactionIdentifier > 65535:
		raise ValueError("transactionIdentifier must be between 0 and 65535.")

	if type(writeAddress) != int:
		raise TypeError("writeAddress must be an int.")

	if type(extendedWriteAddress) != int:
		raise TypeError("extendedWriteAddress must be an int.")

	if extendedWriteAddress < 0 or extendedWriteAddress > 255:
		raise ValueError("extendedWriteAddress must be between 0 and 255.")

	if type(registerValue) != int:
		raise TypeError("registerValue must be an int.")

	if type(alignment) != int:
		raise TypeError("alignment must be an int.")

	if alignment < 0 or alignment > 127:
		raise ValueError("alignment must be between 0 and 127.")

	# Get length of the target address
	targetAddressLength = len(targetAddress)

	# Get length of the reply address
	replyAddressLength = len(replyAddress)

	# Create array for target address bytes
	cTargetArray = (c_uint8 * targetAddressLength)()

	# Assign the target address values
	for i in range(0, targetAddressLength):
		cTargetArray[i] = targetAddress[i]

	# Create array for replay address bytes
	cReplyArray = (c_uint8 * replyAddressLength)()

	# Assign the reply address values
	for j in range(0, replyAddressLength):
		cReplyArray[j] = replyAddress[j]

	# Cast to pointer type
	cTargetArrayPointer = pointer(cTargetArray)
	cReplyArrayPointer = pointer(cReplyArray)

	# Variable holding the raw packet length
	rawPacketLength = c_ulong(0)
	pRawPacketLength = pointer(rawPacketLength)

	# Create packet structure pointer
	packetStructInternal = RMAP_PACKET()
	packetStructInternalPtr = pointer(packetStructInternal)

	# Set argument types and return type of the C function
	dll_rmap.RMAP_BuildWriteRegisterPacket.argtypes = [POINTER(c_uint8 * targetAddressLength), c_ulong,
													   POINTER(c_uint8 * replyAddressLength), c_ulong, c_char, c_char,
													   c_char, c_uint8, c_uint16, c_uint32, c_uint8, c_uint32,
													   POINTER(c_ulong), POINTER(RMAP_PACKET), c_char]
	dll_rmap.RMAP_BuildWriteRegisterPacket.restype = c_void_p

	packet = dll_rmap.RMAP_BuildWriteRegisterPacket(cTargetArrayPointer, c_ulong(targetAddressLength), cReplyArrayPointer,
													c_ulong(replyAddressLength), c_char(verifyBeforeWrite),
													c_char(acknowledge), c_char(incrementAddress),
													c_uint8(key), c_uint16(transactionIdentifier), c_uint32(writeAddress),
													c_uint8(extendedWriteAddress), c_uint32(registerValue),
													pRawPacketLength, packetStructInternalPtr, c_char(alignment))

	if packet is None or rawPacketLength.value == 0:
		raise STARAPIError("RMAP Build Write Register Packet failed.")

	# Create packet structure object for external use
	try:
		packetStruct = PopulateExternalRMAPStructure(packetStructInternal)
	except STARAPIError:
		raise

	# Cast packet to a pointer of bytes
	packetPtr = cast(packet, POINTER(c_ubyte))

	packetByteList = []
	for i in range(0, rawPacketLength.value):
		packetByteList.append(packetPtr[i])

	# Free packet
	RMAP_FreeBuffer(packet)

	return packetByteList, packetStruct

def RMAP_BuildWriteReplyPacket(initiatorAddress, targetAddress, verifyBeforeWrite,
							   incrementAddress, status, transactionIdentifier, alignment) -> Tuple[list, RMAP_PACKET_EXTERNAL]:

	""" Builds an RMAP write reply packet which can be transmit to respond to an RMAP write command.

		Returns a tuple: a list containing the packet bytes and an `STAR_system.rmap_packet_library.RMAP_PACKET_EXTERNAL` object
						 containing the RMAP packet contents.

		Args:\n
			initiatorAddress (list of ints): List containing the logical address bytes
											 of the device to which the reply should be sent.
			targetAddress (int): The SpaceWire logical address bytes of the device that sent the
								 command being responded to.
			verifyBeforeWrite (bool): Whether or not the data should be verified before writing.
			incrementAddress (bool): Whether the target read address should be
									 incremented when reading or not.
			status (STAR_system.rmap_packet_library.RMAP_STATUS): The status of the read operation.
			transactionIdentifier (int): An identifier for the transaction.
			alignment (int): The word size used by the device sending the packet, normally 1.

		Raises:\n
			STARAPIError:\n
				The RMAP packet library could not be loaded.\n
				RMAP Build Write Reply Packet failed.\n
				Could not populate external RMAP packet structure.\n

			TypeError:\n
				initiatorAddress must be a list.\n
				at least one element in initiatorAddress was not an int.\n
				targetAddress must be an int.\n
				verifyBeforeWrite must be a bool.\n
				incrementAddress must be a bool.\n
				transactionIdentifier must be an int.\n
				alignment must be an int.\n

			ValueError:\n
				every element in initiatorAddress must be between 0 and 255.\n
				targetAddress must be between 0 and 255.\n
				transactionIdentifier must be between 0 and 65535.\n
				alignment must be between 0 and 127.\n
	"""

	# Protect against invalid RMAP packet library
	if dll_rmap is None:
		raise STARAPIError(RMAP_API_LIB_LOAD_ERROR_STR)

	# Handle type errors and value errors
	if isinstance(initiatorAddress, list) is False:
		raise TypeError("initiatorAddress must be a list.")

	for initiatorAddressByte in initiatorAddress:
		if type(initiatorAddressByte) != int:
			raise TypeError("every element in initiatorAddress must be an int.")
		if initiatorAddressByte < 0 or initiatorAddressByte > 255:
			raise ValueError("each initiator address byte must be between 0 and 255.")

	if type(targetAddress) != int:
		raise TypeError("targetAddress must be an int.")

	if targetAddress < 0 or targetAddress > 255:
		raise ValueError("targetAddress must be between 0 and 255.")

	if type(verifyBeforeWrite) != bool:
		raise TypeError("verifyBeforeWrite must be a bool.")

	if type(incrementAddress) != bool:
		raise TypeError("incrementAddress must be a bool.")

	if type(transactionIdentifier) != int:
		raise TypeError("transactionIdentifier must be an int.")

	if transactionIdentifier < 0 or transactionIdentifier > 65535:
		raise ValueError("transactionIdentifier must be between 0 and 65535.")

	if type(alignment) != int:
		raise TypeError("alignment must be an int.")

	if alignment < 0 or alignment > 127:
		raise ValueError("alignment must be between 0 and 127.")

	# Get the length of the initiator address
	initiatorAddressLength = len(initiatorAddress)

	# Set up array that holds the initiator address bytes
	cInitiatorArray = (c_uint8 * initiatorAddressLength)()

	# Assign the initiator address byte values
	for i in range(0, initiatorAddressLength):
		cInitiatorArray[i] = initiatorAddress[i]

	# Cast to pointer (for marshalling purposes)
	cInitiatorArrayPointer = pointer(cInitiatorArray)

	# Variable holding the raw packet length
	rawPacketLength = c_ulong(0)
	pRawPacketLength = pointer(rawPacketLength)

	# Create packet structure pointer
	packetStructInternal = RMAP_PACKET()
	packetStructInternalPtr = pointer(packetStructInternal)

	# Set argument types and return type of the C function
	dll_rmap.RMAP_BuildWriteReplyPacket.argtypes = [POINTER(c_uint8 * initiatorAddressLength), c_ulong, c_uint8, c_char,
													c_char, RMAP_STATUS, c_uint16, POINTER(c_ulong),
													POINTER(RMAP_PACKET), c_char]
	dll_rmap.RMAP_BuildWriteReplyPacket.restype = c_void_p

	packet = dll_rmap.RMAP_BuildWriteReplyPacket(cInitiatorArrayPointer, c_ulong(initiatorAddressLength),
												 c_uint8(targetAddress), c_char(verifyBeforeWrite),
												 c_char(incrementAddress), status, c_uint16(transactionIdentifier),
												 pRawPacketLength, packetStructInternalPtr, c_char(alignment))

	if packet is None or rawPacketLength.value == 0:
		raise STARAPIError("RMAP Build Write Reply Packet failed.")

	# Create packet structure object for external use
	try:
		packetStruct = PopulateExternalRMAPStructure(packetStructInternal)
	except STARAPIError:
		raise

	# Cast packet to a pointer of bytes
	packetPtr = cast(packet, POINTER(c_ubyte))

	packetByteList = []
	for i in range(0, rawPacketLength.value):
		packetByteList.append(packetPtr[i])

	# Free packet
	RMAP_FreeBuffer(packet)

	return packetByteList, packetStruct

def RMAP_CalculateReadCommandPacketLength(targetAddressLength, replyAddressLength, alignment) -> int:

	""" Calculates the number of bytes required for an RMAP read command packet, given the
		properties of the packet.\n

		Returns the calculated length of the RMAP read command packet.

		Args:\n
			targetAddressLength (int): Length of the target address.
			replyAddressLength (int): Length of the reply address.
			alignment (int): The word size used by the device sending the packet, normally 1.

		Raises:\n
			STARAPIError:\n
				The RMAP packet library could not be loaded.\n
			TypeError:\n
				targetAddressLength was not an int.\n
				replyAddressLength was not an int.\n
				alignment was not an int.\n
			ValueError:\n
				alignment must be between 0 and 127.\n
	"""

	# Protect against invalid RMAP packet library
	if dll_rmap is None:
		raise STARAPIError(RMAP_API_LIB_LOAD_ERROR_STR)

	if type(targetAddressLength) != int:
		raise TypeError("targetAddressLength must be an int.")

	if type(replyAddressLength) != int:
		raise TypeError("replyAddressLength must be an int.")

	if type(alignment) != int:
		raise TypeError("alignment must be an int.")

	if alignment < 0 or alignment > 127:
		raise ValueError("alignment must be between 0 and 127.")

	# Set argument types and return type of the C function
	dll_rmap.RMAP_CalculateReadCommandPacketLength.argtypes = [c_ulong, c_ulong, c_char]
	dll_rmap.RMAP_CalculateReadCommandPacketLength.restype = c_ulong

	calcLength = dll_rmap.RMAP_CalculateReadCommandPacketLength(c_ulong(targetAddressLength),
																c_ulong(replyAddressLength), c_char(alignment))
	return calcLength

def RMAP_CalculateReadModifyWriteCommandPacketLength(targetAddressLength, replyAddressLength, dataAndMaskLength,
													 alignment) -> int:

	""" Calculates the number of bytes required for an RMAP read-modify-write command packet
		given the properties of the packet.\n

		Returns the calculated length of the RMAP read/modify/write command packet.

		Args:\n
			targetAddressLength (int): Length of the target address.
			replyAddressLength (int): Length of the reply address.
			dataAndMaskLength (int): The combined length in bytes of the data and mask fields.
									 This should be an even number between 0 and 8.
			alignment (int): The word size used by the device sending the packet, normally 1.

		Raises:\n
			STARAPIError:\n
				The RMAP packet library could not be loaded.\n

			TypeError:\n
				targetAddressLength was not an int.\n
				replyAddressLength was not an int.\n
				dataAndMaskLength was not an int.\n
				alignment was not an int.\n

			ValueError:\n
				alignment must be between 0 and 127.\n
	"""

	# Protect against invalid RMAP packet library
	if dll_rmap is None:
		raise STARAPIError(RMAP_API_LIB_LOAD_ERROR_STR)

	# Handle type errors
	if type(targetAddressLength) != int:
		raise TypeError("targetAddressLength must be an int.")

	if type(replyAddressLength) != int:
		raise TypeError("replyAddressLength must be an int.")

	if type(dataAndMaskLength) != int:
		raise TypeError("dataAndMaskLength must be an int.")

	if type(alignment) != int:
		raise TypeError("alignment must be an int.")

	if alignment < 0 or alignment > 127:
		raise ValueError("alignment must be between 0 and 127.")

	# Set argument types and return type of the C function
	dll_rmap.RMAP_CalculateReadModifyWriteCommandPacketLength.argtypes = [c_ulong, c_ulong, c_uint32, c_char]
	dll_rmap.RMAP_CalculateReadModifyWriteCommandPacketLength.restype = c_ulong

	calcLength = dll_rmap.RMAP_CalculateReadModifyWriteCommandPacketLength(c_ulong(targetAddressLength),
																		   c_ulong(replyAddressLength),
																		   c_uint32(dataAndMaskLength),
																		   c_char(alignment))

	return calcLength

def RMAP_CalculateReadModifyWriteReplyPacketLength(initiatorAddressLength, dataLength, alignment) -> int:
	""" Calculates the number of bytes required for an RMAP read/modify/write reply packet
		given the properties of the packet.\n

		Returns the calculated length of the RMAP read/modify/write reply packet.

		Args:\n
			initiatorAddressLength (int): Length of the initiator address.
			dataLength (int): The length of the data field.
			alignment (int): The word size used by the device sending the packet, normally 1.

		Raises:\n
			STARAPIError:\n
				The RMAP packet library could not be loaded.\n

			TypeError:\n
				initiatorAddressLength was not an int.\n
				dataLength was not an int.\n
				alignment was not an int.\n
			ValueError:\n
				alignment must be between 0 and 127.\n
	"""

	# Protect against invalid RMAP packet library
	if dll_rmap is None:
		raise STARAPIError(RMAP_API_LIB_LOAD_ERROR_STR)

	# Handle type errors
	if type(initiatorAddressLength) != int:
		raise TypeError("initiatorAddressLength must be an int.")

	if type(dataLength) != int:
		raise TypeError("dataLength must be an int.")

	if type(alignment) != int:
		raise TypeError("alignment must be an int.")

	if alignment < 0 or alignment > 127:
		raise ValueError("alignment must be between 0 and 127.")

	# Set argument types and return type of the C function
	dll_rmap.RMAP_CalculateReadModifyWriteReplyPacketLength.argtypes = [c_ulong, c_uint32, c_char]
	dll_rmap.RMAP_CalculateReadModifyWriteReplyPacketLength.restype = c_ulong

	calcLength = dll_rmap.RMAP_CalculateReadModifyWriteReplyPacketLength(c_ulong(initiatorAddressLength),
																		 c_uint32(dataLength), c_char(alignment))
	return calcLength

def RMAP_CalculateReadReplyPacketLength(initiatorAddressLength, dataLength, alignment) -> int:

	""" Calculates the number of bytes required for an RMAP read reply packet, given the
		properties of the packet.\n

		Returns the calculated length of the RMAP read reply packet.

		Args:\n
			initiatorAddressLength (int): Length of the initiator address.
			dataLength (int): The length of the data field.
			alignment (int): The word size used by the device sending the packet, normally 1.

		Raises:\n
			STARAPIError:\n
				The RMAP packet library could not be loaded.\n

			TypeError:\n
				initiatorAddressLength was not an int.\n
				dataLength was not an int.\n
				alignment was not an int.\n

			ValueError:\n
				alignment must be between 0 and 127.\n
	"""

	# Protect against invalid RMAP packet library
	if dll_rmap is None:
		raise STARAPIError(RMAP_API_LIB_LOAD_ERROR_STR)

	# Handle type errors
	if type(initiatorAddressLength) != int:
		raise TypeError("initiatorAddressLength must be an int.")

	if type(dataLength) != int:
		raise TypeError("dataLength must be an int.")

	if type(alignment) != int:
		raise TypeError("alignment must be an int.")

	if alignment < 0 or alignment > 127:
		raise ValueError("alignment must be between 0 and 127.")

	# Set argument types and return type of the C function
	dll_rmap.RMAP_CalculateReadReplyPacketLength.argtypes = [c_ulong, c_uint32, c_char]
	dll_rmap.RMAP_CalculateReadReplyPacketLength.restype = c_ulong

	calcLength = dll_rmap.RMAP_CalculateReadReplyPacketLength(c_ulong(initiatorAddressLength),
															  c_uint32(dataLength), c_char(alignment))
	return calcLength

def RMAP_CalculateWriteCommandPacketLength(targetAddressLength, replyAddressLength, dataLength, alignment) -> int:

	""" Calculates the number of bytes required for an RMAP write command packet, given the
		properties of the packet.\n

		Returns the calculated length of the RMAP write command packet.

		Args:\n
			targetAddressLength (int): Length of the target address.
			replyAddressLength (int): Length of the reply address.
			dataLength (int): The length of the data field (in bytes).
			alignment (int): The word size used by the device sending the packet, normally 1.

		Raises:\n
			STARAPIError:\n
				The RMAP packet library could not be loaded.\n

			TypeError:\n
				targetAddressLength was not an int.\n
				replyAddressLength was not an int.\n
				dataLength was not an int.\n
				alignment was not an int.\n

			ValueError:\n
				alignment must be between 0 and 127.\n
	"""

	# Protect against invalid RMAP packet library
	if dll_rmap is None:
		raise STARAPIError(RMAP_API_LIB_LOAD_ERROR_STR)

	if type(targetAddressLength) != int:
		raise TypeError("targetAddressLength must be an int.")

	if type(replyAddressLength) != int:
		raise TypeError("replyAddressLength must be an int.")

	if type(dataLength) != int:
		raise TypeError("dataLength must be an int.")

	if type(alignment) != int:
		raise TypeError("alignment must be an int.")

	if alignment < 0 or alignment > 127:
		raise ValueError("alignment must be between 0 and 127.")

	# Set argument types and return type of the C function
	dll_rmap.RMAP_CalculateWriteCommandPacketLength.argtypes = [c_ulong, c_ulong, c_uint32, c_char]
	dll_rmap.RMAP_CalculateWriteCommandPacketLength.restype = c_ulong

	calcLength = dll_rmap.RMAP_CalculateWriteCommandPacketLength(c_ulong(targetAddressLength),
																 c_ulong(replyAddressLength),
																 c_uint32(dataLength), c_char(alignment))
	return calcLength

def RMAP_CalculateWriteReplyPacketLength(initiatorAddressLength, alignment) -> int:

	""" Calculates the number of bytes required for an RMAP write reply packet, given the
		properties of the packet.\n

		Returns the calculated length of the RMAP write reply packet.

		Args:\n
			initiatorAddressLength (int): Length of the initiator address.
			alignment (int): The word size used by the device sending the packet, normally 1.

		Raises:\n
			STARAPIError:\n
				The RMAP packet library could not be loaded.\n

			TypeError:\n
				initiatorAddressLength was not an int.\n
				alignment was not an int.\n

			ValueError:\n
				alignment must be between 0 and 127.\n
	"""

	# Protect against invalid RMAP packet library
	if dll_rmap is None:
		raise STARAPIError(RMAP_API_LIB_LOAD_ERROR_STR)

	# Handle type errors
	if type(initiatorAddressLength) != int:
		raise TypeError("initiatorAddressLength must be an int.")

	if type(alignment) != int:
		raise TypeError("alignment must be an int.")

	if alignment < 0 or alignment > 127:
		raise ValueError("alignment must be between 0 and 127.")

	# Set argument types and return type of the C function
	dll_rmap.RMAP_CalculateWriteReplyPacketLength.argtypes = [c_ulong, c_char]
	dll_rmap.RMAP_CalculateWriteReplyPacketLength.restype = c_ulong

	calcLength = dll_rmap.RMAP_CalculateWriteReplyPacketLength(c_ulong(initiatorAddressLength), c_char(alignment))

	return calcLength

def RMAP_CheckPacketValid(rawPacketByteList, checkPacketTooLong) -> Tuple[RMAP_STATUS, RMAP_PACKET_EXTERNAL]:

	""" Checks that the given raw packet bytes list is in the correct format for an RMAP packet.

		Returns the status (`STAR_system.rmap_packet_library.RMAP_STATUS`) and `STAR_system.rmap_packet_library.RMAP_PACKET_EXTERNAL`
		object that is populated with the corresponding values taken from the list of raw packet bytes.

		Args:\n
			rawPacketByteList (list of ints): List of bytes of the raw packet.
			checkPacketTooLong (bool): To check whether packet is too long or not.

		Raises:\n
			STARAPIError:\n
				The RMAP packet library could not be loaded.\n

			TypeError:\n
				rawPacketByteList was not a list.\n
				at least an element in rawPacketByteList was not an int.\n
				checkPacketTooLong was not a bool.\n
			ValueError:\n
				each element in rawPacketByteList must be between 0 and 255.\n
	"""

	# Protect against invalid RMAP packet library
	if dll_rmap is None:
		raise STARAPIError(RMAP_API_LIB_LOAD_ERROR_STR)

	# Handle type errors
	if isinstance(rawPacketByteList, list) is False:
		raise TypeError("rawPacketByteList must be a list.")

	for rawPacketByte in rawPacketByteList:
		if type(rawPacketByte) != int:
			raise TypeError("every element in rawPacketByteList must be an int.")
		if rawPacketByte < 0 or rawPacketByte > 255:
			raise ValueError("each raw packet byte must be between 0 and 255.")

	if type(checkPacketTooLong) != bool:
		raise TypeError("checkPacketTooLong must be a bool.")

	# Get length of the target address
	rawPacketLength = len(rawPacketByteList)

	# Create array for raw packet bytes
	cRawPacketArray = (c_uint8 * rawPacketLength)()

	# Assign the target address values
	for i in range(0, rawPacketLength):
		cRawPacketArray[i] = rawPacketByteList[i]

	# Cast to pointer type
	cRawPacketArrayPointer = pointer(cRawPacketArray)

	# Create packet structure pointer
	packetStructInternal = RMAP_PACKET()
	packetStructInternalPtr = pointer(packetStructInternal)

	# Set argument types and return type of the C function
	dll_rmap.RMAP_CheckPacketValid.argtypes = [c_void_p, c_ulong, POINTER(RMAP_PACKET), c_char]
	dll_rmap.RMAP_CheckPacketValid.restype = RMAP_STATUS

	errorCode = dll_rmap.RMAP_CheckPacketValid(cRawPacketArrayPointer, c_ulong(rawPacketLength),
											   packetStructInternalPtr, c_char(checkPacketTooLong))

	packetStruct = None

	# In case of success
	if errorCode == RMAP_STATUS.RMAP_SUCCESS:
		packetStruct = PopulateExternalRMAPStructure(packetStructInternal)

	return errorCode, packetStruct

def RMAP_CheckPacketValidIgnoreProtocol(rawPacketByteList, checkPacketTooLong) ->\
		Tuple[RMAP_STATUS, Optional[RMAP_PACKET_EXTERNAL]]:

	""" Checks that the packet specified is in the correct format for an RMAP packet, but
		does not check that the protocol identifier used by the packet is the RMAP protocol ID.

		Returns the status (`STAR_system.rmap_packet_library.RMAP_STATUS`) and `STAR_system.rmap_packet_library.RMAP_PACKET_EXTERNAL`
		object that is populated with the corresponding values taken from the list of raw packet bytes.\n
		None is returned for the 2nd value of the tuple in case this function fails for any reason.

		Args:\n
			rawPacketByteList (list of ints): List of bytes of the raw packet.
			checkPacketTooLong (bool): To check whether packet is too long or not.

		Raises:\n
			STARAPIError:\n
				The RMAP packet library could not be loaded.\n
				Exception raised by PopulateExternalRMAPStructure.\n

			TypeError:\n
				rawPacketByteList was not a list.\n
				at least an element in rawPacketByteList was not an int.\n
				packetLength was not an int.\n
				packetStruct was not an RMAP_PACKET and was not None.\n

			ValueError:\n
				each element in rawPacketByteList must be between 0 and 255.\n
	"""

	# Protect against invalid RMAP packet library
	if dll_rmap is None:
		raise STARAPIError(RMAP_API_LIB_LOAD_ERROR_STR)

	# Handle type errors
	if isinstance(rawPacketByteList, list) is False:
		raise TypeError("rawPacketByteList must be a list.")

	for rawPacketByte in rawPacketByteList:
		if type(rawPacketByte) != int:
			raise TypeError("every element in rawPacketByteList must be an int.")
		if rawPacketByte < 0 or rawPacketByte > 255:
			raise ValueError("each raw packet byte must be between 0 and 255.")

	# Get length of the target address
	rawPacketLength = len(rawPacketByteList)

	# Create array for raw packet bytes
	cRawPacketArray = (c_uint8 * rawPacketLength)()

	# Assign the target address values
	for i in range(0, rawPacketLength):
		cRawPacketArray[i] = rawPacketByteList[i]

	# Cast to pointer type
	cRawPacketArrayPointer = pointer(cRawPacketArray)

	# Create packet structure pointer
	packetStructInternal = RMAP_PACKET()
	packetStructInternalPtr = pointer(packetStructInternal)

	# Set argument types and return type of the C function
	dll_rmap.RMAP_CheckPacketValidIgnoreProtocol.argtypes = [c_void_p, c_ulong, POINTER(RMAP_PACKET), c_char]
	dll_rmap.RMAP_CheckPacketValidIgnoreProtocol.restype = RMAP_STATUS

	errorCode = dll_rmap.RMAP_CheckPacketValidIgnoreProtocol(cRawPacketArrayPointer, c_ulong(rawPacketLength),
															 packetStructInternalPtr, c_char(checkPacketTooLong))

	# In case of success
	if errorCode == RMAP_STATUS.RMAP_SUCCESS:

		try:
			packetStruct = PopulateExternalRMAPStructure(packetStructInternal)
		except STARAPIError:
			raise
	else:
		packetStruct = None

	return errorCode, packetStruct

def RMAP_FreeBuffer(buffer):
	""" Frees a previously allocated buffer containing a packet created using
		the RMAP_Build* functions.

		Raises:\n
			STARAPIError:\n
				The RMAP packet library could not be loaded.\n
	"""

	# Protect against invalid RMAP packet library
	if dll_rmap is None:
		raise STARAPIError(RMAP_API_LIB_LOAD_ERROR_STR)

	# Set argument types and return type of the C function
	dll_rmap.RMAP_FreeBuffer.argtypes = [c_void_p]
	dll_rmap.RMAP_FreeBuffer.restype = None

	dll_rmap.RMAP_FreeBuffer(buffer)

def RMAP_GET_VERSION_EDIT(versionInfo) -> int:
	"""Returns the edit number from the specified version information.

	The version information can be obtained from a call to `STAR_system.rmap_packet_library.RMAP_GetVersion`,
	which returns a value with the edit number in bits 6 to 15.

	Args:\n
		versionInfo (int): The version info.

	Raises:\n
		TypeError:\n
			versionInfo must be an int.
	"""

	if type(versionInfo) != int:
		raise TypeError("versionInfo was not an int.")

	edit = ((versionInfo & 0x0000ffc0) >> 6)
	return edit

def RMAP_GET_VERSION_MAJOR(versionInfo) -> int:
	"""Returns the major version number from the specified version information.

	The version information can be obtained from a call to `STAR_system.rmap_packet_library.RMAP_GetVersion`, which
	returns a value with the major version number in the most significant 8 bits, bits 24 to 31.

	Args:\n
		versionInfo (int): The version info.

	Raises:\n
		TypeError:\n
			versionInfo must be an int.
	"""

	if type(versionInfo) != int:
		raise TypeError("versionInfo was not an int.")

	major = ((versionInfo & 0xff000000) >> 24)
	return major

def RMAP_GET_VERSION_MINOR(versionInfo) -> int:
	"""Returns the minor version number from the specified version information.

	The version information can be obtained from a call to `STAR_system.rmap_packet_library.RMAP_GetVersion`, which
	returns a value with the minor version number in bits 16 to 23.

	Args:\n
		versionInfo (int): The version info.

	Raises:\n
		TypeError:\n
			versionInfo must be an int.
	"""

	if type(versionInfo) != int:
		raise TypeError("versionInfo was not an int.")

	minor = ((versionInfo & 0x00ff0000) >> 16)
	return minor


def RMAP_GET_VERSION_PATCH(versionInfo) -> int:
	"""Returns the patch level from the specified version information.

	The version information can be obtained from a call to `STAR_system.rmap_packet_library.RMAP_GetVersion`, which
	returns a value with the patch level in bits 0 to 5.

	The patch level should be 0 in a release version of the RMAP Packet Library.

	Args:\n
		versionInfo (int): The version info.

	Raises:\n
		TypeError:\n
			versionInfo must be an int.
	"""

	if type(versionInfo) != int:
		raise TypeError("versionInfo was not an int.")

	patch = (versionInfo & 0x0000003f)
	return patch

def RMAP_CalculateCRC(bufferList) -> int:
	""" Calculates and returns an 8-bit CRC for the given buffer.

		Args:\n
			bufferList (list of ints): List containing the values to calculate the CRC for.

		Raises:\n
			STARAPIError:\n
				The RMAP packet library could not be loaded.\n

			TypeError:\n
				bufferList was not a list.\n
				at least one element in bufferList was not an int.\n

			ValueError:\n
				each element in bufferList must be between 0 and 255.\n
	"""

	# Protect against invalid RMAP packet library
	if dll_rmap is None:
		raise STARAPIError(RMAP_API_LIB_LOAD_ERROR_STR)

	if isinstance(bufferList, list) is False:
		raise TypeError("bufferList must be a list.")

	for bufferListByte in bufferList:
		if type(bufferListByte) != int:
			raise TypeError("each element in bufferList must be an int.")
		if bufferListByte < 0 or bufferListByte > 255:
			raise ValueError("each element in bufferList must be between 0 and 255.")

	# Get length of the buffer list
	bufferListLength = len(bufferList)

	# Create array for buffer list
	cBufferListArray = (c_uint8 * bufferListLength)()

	# Assign the buffer values
	for i in range(0, bufferListLength):
		cBufferListArray[i] = bufferList[i]

	# Cast to pointer type
	cBufferListArrayPointer = pointer(cBufferListArray)

	# Set argument types and return type of the C function
	dll_rmap.RMAP_CalculateCRC.argtypes = [c_void_p, c_ulong]
	dll_rmap.RMAP_CalculateCRC.restype = c_uint8

	crc = dll_rmap.RMAP_CalculateCRC(cBufferListArrayPointer, c_ulong(bufferListLength))

	return crc

def RMAP_CalculateCRCWithSeed(bufferList, crc) -> int:
	""" Calculates and returns an 8-bit CRC for the given buffer, starting from the given seed.

		Args:\n
			bufferList (list of ints): List containing the values to calculate the CRC for.
			crc (int): The seed CRC to be used when calculating the CRC.

		Raises:\n
			STARAPIError:\n
				The RMAP packet library could not be loaded.\n

			TypeError:\n
				bufferList was not a list.\n
				at least one element in bufferList was not an int.\n
				crc was not an int.\n

			ValueError:\n
				each element in bufferList must be between 0 and 255.\n
				crc must be between 0 and 255.\n
	"""

	# Protect against invalid RMAP packet library
	if dll_rmap is None:
		raise STARAPIError(RMAP_API_LIB_LOAD_ERROR_STR)

	if isinstance(bufferList, list) is False:
		raise TypeError("bufferList must be a list.")

	for bufferListByte in bufferList:
		if type(bufferListByte) != int:
			raise TypeError("each element in bufferList must be an int.")
		if bufferListByte < 0 or bufferListByte > 255:
			raise ValueError("each element in bufferList must be between 0 and 255.")

	if type(crc) != int:
		raise TypeError("crc must be an int.")

	if crc < 0 or crc > 255:
		raise ValueError("crc must be between 0 and 255.")

	# Get length of the buffer list
	bufferListLength = len(bufferList)

	# Create array for buffer list
	cBufferListArray = (c_uint8 * bufferListLength)()

	# Assign the buffer values
	for i in range(0, bufferListLength):
		cBufferListArray[i] = bufferList[i]

	# Cast to pointer type
	cBufferListArrayPointer = pointer(cBufferListArray)

	# Set argument types and return type of the C function
	dll_rmap.RMAP_CalculateCRCWithSeed.argtypes = [c_void_p, c_ulong, c_uint8]
	dll_rmap.RMAP_CalculateCRCWithSeed.restype = c_uint8

	newCrc = dll_rmap.RMAP_CalculateCRCWithSeed(cBufferListArrayPointer, c_ulong(bufferListLength), c_uint8(crc))

	return newCrc

def RMAP_GetVersion() -> int:
	""" Returns the current version information for the RMAP Packet Library.

		The most significant 8 bits will contain the major version number, the next
		significant 8 bits the minor version number, the next significant 10 bits the edit
		number, and the 6 least significant bits the patch level. In a release version of
		the library, the patch level should be 0.

		Raises:\n
			STARAPIError:\n
				The RMAP packet library could not be loaded.\n
	"""

	# Protect against invalid RMAP packet library
	if dll_rmap is None:
		raise STARAPIError(RMAP_API_LIB_LOAD_ERROR_STR)

	# Set argument types and return type of the C function
	dll_rmap.RMAP_GetVersion.argtypes = []
	dll_rmap.RMAP_GetVersion.restype = c_uint32

	version = dll_rmap.RMAP_GetVersion()

	return version

def RMAP_IsCRCValid(bufferList, crc) -> bool:
	""" Determines if the specified 8-bit CRC is valid for the given buffer.

		Returns True if the CRC is valid, False otherwise.

		Args:\n
			bufferList (list of ints): List containing the values to check the CRC against.
			crc (int): The CRC to be used when comparing the calculated CRC.

		Raises:\n
			STARAPIError:\n
				The RMAP packet library could not be loaded.\n
				RMAP_IsCRCValid returned incorrect value.\n

			TypeError:\n
				bufferList was not a list.\n
				at least one element in bufferList was not an int.\n
				crc was not an int.\n

			ValueError:\n
				each element in bufferList must be between 0 and 255.\n
				crc must be between 0 and 255.\n
	"""

	# Protect against invalid RMAP packet library
	if dll_rmap is None:
		raise STARAPIError(RMAP_API_LIB_LOAD_ERROR_STR)

	if isinstance(bufferList, list) is False:
		raise TypeError("bufferList must be a list.")

	for bufferListByte in bufferList:
		if type(bufferListByte) != int:
			raise TypeError("each element in bufferList must be an int.")
		if bufferListByte < 0 or bufferListByte > 255:
			raise ValueError("each element in bufferList must be between 0 and 255.")

	if type(crc) != int:
		raise TypeError("crc must be an int.")

	if crc < 0 or crc > 255:
		raise ValueError("crc must be between 0 and 255.")

	# Get length of the buffer list
	bufferListLength = len(bufferList)

	# Create array for buffer list
	cBufferListArray = (c_uint8 * bufferListLength)()

	# Assign the buffer values
	for i in range(0, bufferListLength):
		cBufferListArray[i] = bufferList[i]

	# Cast to pointer type
	cBufferListArrayPointer = pointer(cBufferListArray)

	# Set argument types and return type of the C function
	dll_rmap.RMAP_IsCRCValid.argtypes = [c_void_p, c_ulong, c_uint8]
	dll_rmap.RMAP_IsCRCValid.restype = c_char

	valid = dll_rmap.RMAP_IsCRCValid(cBufferListArrayPointer, c_ulong(bufferListLength), c_uint8(crc))

	# Check that 1 char value was returned
	if len(valid) != 1:
		raise STARAPIError("RMAP_IsCRCValid returned incorrect value.")

	# Convert this value to bool
	return bool(list(valid)[0])

