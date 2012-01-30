from lib import utilities
from lib.utilities import Debug

def videoStarted(oStatus,id,year,parsedInfo,episode = 0):
    #add theTvDb ID
    responce = utilities.watchingEpisodeOnTrakt(id,parsedInfo.series_name,year,str(parsedInfo.season_number),str(parsedInfo.episode_numbers[episode]),str(oStatus.totalTime),str(oStatus.percent))
    Debug('Video playing: %s - %s' %(responce['status'],responce['message']))

def videoStopped():
    responce = utilities.cancelWatchingEpisodeOnTrakt()
    Debug('Video stopped: %s - %s' %(responce['status'],responce['message']))

def videoStillRunning(oStatus,id,year,parsedInfo,episode = 0):
    videoStarted(oStatus,id,year,parsedInfo,episode)
    Debug('Video still running!')

def videoIsEnding(oStatus,id,year,parsedInfo,episode = 0):
    responce = utilities.scrobbleEpisodeOnTrakt(id,parsedInfo.series_name,year,str(parsedInfo.season_number),str(parsedInfo.episode_numbers[episode]),str(oStatus.totalTime),str(oStatus.percent))
    if responce != None:
        Debug('Video is ending: %s - %s ' %(responce['status'],responce['message']))
        return 1
    return 0