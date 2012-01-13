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

import sys 
from MediaParser import *
from pch import *
from config import *
from time import sleep
from utilities import *
import getopt
stop = 0
currentPath=''
currentTime=0
watched=0
try:
	opts, args = getopt.getopt(sys.argv[1:], "d::", ['']) #@UnusedVariable
except getopt.GetoptError:
	print "Available options: No option for now sry :P"
	sys.exit()
	
def printHelp():
	print 'Usage %s <other options>' % 'PCHtrak.py'
	print ''
	print 'TODO'

def main():
	global currentPath
	global currentTime
	global watched
	oPchRequestor = PchRequestor(ipPch)
	oStatus = oPchRequestor.getPchStatus()
	if currentPath != oStatus.fullPath:
		currentPath = oStatus.fullPath
		if currentPath != '':
			VideoStarted()
		else:
			VideoStopped()
	elif oStatus.percent > 90:
		if wacthed == 0:
			watched = 1
			VideoIsEnding()
	elif oStatus.currentTime > currentTime + refreshTime*60:
		currentTime = oStatus.currentTime
		VideoStillRunning()
	if oStatus.status != EnumStatus.NOPLAY:
		oParser = MediaParser()
		Debug(oParser.parseFileName(oStatus.fileName))
		Debug("PCH is : " + oStatus.status + " - [" + oStatus.fileName + "] | Watching=" + str(oStatus.currentTime) + " on " + str(oStatus.totalTime) + " (" + str(oStatus.percent) + "%)")
	else:
		Debug(oStatus.status)
		
		
def VideoStarted():
	Debug('Video started!')
	#watchingEpisodeOnTrakt(reqPch.theTvDb,reqPch.name,str(reqPch.year),reqPch.season,reqPch.episode,str(reqPch.totalTime),str(reqPch.percent))

def VideoStopped():
	cancelWatchingEpisodeOnTrakt()
	Debug('Video stopped!')

def VideoStillRunning():
	Debug('Video still running!')
	#watchingEpisodeOnTrakt(reqPch.theTvDb,reqPch.name,str(reqPch.year),reqPch.season,reqPch.episode,str(reqPch.totalTime),str(reqPch.percent))

def VideoIsEnding():
	Debug('Video is ending')
	#scrobbleEpisodeOnTrakt(tvdb_id, title, year, season, episode, duration, percent):
		
	
while not stop:
	main()
	sleep(sleepTime)
