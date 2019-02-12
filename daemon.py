#!/usr/bin/env python
"""Usage:	daemon.py [-d DB] [-l LVL]
	daemon.py -h
	daemon.py -v

Arguments:
  DB	Path to database file
  LVL  	Log level

Options:
  -h --help   		Show this screen
  -l --log LVL    	Specify log level [default: 10]
  -d --database DB    	Use the specified database [default: ../../db.sqlite3]
  -v --version    	Show version

"""
from docopt import docopt


if __name__ == '__main__':
	args = docopt(__doc__,version="Arduinopinic Daemon v0.01")
	print(args['--database'])
