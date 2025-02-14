import sys
import struct
import rmap_crc8

# Todo: RMAP read/modify/write

class Rmap():

    def __init__(self, spw_raw, dest, reply, dest_key=0x00, prot_id=0x01):
        self.spw_raw = spw_raw
        self.dest = dest
        self.reply = reply
        self.dest_key = dest_key
        self.prot_id = prot_id

    def rmap_header(self, rmap_cmd):
        header = struct.pack('>B', self.dest)  # destination
        header += struct.pack('>B', self.prot_id) # protocol id
        header += struct.pack('>B', rmap_cmd) # write
        header += struct.pack('>B', self.dest_key) # destination key
        header += '\x00\x00\x00'
        header += struct.pack('>B', self.reply) # reply address
        header += struct.pack('>B', self.reply) # initiator logical addr.
        header += '\x00\x00' # transaction id
        header += '\x00' # external address

        return header
        
    def rmap_write(self, addr, sdata):
        length = len(sdata)
        header = self.rmap_header(0x71)
        
        header += struct.pack('>I', addr) # rmap address
        header += struct.pack('>I', length & 0xffffff)[1:] # length
        
        hash = rmap_crc8.crc8()
        hash.update(header)
        header += hash.digest() # crc
        
        payload = header
        payload += sdata
        
        hash_data = rmap_crc8.crc8()
        hash_data.update(sdata)
        payload += hash_data.digest()
        
        self.spw_raw.send(payload)
                
    def rmap_read(self, addr, length):
        header = self.rmap_header(0x4d)
        header += struct.pack('>I', addr) # rmap address
        header += struct.pack('>I', length & 0xffffff)[1:] # length
        
        hash = rmap_crc8.crc8()
        hash.update(header)
        header += hash.digest() # crc

        self.spw_raw.lock.acquire()
        self.spw_raw.send(header)
        
        data = self.spw_raw.receive()
        self.spw_raw.lock.release()
        
        hash_data = rmap_crc8.crc8()
        hash_data.update(data[13:-1])
        
        if(hash_data.digest() == data[-1]):
            return data[13:-1]
        else:
            return ''

    def rmap_rmw(self, addr, sdata, mask):
        length = len(sdata)
        header = self.rmap_header(0x5d)
        
        header += struct.pack('>I', addr) # rmap address
        header += struct.pack('>I', length & 0xffffff)[1:] # length
        
        hash = rmap_crc8.crc8()
        hash.update(header)
        header += hash.digest() # crc
        
        payload = header
        payload += sdata
        payload += mask
        
        hash_data = rmap_crc8.crc8()
        hash_data.update(sdata)
        payload += hash_data.digest()
        
        self.spw_raw.send(payload)
        
       

                        
