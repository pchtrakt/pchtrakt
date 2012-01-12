from pchRequest import *
from config import *
from time import sleep
from utilities import Debug
"""
from urllib import urlopen
from hashlib import sha1
from utilities import *
"""

def popRequest():
	reqPch = PchRequest(ipPch)
	if reqPch.status != EnumStatus.NOPLAY:
		Debug(reqPch.name + '-' + reqPch.SxE + '-' + reqPch.title)
	else:
		Debug(reqPch.status)
	

	#watchingEpisodeOnTrakt(reqPch.theTvDb,reqPch.name,str(reqPch.year),reqPch.season,reqPch.episode,str(reqPch.totalTime),str(reqPch.percent))
#cancelWatchingEpisodeOnTrakt()
	
while True:
	popRequest()
	sleep(5)