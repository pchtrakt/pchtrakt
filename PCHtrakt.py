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

from pchRequest import *
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
	reqPch = PchRequest(ipPch)
	oStatus = reqPch.getPchStatus()	
	if oStatus.status != EnumStatus.NOPLAY:
		oStatus.fileName=oStatus.fileName.replace(" ",".")
		oStatus.fileName=oStatus.fileName.replace("-",".")
		Debug("PCH is : " + oStatus.status + " - [" + oStatus.fileName + "] | Watching=" + str(oStatus.currentTime) + " on " + str(oStatus.totalTime) + " (" + str(oStatus.percent) + "%)")
		p=re.compile('(?P<show>[\w\s.,_-]+?)\.[Ss]?(?P<season>[\d]{1,2})[XxEe]?(?P<episode>[\d]{2})')
		Debug(p.findall(oStatus.fileName))
		#Debug(reqPch.name + '-' + reqPch.SxE + '-' + reqPch.title)
	else:
		Debug(oStatus.status)
	

	#watchingEpisodeOnTrakt(reqPch.theTvDb,reqPch.name,str(reqPch.year),reqPch.season,reqPch.episode,str(reqPch.totalTime),str(reqPch.percent))
#cancelWatchingEpisodeOnTrakt()
	
while not stop:
	main()
	sleep(sleepTime)
