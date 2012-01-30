from lib import utilities
from lib.utilities import Debug
import pchtrakt
from pchtrakt import mediaparser as mp
from pchtrakt.config import *


def videoStarted(myMedia):
    responce = utilities.watchingEpisodeOnTrakt(myMedia.id,
                                                myMedia.parsedInfo.series_name,
                                                myMedia.year,
                                                str(myMedia.parsedInfo.season_number),
                                                str(myMedia.parsedInfo.episode_numbers[myMedia.idxEpisode]),
                                                str(myMedia.oStatus.totalTime),
                                                str(myMedia.oStatus.percent))
    msg = 'Video playing: %s - %s' %(responce['status'],responce['message'])
    Debug(msg)
    pchtrakt.logger.info(msg)

def videoStopped():
    responce = utilities.cancelWatchingEpisodeOnTrakt()
    msg = 'Video stopped: %s - %s' %(responce['status'],responce['message'])
    Debug(msg)
    pchtrakt.logger.info(msg)

def videoStillRunning(myMedia):
    videoStarted(myMedia)
    Debug('Video still running!')

def videoIsEnding(myMedia):
    responce = utilities.scrobbleEpisodeOnTrakt(myMedia.id,
                                                myMedia.parsedInfo.series_name,
                                                myMedia.year,
                                                str(myMedia.parsedInfo.season_number),
                                                str(myMedia.parsedInfo.episode_numbers[myMedia.idxEpisode]),
                                                str(myMedia.oStatus.totalTime),
                                                str(myMedia.oStatus.percent))
    if responce != None:
        msg = 'Video is ending: %s - %s ' %(responce['status'],responce['message'])
        Debug(msg)
        pchtrakt.logger.info(msg)
        return 1
    return 0

    
def videoStatusHandleMovie(myMedia):
    if pchtrakt.lastPath != myMedia.oStatus.fullPath:
        pchtrakt.watched = 0
        pchtrakt.lastPath = myMedia.oStatus.fullPath
        pchtrakt.currentTime = myMedia.oStatus.currentTime
        if pchtrakt.lastPath != '':
            videoStarted(myMedia)
    if myMedia.oStatus.currentTime > pchtrakt.currentTime + refreshTime*60:
        pchtrakt.currentTime = myMedia.oStatus.currentTime
        # videoStillRunning(myMedia)        
    elif myMedia.oStatus.percent > 90:
        if not pchtrakt.watched:
            pass
            # pchtrakt.watched = videoIsEnding(myMedia)
            
            
def videoStatusHandleTVSeries(myMedia):
    if len(myMedia.parsedInfo.episode_numbers)>1:
            doubleEpisode = 1
    else:
        doubleEpisode = 0
    if pchtrakt.lastPath != myMedia.oStatus.fullPath:
        pchtrakt.watched = 0
        pchtrakt.lastPath = myMedia.oStatus.fullPath
        pchtrakt.currentTime = myMedia.oStatus.currentTime
        myMedia.idxEpisode = 0
        if pchtrakt.lastPath != '':
            if doubleEpisode:
                while myMedia.oStatus.percent > (myMedia.idxEpisode + 1) * 90.0/len(myMedia.parsedInfo.episode_numbers):
                    myMedia.idxEpisode += 1
                videoStarted(myMedia)
                pchtrakt.currentTime = myMedia.oStatus.currentTime
            else:
                videoStarted(myMedia)
                
    if myMedia.oStatus.currentTime > pchtrakt.currentTime + refreshTime*60:
        pchtrakt.currentTime = myMedia.oStatus.currentTime
        videoStillRunning(myMedia)        
    elif doubleEpisode and myMedia.oStatus.percent > (myMedia.idxEpisode+1) * 90.0/len(myMedia.parsedInfo.episode_numbers) and myMedia.idxEpisode+1 < len(myMedia.parsedInfo.episode_numbers):
        videoIsEnding(myMedia)
        sleep(5)
        myMedia.idxEpisode += 1
        videoStarted(myMedia)
    elif myMedia.oStatus.percent > 90:
        if not pchtrakt.watched:
            if doubleEpisode:
                pchtrakt.watched = videoIsEnding(myMedia)
            else:
                 pchtrakt.watched = videoIsEnding(myMedia)

def videoStatusHandle(myMedia):
    if isinstance(myMedia.parsedInfo,mp.MediaParserResultTVShow):
        videoStatusHandleTVSeries(myMedia)
    elif isinstance(myMedia.parsedInfo,mp.MediaParserResultMovie):
        videoStatusHandleMovie(myMedia)
