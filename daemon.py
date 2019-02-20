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
  -f --logfile LOGFILE  	Use the specified log file [default: log/daemon.log]
  -d --database DB    		Use the specified database [default: ../../db.sqlite3]
  -v --version    		Show version
  --verbose  			Verbose mode

"""
import os
import sys
import logging
import sqlite3
import time

from docopt import docopt
from terminaltables import AsciiTable
import arrow
import smbus2

from Ardui2c.lib  import RX_msg, Configuration, Session

######### definition of functions ################################
##################################################################

######### function verbose
def verbose(msg):
	if args['--verbose'] == True:
		print msg

######### Program ################################################
##################################################################

if __name__ == '__main__':
	attempt = 0
######### Retrieving arguments
	args = docopt(__doc__,version="Arduinopinic Daemon v0.01")
######### Init logging module
        try:
		logging.basicConfig(filename=args['--logfile'],level=int(args['--log']),
		format='%(asctime)s %(levelname)s : %(message)s')
        except Exception as error:
		print("Unable to init logging module...")
		print(error)
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
######### Writing session info
        session = Session()
	cursor.execute('''INSERT INTO Arduinopinic_session(pid, path, runtime, lastmodified, success, loop, attempts)
                         VALUES(?,?,?,?,?,?,?)''', (session.pid,session.path,session.runtime.format(),session.runtime.format(),session.success,session.loop,session.attempts))
	session.id = cursor.lastrowid
	DBB.commit()

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
		cursor.execute('''UPDATE Arduinopinic_session SET success = ?,loop = ?,attempts = ? WHERE id = ?''',
 (session.success,session.loop,session.attempts,session.id))
		DBB.commit()

		session.loop += 1
		nattempt = 1
######## 5-attempt loop
		while  nattempt < 6:
			try:
				session.attempts += 1
				tx_msg = RX_msg(bus.read_i2c_block_data(config.i2c,0x01,9))
			except:
######## no i2c so retry loop
				if (nattempt ==5):
					logging.error("%d/%d ERROR: Last attempt - i2c failed - Waiting for next measure" % (session.loop,nattempt))
					verbose("%d/%d ERROR: Last attempt - i2c failed - Waiting for next measure" % (session.loop,nattempt))
					nattempt += 1
					time.sleep(config.delay-((nattempt-1)*config.delay/10))
				else:
                                        logging.warning("%d/%d FAILURE: Not able to get I2C data" % (session.loop,nattempt))
                                        verbose("%d/%d FAILURE: Not able to get I2C data" % (session.loop,nattempt))
                                        nattempt += 1
					time.sleep(config.delay/10)
				continue
######## if msg received - crc test
			if tx_msg.isvalid():
######## crc is ok
				session.success += 1
                                verbose("%d/%d SUCCESS: %s | success rate: %.2f" % (session.loop,nattempt,tx_msg.info(),float(session.success)/session.attempts*100))
				verbose(tx_msg.debug())
				logging.info("%d/%d SUCCESS: %s | success rate: %.2f" % (session.loop,nattempt,tx_msg.info(),float(session.success)/session.attempts*100))
				logging.debug(tx_msg.debug())
				cursor.execute('''INSERT INTO Arduinopinic_temp_db(date, tempext, tempeau, humid)
 	                 VALUES(?,?,?,?)''', (tx_msg.date,tx_msg.temp,tx_msg.water,tx_msg.humid))
				DBB.commit()

				time.sleep(config.delay-((nattempt-1)*config.delay/10))
				break
######## crc not ok
			else:
				if (nattempt ==5):
                                        verbose("%d/%d ERROR: Measure failed: %s | success rate: %.2f" % (session.loop,nattempt,tx_msg.info(),float(session.success)/session.attempts*100))
					verbose(tx_msg.debug())
					logging.error("%d/%d ERROR: Measure failed: %s | success rate: %.2f" % (session.loop,nattempt,tx_msg.info(),float(session.success)/session.attempts*100))
					logging.error(tx_msg.debug())
                                        nattempt += 1
                                        time.sleep(config.delay-((nattempt-1)*config.delay/10))
				else:
					verbose("%d/%d FAILURE: %s | success rate: %.2f" % (session.loop,nattempt,tx_msg.info(),float(session.success)/session.attempts*100))
					verbose(tx_msg.debug())
                	                logging.warning("%d/%d FAILURE: %s | success rate: %.2f" % (session.loop,nattempt,tx_msg.info(),float(session.success)/session.attempts*100))
                        	        logging.warning(tx_msg.debug())
					nattempt += 1
					time.sleep(config.delay/10)
				continue
