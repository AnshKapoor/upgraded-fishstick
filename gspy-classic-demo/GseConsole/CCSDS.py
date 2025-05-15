import struct

class TcDataFieldHeader(object):
	__slots__ = ("flagPusAck", "serviceType", "serviceSubtype", "sourceId") 
	
	def __init__(self):
		self.flagPusAck = 0
		self.serviceType = 0
		self.serviceSubtype = 0
		self.sourceId = 0

	def __str__(self):
		result = struct.pack('>B', self.flagPusAck)
		result += struct.pack('>B', self.serviceType)
		result += struct.pack('>B', self.serviceSubtype)
		result += struct.pack('>B', self.sourceId)
		return result

############################
		
class TcPacketDataField(object):
	__slots__ = ("tcDataFieldHeader", "appDataHeader", "appData", "errorControl", "crc_polynomial") 
	
	def __init__(self):
		self.tcDataFieldHeader = TcDataFieldHeader()
                self.appDataHeader = TcAppDataHeader()
		self.appData = '\x00'
		self.errorControl = 0
                self.crc_polynomial = 0x1021

        def crc(self, crc_word, crc_byte):
                crc_word ^= crc_byte << 8
                for i in range(8):
                        if((crc_word & 0x8000) > 0):
                                crc_word = (crc_word << 1) ^ self.crc_polynomial
                        else:
                                crc_word = crc_word << 1

                return (crc_word & 0xffff)

        def calc_crc(self, data):
                self.errorControl = 0xffff
                #data = str(self.appDataHeader)
                #data += self.appData
                for s in data:
                        self.errorControl = self.crc(self.errorControl, ord(s))

	def __str__(self):
		result = str(self.tcDataFieldHeader)
                result += str(self.appDataHeader)
		result += self.appData
		result += struct.pack('>H', self.errorControl)
		return result        

###########################

class TcAppDataHeader(object):
	__slots__ = ("memoryId", "startAddress", "length") 
	
	def __init__(self):
		self.memoryId = 0
		self.startAddress = 0
		self.length = 0

	def __str__(self):
		result = struct.pack('>H', self.memoryId)
		result += struct.pack('>L', self.startAddress)
		result += struct.pack('>L', self.length)
		return result

###########################


class TcPacket(object):
	__slots__ = ("tcTransport", "tcPacketHeader", "tcPacketDataField") 
	def __init__(self):
                self.tcTransport = TmTransport()
		self.tcPacketHeader = TmId()
		self.tcPacketDataField = TcPacketDataField()

	def __str__(self):
                result = str(self.tcTransport)
		result += str(self.tcPacketHeader)
		result += str(self.tcPacketDataField)
		return result

###########################

class CCSDSInfo(object):
	__slots__ = ("length", "payloadCrc", "numberOfPackets", "numberOfPacketsSent") 
	
	def __init__(self):
		self.length = 0
		self.payloadCrc = 0
		self.numberOfPackets = 0
		self.numberOfPacketsSent = 0
		
	def __str__(self):
		result = struct.pack('>L', self.length)
		result += struct.pack('>H', self.payloadCrc)
		result += struct.pack('>H', self.numberOfPackets)
		result += struct.pack('>H', self.numberOfPacketsSent)
		return result

###########################
###########################

class TmTransport(object):
        def __init__(self, payload='\x00\x00\x00\x00'):
                self.logicalAdd = struct.unpack('>B', payload[0])[0]
                self.protocolId = struct.unpack('>B', payload[1])[0]
                self.applicationId = struct.unpack('>B', payload[3])[0]

        def __str__(self):
                result = struct.pack('>B', self.logicalAdd)
                result += struct.pack('>B', self.protocolId)
                result += '\x00' # reserved
                result += struct.pack('>B', self.applicationId)
                return result
                

class TmId(object):
        def __init__(self, payload='\x00\x00\x00\x00\x00\x00'):
                data = struct.unpack('>H', payload[0:2])[0]
                self.version = (data & (0x7 << 13)) >> 13
                self.packetType = (data & (0x1 << 12)) >> 12
                self.dataFieldHeaderFlag = (data & (0x1 << 11)) >> 11 
                self.processId = (data & (0x7f << 4)) >> 4
                self.packetCategory = data & 0x000f
                data = struct.unpack('>H', payload[2:4])[0]
                self.sequenceFlags = (data & (0x3 << 14)) >> 14
                self.sequenceCount = data & 0x3fff
                self.packetLength = struct.unpack('>H', payload[4:6])[0]

        def __str__(self):
                data = (self.version & 0x7) << 13
                data |= (self.packetType & 0x1) << 12
                data |= (self.dataFieldHeaderFlag & 0x1) << 11
                data |= (self.processId & 0x7f) << 4
                data |= (self.packetCategory & 0xf)
                result = struct.pack('>H', data)
                data = (self.sequenceFlags & 0x3) << 14
                data |= (self.sequenceCount & 0x3fff)
                result += struct.pack('>H', data)
                result += struct.pack('>H', self.packetLength)
                return result
        
class TmDataFileHeader(object):
        def __init__(self, payload):
                data = struct.unpack('>L', payload[0:4])[0]
                self.secondaryHeaderFlag = (data & (0x1 << 31)) >> 31
                self.pusVersion = (data & (0x7 << 28)) >> 28 
                self.ack = (data & (0xf << 24)) >> 24
                self.serviceType = (data & (0xff << 16)) >> 16
                self.serviceSubtype = (data & (0xff << 8)) >> 8
                self.routingId = data & 0xff

class TmTime(object):
        def __init__(self, payload):
                self.coarseTime = struct.unpack('>L', payload[0:4])[0]
                self.fineTime = struct.unpack('>H', payload[4:6])[0]

class TmCommon(object):
        def __init__(self, payload):
                self.id = TmId(payload[0:6])
                self.dfh = TmDataFileHeader(payload[6:10])

class TmHeader(object):
        def __init__(self, payload):
                self.transport = TmTransport(payload[0:4])
                self.common = TmCommon(payload[4:14])
                self.time = TmTime(payload[14:20])

class TmBootEvent(object):
        def __init__(self, payload):
                self.id = struct.unpack('>H', payload[0:2])[0]
                self.msg = payload[2:40]

class TmBootError(object):
        def __init__(self, payload):
                self.id = struct.unpack('>H', payload[0:2])[0]
                
class TmBootEventMsg(object):
        def __init__(self, payload):
                self.tmHead = TmHeader(payload[0:20])
                self.event = TmBootEvent(payload[20:60])

class TmBootErrorMsg(object):
        def __init__(self, payload):
                self.tmHead = TmHeader(payload[0:20])
                self.error = TmBootError(payload[20:22])
