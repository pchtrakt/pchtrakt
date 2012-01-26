#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Authors: Jonathan Lauwers / Frederic Haumont
# URL: http://github.com/pchtrakt/pchtrakt
#
# This file is part of pchtrakt.
#
# pchtrakt is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pchtrakt is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pchtrakt.  If not, see <http://www.gnu.org/licenses/>.

# pchtrakt - Connect your PCH 200 Series to trakt.tv :)
# pchtrakt uses some pyhton lib :
#	- tvdb_api (https://github.com/dbr/tvdb_api)
#	- nbrhttpconnection (another project)
# 	- some classes from Sick Beard (http://sickbeard.com/)

import sys 
import getopt
import pchtrakt
import os

from pch import *
from scrobble import *
from config import *
from local_config import *
from time import sleep
from lib.tvdb_api import tvdb_api 
from lib.tvdb_api import tvdb_exceptions
from lib import parser
from lib import regexes
from datetime import date

tvdb = tvdb_api.Tvdb()
MAXFD = 1024
pchtrakt.stop = 0
pchtrakt.currentPath = ''
pchtrakt.currentTime = 0
pchtrakt.watched = 0
pchtrakt.DAEMON = 0
pchtrakt.nbr = 0
pchtrakt.oPchRequestor = PchRequestor()
pchtrakt.oNameParser =  parser.NameParser()
pchtrakt.StopTrying = 0
pchtrakt.oStatus = 0

def printHelp():
	print 'Usage %s <options>' % 'pchtrak.py'
	print 'Options:'
	print '	-d,--daemon:	launches pchtrakt in the background'


def getParams():
	try:
		opts, args = getopt.getopt(sys.argv[1:], "dh", ['daemon','help']) #@UnusedVariable
	except getopt.GetoptError:
		print "Available options: -d, --daemon"
		sys.exit()

	for o, a in opts:
		# Run as a daemon
		if o in ('-d', '--daemon'):
			if sys.platform == 'win32':
				print "Daemonize not supported under Windows, starting normally"
			else:
				pchtrakt.DAEMON = True
		
		if o in ('-h', '--help'):
			printHelp()
			sys.exit()

def main():
	pchtrakt.oStatus = pchtrakt.oPchRequestor.getStatus(ipPch,5)
	if pchtrakt.currentPath != pchtrakt.oStatus.fullPath:
		pchtrakt.StopTrying = 0
	if not pchtrakt.StopTrying:
		if pchtrakt.oStatus.status != EnumStatus.NOPLAY and pchtrakt.oStatus.status != EnumStatus.UNKNOWN:
			if pchtrakt.oStatus.status != EnumStatus.LOAD:
				parsedInfo = pchtrakt.oNameParser.parse(pchtrakt.oStatus.fileName)
				if parsedInfo.season_number == None:
					raise BaseException('No season - maybe anime?')
				Debug('TV Show : %s - Season:%s - Episode:%s - %s%% - %s - TvDB: %s' 
					%(parsedInfo.series_name,parsedInfo.season_number,
					parsedInfo.episode_numbers,pchtrakt.oStatus.percent,
					pchtrakt.oStatus.status,tvdb[parsedInfo.series_name]['id']))
				#episodeinfo = tvdb[parsedInfo.series_name][parsedInfo.season_number][parsedInfo.episode_numbers[pchtrakt.nbr]] 
				videoStatusHandle(pchtrakt.oStatus,str(tvdb[parsedInfo.series_name]['id']),str(tvdb[parsedInfo.series_name]['firstaired']).split('-')[0],parsedInfo)
		else:
			if pchtrakt.currentPath != '':
				videoStopped()
				pchtrakt.watched = 0
				pchtrakt.currentPath = ''
			Debug("PCH status = " + pchtrakt.oStatus.status)

def daemonize():
	"""
	Fork off as a daemon
	"""

	# Make a non-session-leader child process
	try:
		pid = os.fork() #@UndefinedVariable - only available in UNIX
		if pid != 0:
			sys.exit(0)
	except OSError, e:
		raise RuntimeError("1st fork failed: %s [%d]" %
				   (e.strerror, e.errno))

	os.setsid() #@UndefinedVariable - only available in UNIX

	# Make sure I can read my own files and shut out others
	prev = os.umask(0)
	os.umask(prev and int('077', 8))

	# Make the child a session-leader by detaching from the terminal
	try:
		pid = os.fork() #@UndefinedVariable - only available in UNIX
		if pid != 0:
			sys.exit(0)
	except OSError, e:
		raise RuntimeError("2st fork failed: %s [%d]" %
					(e.strerror, e.errno))
	import resource	# Resource usage information.
	maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
	if (maxfd == resource.RLIM_INFINITY):
		maxfd = MAXFD

	# Iterate through and close all file descriptors.
	for fd in range(0, maxfd):
		try:
			os.close(fd)
		except OSError:	# ERROR, fd wasn't open to begin with (ignored)
			pass

		# Redirect the standard I/O file descriptors to the specified file.  Since
		# the daemon has no controlling terminal, most daemons redirect stdin,
		# stdout, and stderr to /dev/null.  This is done to prevent side-effects
		# from reads and writes to the standard I/O file descriptors.

		# This call to open is guaranteed to return the lowest file descriptor,
		# which will be 0 (stdin), since it was closed above.
	os.open('/dev/null', os.O_RDWR)	# standard input (0)

		# Duplicate standard input to standard output and standard error.
	os.dup2(0, 1)			# standard output (1)
	os.dup2(0, 2)			# standard error (2)

	
"""
these methods should be in another class
... but these are not the methods you are looking for :D
"""

def videoStatusHandle(oStatus,id,year,parsedInfo):
	if len(parsedInfo.episode_numbers)>1:
		doubleEpisode = 1
	else:
		doubleEpisode = 0
	if pchtrakt.currentPath != oStatus.fullPath:
		pchtrakt.watched = 0
		pchtrakt.currentPath = oStatus.fullPath
		pchtrakt.currentTime = oStatus.currentTime
		pchtrakt.nbr = 0
		if pchtrakt.currentPath != '':
			if doubleEpisode and oStatus.percent > 45:
				pchtrakt.nbr = pchtrakt.nbr + 1
				id2 = tvdb[parsedInfo.series_name][parsedInfo.season_number][parsedInfo.episode_numbers[pchtrakt.nbr]]['id']
				videoStarted(oStatus,id2,year,parsedInfo,pchtrakt.nbr)
			else:
				videoStarted(oStatus,id,year,parsedInfo)
		else:
			videoStopped()
	if oStatus.currentTime > pchtrakt.currentTime + refreshTime*60:
		pchtrakt.currentTime = oStatus.currentTime
		videoStillRunning(oStatus,id,year,parsedInfo,pchtrakt.nbr)		
	elif doubleEpisode and oStatus.percent > 90.0/len(parsedInfo.episode_numbers) and oStatus.percent > (pchtrakt.nbr+1) * 90.0/len(parsedInfo.episode_numbers):
		Debug(str(pchtrakt.nbr+1) + ' part of a multi-episode' )
		videoIsEnding(oStatus,id,year,parsedInfo,pchtrakt.nbr)
		Debug(str(parsedInfo.episode_numbers[pchtrakt.nbr]) + ' is finished')
		sleep(5)
		pchtrakt.nbr = pchtrakt.nbr + 1
		id2 = tvdb[parsedInfo.series_name][parsedInfo.season_number][parsedInfo.episode_numbers[pchtrakt.nbr]]['id']
		videoStarted(oStatus,id2,year,parsedInfo,pchtrakt.nbr)
		Debug(str(parsedInfo.episode_numbers[pchtrakt.nbr]) + ' is started')
	elif oStatus.percent > 90:
		if not pchtrakt.watched:
			if doubleEpisode:
				videoIsEnding(oStatus,id,year,parsedInfo,len(parsedInfo.episode_numbers)-1)
			else:
				 pchtrakt.watched = videoIsEnding(oStatus,id,year,parsedInfo)

def stopTrying():
	pchtrakt.StopTrying = 1
	pchtrakt.currentPath = pchtrakt.oStatus.fullPath
	

if __name__ == '__main__':
	getParams()
	if pchtrakt.DAEMON:
		daemonize()
	while not pchtrakt.stop:
		try:
			main()
			sleep(sleepTime)
		except (KeyboardInterrupt, SystemExit):
			print ':::Stopping pchtrakt:::'
			pchtrakt.stop = 1
		except parser.InvalidNameException:
			stopTrying()
			print ':::What is this movie? %s Stop trying:::' %(pchtrakt.currentPath)
		except tvdb_exceptions.tvdb_shownotfound:
			stopTrying()
			print ':::TheTvDB - Show not found %s :::' %(pchtrakt.currentPath)
		# except BaseException as e:
			# stopTrying()
			# print '::: %s :::' %(pchtrakt.currentPath)
			# print '::: %s :::' %(e)

