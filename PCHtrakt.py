import sys 

from pchRequest import *
from config import *
from time import sleep
from utilities import *
import getopt
import parser
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
	np = parser.NameParser(True)
	parse_result = np.parse('test - 1x06 - toto.mkv')
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
