import os
import struct

import crcmod.predefined
import arrow

class RX_msg:
	def __init__(self,tx_packet):
		self.raw = tx_packet
		self.length = self.raw[0]
		self.msg = self.raw[:-2]
		self.temp = float(self._get_int(self.msg[1:3]))/100
		self.humid = float(self._get_int(self.msg[5:7]))/100
		self.water = float(self._get_int(self.msg[3:5]))/100
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
		crc.update(bytearray(self.msg))
		self.localcrc = hex(crc.crcValue)
		if len(self.localcrc[2:]) == 3:
			self.localcrc = "0x0" + self.localcrc[2:]
######
	def _get_int(self,data):
		return struct.unpack('h', bytearray(data))[0]
	def isvalid(self):
		return self.localcrc==self.rxcrc
	def debug(self):
		return "\t%s    ||    RXCRC : %s | LOCCRC : %s" % (self.raw,self.rxcrc,self.localcrc)
	def info(self):
		return "temp ext: %.2f | temp eau: %.2f | humid: %.2f" % (self.temp,self.water,self.humid)

class Configuration:
		def __init__(self,liste,args):
			self.i2c = liste[1]
			self.delay = float(liste[2])
			self.lastmodified = liste[4]
			self.loglevel = args['--log']
			self.logfile = args['--logfile']
			self.timezone = liste[3]
		def table(self):
			tab = []
			tab.append(['Parameters', 'Value'])
			tab.append(['i2c', self.i2c])
			tab.append(['delay', self.delay])
			tab.append(['last modified', self.lastmodified])
			tab.append(['log level', self.loglevel])
			tab.append(['timezone', self.timezone])
			tab.append(['log file', self.logfile])
			return tab

class Session:
	def __init__(self):
		self.pid = os.getpid()
		self.path = os.path.abspath(__file__)
		self.runtime = arrow.utcnow()
		self.success = 0
		self.attempts = 0
		self.loop = 0
		self.id = 0
