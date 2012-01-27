from lib import utilities
from lib.utilities import Debug
import pchtrakt

def videoStarted(oStatus,id,year,parsedInfo,episode = 0):
	#add theTvDb ID
	responce = utilities.watchingEpisodeOnTrakt(id,parsedInfo.series_name,year,str(parsedInfo.season_number),str(parsedInfo.episode_numbers[episode]),str(oStatus.totalTime),str(oStatus.percent))
	msg = 'Video playing: %s - %s' %(responce['status'],responce['message'])
	Debug(msg)
	pchtrakt.logger.info(msg)

def videoStopped():
	responce = utilities.cancelWatchingEpisodeOnTrakt()
	msg = 'Video stopped: %s - %s' %(responce['status'],responce['message'])
	Debug(msg)
	pchtrakt.logger.info(msg)

def videoStillRunning(oStatus,id,year,parsedInfo,episode = 0):
	videoStarted(oStatus,id,year,parsedInfo,episode)
	Debug('Video still running!')

def videoIsEnding(oStatus,id,year,parsedInfo,episode = 0):
	responce = utilities.scrobbleEpisodeOnTrakt(id,parsedInfo.series_name,year,str(parsedInfo.season_number),str(parsedInfo.episode_numbers[episode]),str(oStatus.totalTime),str(oStatus.percent))
	if responce != None:
		msg = 'Video is ending: %s - %s ' %(responce['status'],responce['message'])
		Debug(msg)
		pchtrakt.logger.info(msg)
		return 1
	return 0