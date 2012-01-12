import sys 

from pchRequest import *
from config import *
from time import sleep
from utilities import Debug
import getopt
global stop
stop = 0

try:
	opts, args = getopt.getopt(sys.argv[1:], "qfdp::", ['']) #@UnusedVariable
except getopt.GetoptError:
	print "Available options: No option for now sry :P"
	sys.exit()
	
def printHelp():
	print 'Usage %s <other options>' % 'PCHtrak.py'
	print ''
	print 'TODO'

def popRequest():
	reqPch = PchRequest(ipPch)
	if reqPch.status != EnumStatus.NOPLAY:
		Debug(reqPch.name + '-' + reqPch.SxE + '-' + reqPch.title)
	else:
		Debug(reqPch.status)
	

	#watchingEpisodeOnTrakt(reqPch.theTvDb,reqPch.name,str(reqPch.year),reqPch.season,reqPch.episode,str(reqPch.totalTime),str(reqPch.percent))
#cancelWatchingEpisodeOnTrakt()
	
while not stop:
	popRequest()
	sleep(5)