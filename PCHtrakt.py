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

import sys 
from mediaparser import *
from pch import *
from config import *
from time import sleep
from lib.utilities import *
import getopt

stop = 0
currentPath = ''
currentTime = 0
watched = 0

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
	oPchRequestor = PchRequestor()
	oStatus = oPchRequestor.getStatus(ipPch)
	if oStatus.status != EnumStatus.NOPLAY and oStatus.status != EnumStatus.UNKNOWN:
		oParser = MediaParser()
		parsedInfo = oParser.parseFileName(oStatus.fileName)
		Debug(parsedInfo)
		Debug("PCH is : " + oStatus.status + " - [" + oStatus.fileName 
			+ "] | Watching=" + str(oStatus.currentTime) + " on " 
			+ str(oStatus.totalTime) + " (" + str(oStatus.percent) + "%)")
		videoStatusHandle(oStatus,parsedInfo)
	else:
		Debug("PCH status = " + oStatus.status)
		
		
"""
these methods should be in another class
... but these are not the methods you are looking for :D
"""
def videoStatusHandle(oStatus,parsedInfo):
	#TODO(jlauwers) replace global by an object
	global watched
	global currentPath
	global currentTime
	if currentPath != oStatus.fullPath:
		currentPath = oStatus.fullPath
		if currentPath != '':
			videoStarted(oStatus,parsedInfo)
		else:
			videoStopped()
	elif oStatus.percent > 90:
		if watched == 0:
			watched = 1
			videoIsEnding(oStatus,parsedInfo)
	elif oStatus.currentTime > currentTime + refreshTime*60:
		currentTime = oStatus.currentTime
		videoStillRunning(oStatus,parsedInfo)
		
def videoStarted(oStatus,parsedInfo):
	#add theTvDb ID
	#watchingEpisodeOnTrakt(theTvDbId,name,year,season,episode,str(reqPch.totalTime),str(reqPch.percent))
	Debug('Video playing!')
	

def videoStopped():
	cancelWatchingEpisodeOnTrakt()
	Debug('Video stopped!')

def videoStillRunning(oStatus,parsedInfo):
	videoStarted(oStatus,parsedInfo)
	Debug('Video still running!')
	

def videoIsEnding(oStatus,parsedInfo):
	#scrobbleEpisodeOnTrakt(tvdb_id, title, year, season, episode, duration, percent):
	#TODO(jlauwers) Create the .watched file if yamjpath is not empty?
	Debug('Video is ending')
	
		
	
while not stop:
	main()
	sleep(sleepTime)
