#!/usr/bin/env python
# -*- coding: utf-8 -*
"""Usage:	daemon.py [--verbose] [-d DB] [-l LVL] [-f LOGFILE]
	daemon.py -h
	daemon.py -v

Arguments:
  DB		Path to database file
  LVL  		Log level
  LOGFILE	Path to log file

Options:
  -h --help   			Show this screen
  -l --log LVL    		Specify log level [default: 10]
  -f --logfile LOGFILE  	Use the specified log file [default: dd.log]
  -d --database DB    		Use the specified database [default: ../../db.sqlite3]
  -v --version    		Show version
  --verbose  			Verbose mode

"""
from docopt import docopt
import sys
import logging
import sqlite3
from terminaltables import AsciiTable
import arrow
import smbus2
import time

######### definition of objects ##################################
##################################################################

######### configuration
class Configuration:
        def __init__(self,liste,args):
                self.i2c = liste[1]
                self.delay = liste[2]
                self.lastmodified = liste[4]
		self.loglevel = args['--log']
		self.logfile = args['--logfile']
		self.timezone = liste[3]
		self.runtime = arrow.utcnow().to(self.timezone)
        def table(self):
                tab = []
                tab.append(['Parameters', 'Value'])
                tab.append(['i2c', self.i2c])
                tab.append(['delay', self.delay])
                tab.append(['last modified', self.lastmodified])
		tab.append(['log level', self.loglevel])
		tab.append(['timezone', self.timezone])
		tab.append(['log file', self.logfile])
                tab.append(['runtime', self.runtime.format('YYYY-MM-DD HH:mm:ss ZZ')])
                return tab

######### definition of functions ################################
##################################################################

######### function verbose
def verbose(msg):
	if args['--verbose'] == True:
		print msg

######### Program ################################################
##################################################################

if __name__ == '__main__':
	nloop = 0		#counting packet received
	ncrcok = 0		#counting packet received with crc ok
######### Retrieving arguments
	args = docopt(__doc__,version="Arduinopinic Daemon v0.01")
######### Init logging module
        try:
		logging.basicConfig(filename=args['--logfile'],level=int(args['--log']),
		format='%(asctime)s %(levelname)s : %(message)s')
        except Exception as error:
		print("Unable to init logging module...")
		sys.exit(1)
	else:
		logging.debug("Logging module initialised...")
		verbose("Logging module initialised...")
######### Opening database
	try:
		DBB = sqlite3.connect(args['--database'])
	except Exception as error:
		logging.critical("Unable to open database...")
		print("Unable to open database...")
		logging.critical(error)
		print(error)
		logging.shutdown()
                sys.exit(1)
        else:
                logging.debug("Database opened...")
		verbose("Database opened...")
######### Getting config
        try:
                cursor = DBB.cursor()
		cursor.execute("""SELECT * FROM Arduinopinic_config""")
		config_dbb = cursor.fetchone()
		config = Configuration(config_dbb,args)
        except Exception as error:
                logging.critical("Unable to get configuration from database...")
                print("Unable to get configuration from database...")
                logging.critical(error)
                print(error)
		logging.shutdown()
		DBB.close()
                sys.exit(1)
        else:
                logging.debug("Configuration retrieved...")
                verbose("Configuration retrieved...")
                logging.debug(AsciiTable(config.table()).table)
                verbose(AsciiTable(config.table()).table)
######### Opening i2c
        try:
                bus = smbus2.SMBus(1)
        except Exception as error:
                logging.critical("Unable to open i2c connection...")
                print("Unable to open i2c connection...")
                logging.critical(error)
                print(error)
                logging.shutdown()
                DBB.close()
                sys.exit(1)
        else:
                logging.debug("i2c connection opened...")
                verbose("i2c connection opened...")
		time.sleep(1) #Pause to treat opening (probably useless)

######### Main loop ##############################################
##################################################################
	while True:
		nloop = nloop + 1
		nattempt = 1
		verbose("########## PACKET N°%d#################" % nloop)
		logging.debug("########## PACKET N°%d#################" % nloop)
######## 5-attempt loop
		while  nattempt < 6:
			try:
				tx_msg=bus.read_i2c_block_data(config.i2c,0x01,9)
			except:
######## no i2c so retry loop
				if (nattempt ==5):
					logging.error("-Last attempt failed: going to next measure")
					verbose("-Last attempt failed: going to next measure")
					nattempt = nattempt + 1
					time.sleep(config.delay/10)
				else:
                                        logging.warning("-Attempt : %d - Not able to get I2C data" % nattempt)
                                        verbose("-Attempt : %d - Not able to get I2C data" % nattempt)
                                        nattempt = nattempt + 1
					time.sleep(config.delay/10)
				continue
######## if msg received - crc test
			verbose (tx_msg)
			
			nattempt = nattempt + 1
			time.sleep(config.delay) #delay divise par nombre d essai
			break
