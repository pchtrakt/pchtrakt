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
from pch import *
from config import *
from time import sleep
from lib.utilities import *
import getopt
from lib import tvdb_api 
from lib import parser
from lib import regexes
from datetime import date
stop = 0
currentPath = ''
currentTime = 0
watched = 0
tvdb = tvdb_api.Tvdb()

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
	oPchRequestor = PchRequestor()
	oStatus = oPchRequestor.getStatus(ipPch,5)
	if oStatus.status != EnumStatus.NOPLAY and oStatus.status != EnumStatus.UNKNOWN:
		oNameParser =  parser.NameParser()
		parsedInfo = oNameParser.parse(oStatus.fileName)
		Debug(u"PCH current status = [" + oStatus.status + "] - TV Show : " + parsedInfo.series_name + " - Season:" + str(parsedInfo.season_number) + " - Episode:" + str(parsedInfo.episode_numbers)	)
		#Debug("PCH is : " + oStatus.status + " - [" + oStatus.fileName 
		#	+ "] | Watching=" + str(oStatus.currentTime) + " on " 
		#	+ str(oStatus.totalTime) + " (" + str(oStatus.percent) + "%)")
		episodeinfo = tvdb[parsedInfo.series_name][parsedInfo.season_number][parsedInfo.episode_numbers[0]] #TODO(achtus) Hardcoding 1st episode
		Debug("TvShow ID on tvdb = " + str(tvdb[parsedInfo.series_name]['id']))
		Debug("FirstAired= " + str(tvdb[parsedInfo.series_name]['firstaired']))
		Debug("Episode ID on tvdb = " + str(episodeinfo['id']))
		videoStatusHandle(oStatus,str(episodeinfo['id']),str(tvdb[parsedInfo.series_name]['firstaired']).split('-')[0],parsedInfo)
	else:
		if currentPath != '':
			videoStopped()
			currentPath = ''
		Debug("PCH status = " + oStatus.status)
		
		
"""
these methods should be in another class
... but these are not the methods you are looking for :D
"""
def videoStatusHandle(oStatus,id,year,parsedInfo):
	#TODO(jlauwers) replace global by an object
	global watched
	global currentPath
	global currentTime
	if currentPath != oStatus.fullPath:
		currentPath = oStatus.fullPath
		if currentPath != '':
			videoStarted(oStatus,id,year,parsedInfo)
		else:
			videoStopped()
	elif oStatus.percent > 90:
		if watched == 0:
			watched = 1
			videoIsEnding(oStatus,id,year,parsedInfo)
	elif oStatus.currentTime > currentTime + refreshTime*60:
		currentTime = oStatus.currentTime
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
	while not stop:
		main()
		sleep(sleepTime)
