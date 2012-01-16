# -*- coding: utf-8 -*-
# Authors: Jonathan Lauwers / Frederic Haumont
# URL: http://github.com/PCHtrakt/PCHtrakt
#
# This file is part of PCHtrakt.
#
# PCHtrakt is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PCHtrakt is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PCHtrakt.  If not, see <http://www.gnu.org/licenses/>.

# PCHtrakt - Connect your PCH 200 Series to trakt.tv :)
# PCHtrakt uses some pyhton lib :
#	- tvdb_api ()
#	- nbrhttpconnection ()
# 	- some classes from Sick Beard () 

import sys 
import pchtrakt
import getopt
from pch import *
from config import *
from time import sleep
from lib.utilities import *
from lib import tvdb_api 
from lib import parser
from lib import regexes
from datetime import date

pchtrakt.stop = 0
pchtrakt.currentPath = ''
pchtrakt.currentTime = 0
pchtrakt.watched = 0
tvdb = tvdb_api.Tvdb()
pchtrakt.DAEMON = 0

def printHelp():
	print 'Usage %s <other options>' % 'pchtrak.py'
	print ''
	print 'TODO'

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
			print '-d,--daemon launches pchtrakt in the background'
			sys.exit()

def main():
	oPchRequestor = PchRequestor()
	oStatus = oPchRequestor.getStatus(ipPch,5)
	if oStatus.status != EnumStatus.NOPLAY and oStatus.status != EnumStatus.UNKNOWN:
		oNameParser =  parser.NameParser()
		parsedInfo = oNameParser.parse(oStatus.fileName)
		Debug(u"PCH current status = [" + oStatus.status + "] - TV Show : " + parsedInfo.series_name + " - Season:" + str(parsedInfo.season_number) + " - Episode:" + str(parsedInfo.episode_numbers))
		try:
			episodeinfo = tvdb[parsedInfo.series_name][parsedInfo.season_number][parsedInfo.episode_numbers[0]] #TODO(achtus) Hardcoding 1st episode
		except:
			return
		Debug("TvShow ID on tvdb = " + str(tvdb[parsedInfo.series_name]['id']))
		Debug("FirstAired= " + str(tvdb[parsedInfo.series_name]['firstaired']))
		Debug("Episode ID on tvdb = " + str(episodeinfo['id']))
		videoStatusHandle(oStatus,str(episodeinfo['id']),str(tvdb[parsedInfo.series_name]['firstaired']).split('-')[0],parsedInfo)
	else:
		if pchtrakt.currentPath != '':
			videoStopped()
			pchtrakt.currentPath = ''
		Debug("PCH status = " + oStatus.status)

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
	if pchtrakt.currentPath != oStatus.fullPath:
		pchtrakt.currentPath = oStatus.fullPath
		if pchtrakt.currentPath != '':
			videoStarted(oStatus,id,year,parsedInfo)
		else:
			videoStopped()
	elif oStatus.percent > 90:
		if pchtrakt.watched == 0:
			pchtrakt.watched = 1
			videoIsEnding(oStatus,id,year,parsedInfo)
	elif oStatus.currentTime > pchtrakt.currentTime + refreshTime*60:
		pchtrakt.currentTime = oStatus.currentTime
		videoStillRunning(oStatus,id,year,parsedInfo)
		
def videoStarted(oStatus,id,year,parsedInfo):
	#add theTvDb ID
	watchingEpisodeOnTrakt(id,parsedInfo.series_name,year,str(parsedInfo.season_number),str(parsedInfo.episode_numbers[0]),str(oStatus.totalTime),str(oStatus.percent))
	Debug('Video playing!')
	

def videoStopped():
	cancelWatchingEpisodeOnTrakt()
	Debug('Video stopped!')

def videoStillRunning(oStatus,id,year,parsedInfo):
	videoStarted(oStatus,id,year,parsedInfo)
	Debug('Video still running!')

def videoIsEnding(oStatus,id,year,parsedInfo):
	scrobbleEpisodeOnTrakt(id,parsedInfo.series_name,year,str(parsedInfo.season_number),str(parsedInfo.episode_numbers[0]),str(oStatus.totalTime),str(oStatus.percent))
	#TODO(jlauwers) Create the .watched file if yamjpath is not empty?
	Debug('Video is ending')	
	
if __name__ == '__main__':
	getParams()
	if pchtrakt.DAEMON == True:
		daemonize()
	while not pchtrakt.stop:
		main()
		sleep(sleepTime)
