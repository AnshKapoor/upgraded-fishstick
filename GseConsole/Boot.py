import os
import sys
import thread
import SpaceWire

from CCSDS import *

class Boot(object):
    def __init__(self, spw, soft_filename=''):
        self.soft_filename = soft_filename
        self.spw = spw
        self.app_data_max = 226
        
    def decode(self, message):

        if len(message) < 20:
            message += self.spw.spw_raw.receive()
            
        header = TmHeader(message[0:20])
       
        if(header.common.dfh.serviceType == 5):
            if(header.common.dfh.serviceSubtype == 1):
                eventMessage = TmBootEventMsg(message[0:60])
                
                self.spw.print_handler(eventMessage.event.msg + '\n')
                if(self.soft_filename != ''):
                    thread.start_new_thread(self.boot_into, (self.soft_filename,))
            elif(header.common.dfh.serviceSubtype == 4):
                self.spw.print_handler('Boot error message received', fmt='e')

        return message[header.common.id.packetLength+11:]
      
    def empty_packet(self):
        packet = TcPacket()
        packet.tcTransport.logicalAdd = 0x45
        packet.tcTransport.protocolId = 0x02
        packet.tcTransport.applicationId = 0x00

        packet.tcPacketHeader.version = 0
        packet.tcPacketHeader.packetType = 1
        packet.tcPacketHeader.dataFieldHeaderFlag = 1
        packet.tcPacketHeader.processId = 72
        packet.tcPacketHeader.packetCategory = 12
        
        packet.tcPacketHeader.sequenceFlags = 0x03
        packet.tcPacketHeader.sequenceCount = 0x00
        
        packet.tcPacketHeader.packetLength = 5

        packet.tcPacketDataField.tcDataFieldHeader.flagPusAck = 0x19
        packet.tcPacketDataField.tcDataFieldHeader.serviceType = 6
        packet.tcPacketDataField.tcDataFieldHeader.serviceSubtype = 2
        packet.tcPacketDataField.tcDataFieldHeader.sourceId = 120
        
        return packet
                
    def boot_into(self, filename_gse):
        self.upload_binary(filename_gse, 0x40000000)
        self.jump(0x40000000)
        
    def upload_binary(self, filename_gse, address):
  
        size = os.path.getsize(filename_gse)

        packet = self.empty_packet()
        
        packet.tcPacketDataField.appDataHeader.memoryId = 0xa069
        packet.tcPacketDataField.appDataHeader.startAddress = address
        packet.tcPacketDataField.appDataHeader.length = self.app_data_max

        file = open(filename_gse, 'rb')
        offset = 0
                
        n, last_part = divmod(size, self.app_data_max)

        self.spw.print_handler('Booting into: ' + filename_gse + '\n')
                
        for i in range(0, n, 1):

            packet.tcPacketDataField.appData = file.read(self.app_data_max)
            packet.tcPacketHeader.packetLength = self.app_data_max + 5 + 10
            packet.tcPacketHeader.sequenceCount = i
            packet.tcPacketDataField.calc_crc(str(packet.tcPacketHeader)+\
                                              str(packet.tcPacketDataField.tcDataFieldHeader)+\
                                              str(packet.tcPacketDataField.appDataHeader)+\
                                              str(packet.tcPacketDataField.appData))
            #print('.')
            self.spw.spw_raw.send(str(packet))
            #if i in range(0,3):
            #    for c in str(packet):
            #        print(str(hex(ord(c))))
            #    print(' ')
            packet.tcPacketDataField.appDataHeader.startAddress += self.app_data_max
            offset += self.app_data_max
                
        if last_part > 0:
            packet.tcPacketDataField.appDataHeader.length = last_part
            packet.tcPacketDataField.appData = file.read(last_part)
            packet.tcPacketHeader.sequenceCount = n
            packet.tcPacketDataField.calc_crc(str(packet.tcPacketHeader)+\
                                              str(packet.tcPacketDataField.tcDataFieldHeader)+\
                                              str(packet.tcPacketDataField.appDataHeader)+\
                                              str(packet.tcPacketDataField.appData))
            #print('.')
            self.spw.spw_raw.send(str(packet))
                
        file.close()

        
    def jump(self, address):
        packet = self.empty_packet()
        
        packet.tcPacketDataField.appDataHeader.memoryId = 0xa0cc
        packet.tcPacketDataField.appDataHeader.startAddress = address
        packet.tcPacketDataField.appDataHeader.length = 1
        packet.tcPacketDataField.calc_crc(str(packet.tcPacketHeader)+\
                                          str(packet.tcPacketDataField.tcDataFieldHeader)+\
                                          str(packet.tcPacketDataField.appDataHeader)+\
                                          str(packet.tcPacketDataField.appData))
        
        self.spw.spw_raw.send(str(packet))
        print('Jump')
    
