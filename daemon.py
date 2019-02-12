#!/usr/bin/env python
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

######### function verbose
def verbose(msg):
	if args['--verbose'] == True:
		print msg


if __name__ == '__main__':
######### Retrieving arguments
	args = docopt(__doc__,version="Arduinopinic Daemon v0.01")
	print(args)
######### Init logging module
        try:
		logging.basicConfig(filename=args['--logfile'],level=int(args['--log']),
		format='%(asctime)s %(levelname)s : %(message)s')
        except Exception as error:
		print("Unable to init logging module...")
		sys.exit(1)
	else:
		logging.debug("Logging module initialised...")
######### Opening database
	try:
		DBB = sqlite3.connect(args['--database'])
	except Exception as error:
		logging.critical("Unable to open database...")
		print("Unable to open database...")
		logging.critical(error)
		print(error)
                sys.exit(1)
######### Getting config
        try:
                cursor = DBB.cursor()
		cursor.execute("""SELECT * FROM config""")
        except Exception as error:
                logging.critical("Unable to get configuration from database...")
                print("Unable to get configuration from database...")
                logging.critical(error)
                print(error)
                sys.exit(1)


