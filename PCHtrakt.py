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
global stop
stop = 0

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
	oPchRequestor = PchRequestor(ipPch)
	oStatus = oPchRequestor.getPchStatus()	
	if oStatus.status != EnumStatus.NOPLAY:
		oParser = MediaParser()
		Debug(oParser.parseFileName(oStatus.fileName))
		Debug("PCH is : " + oStatus.status + " - [" + oStatus.fileName + "] | Watching=" + str(oStatus.currentTime) + " on " + str(oStatus.totalTime) + " (" + str(oStatus.percent) + "%)")
	else:
		Debug(oStatus.status)
	
	#watchingEpisodeOnTrakt(reqPch.theTvDb,reqPch.name,str(reqPch.year),reqPch.season,reqPch.episode,str(reqPch.totalTime),str(reqPch.percent))
	#cancelWatchingEpisodeOnTrakt()
	
while not stop:
	main()
	sleep(sleepTime)