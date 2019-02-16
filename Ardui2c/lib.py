import crcmod.predefined
import struct
import arrow

class RX_msg:
    def __init__(self,tx_msg):
        self.raw = tx_msg
        self.length = self.raw[0]
        self.msg = self.raw[:-2]
        self.temp = float(self._get_int(self.msg[1:3]))/100
        self.humid = float(self._get_int(self.msg[3:5]))/100
        self.water = float(self._get_int(self.msg[5:7]))/100
	self.date = arrow.utcnow().format()
#######Recomposing hex in self.rxcrc
        if len(hex(self.raw[-2:-1][0])[2:])==1:
            self.rxcrc = '0' + hex(self.raw[-2:-1][0])[2:]
        else:
            self.rxcrc = hex(self.raw[-2:-1][0])[2:]
        if len(hex(self.raw[-1:][0])[2:])==1:
            self.rxcrc = '0' + hex(self.raw[-1:][0])[2:] + self.rxcrc
        else:
            self.rxcrc = hex(self.raw[-1:][0])[2:] + self.rxcrc
        self.rxcrc = "0x" + self.rxcrc
######calculate crc
        crc = crcmod.predefined.Crc('xmodem')
        nb = 0
        while nb < (len(self.msg)):     #minus 2 to avoid taking into account CRC bytes
            crc.update(chr(self.msg[nb]))
            nb=nb+1
        self.localcrc = hex(crc.crcValue)
######
    def _get_int(self,data):
        return struct.unpack('h', "".join(map(chr, data)))[0]
    def isvalid(self):
        return self.localcrc==self.rxcrc
