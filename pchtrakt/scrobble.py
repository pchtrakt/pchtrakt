from lib import utilities
from lib.utilities import Debug
import pchtrakt
from pchtrakt import mediaparser as mp
from pchtrakt.config import *
from time import sleep


def showStarted(myMedia):
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
    
def movieStarted(myMedia):
    responce = utilities.watchingMovieOnTrakt(myMedia.id,
                                               myMedia.parsedInfo.movie_title,
                                               myMedia.year,
                                               str(myMedia.oStatus.totalTime),
                                               str(myMedia.oStatus.percent))
    msg = 'Video playing: %s - %s' %(responce['status'],responce['message'])
    Debug(msg)
    pchtrakt.logger.info(msg)
    
    
def showStopped():
    responce = utilities.cancelWatchingEpisodeOnTrakt()
    msg = 'Video stopped: %s - %s' %(responce['status'],responce['message'])
    Debug(msg)
    pchtrakt.logger.info(msg)

    
def movieStopped():
    responce = utilities.cancelWatchingMovieOnTrakt()
    msg = 'Video stopped: %s - %s' %(responce['status'],responce['message'])
    Debug(msg)
    pchtrakt.logger.info(msg)
    
    
def videoStopped():
    if pchtrakt.isTvShow:
        showStopped()
    elif pchtrakt.isMovie:
        movieStopped()
    
    
def showStillRunning(myMedia):
    showStarted(myMedia)
    Debug('Video still running!')

    
def movieStillRunning(myMedia):
    movieStarted(myMedia)
    Debug('Video still running!')
    
    
def showIsEnding(myMedia):
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
    
    
def movieIsEnding(myMedia):
    responce = utilities.scrobbleMovieOnTrakt(myMedia.id,
                                               myMedia.parsedInfo.movie_title,
                                               myMedia.year,
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
            movieStarted(myMedia)
    if myMedia.oStatus.currentTime > pchtrakt.currentTime + int(refreshTime)*60:
        pchtrakt.currentTime = myMedia.oStatus.currentTime
        movieStillRunning(myMedia)        
    elif myMedia.oStatus.percent > 90:
        if not pchtrakt.watched:
            pchtrakt.watched = movieIsEnding(myMedia)
            
            
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
            if myMedia.oStatus.percent > 90:
                pchtrakt.watched  = 1
                Debug('Started at more than 90%! I''m not doing anything!')
            elif doubleEpisode:
                while myMedia.oStatus.percent > (myMedia.idxEpisode + 1) * 90.0/len(myMedia.parsedInfo.episode_numbers):
                    myMedia.idxEpisode += 1
                showStarted(myMedia)
                pchtrakt.currentTime = myMedia.oStatus.currentTime
            else:
                showStarted(myMedia)
    if not pchtrakt.watched:    
        if myMedia.oStatus.currentTime > pchtrakt.currentTime + int(refreshTime)*60:
            pchtrakt.currentTime = myMedia.oStatus.currentTime
            showStillRunning(myMedia)        
        elif doubleEpisode and myMedia.oStatus.percent > (myMedia.idxEpisode+1) * 90.0/len(myMedia.parsedInfo.episode_numbers) and myMedia.idxEpisode+1 < len(myMedia.parsedInfo.episode_numbers):
            showIsEnding(myMedia)
            myMedia.idxEpisode += 1
            showStarted(myMedia)
        elif myMedia.oStatus.percent > 90:
            if not pchtrakt.watched:
                if doubleEpisode:
                    pchtrakt.watched = showIsEnding(myMedia)
                else:
                     pchtrakt.watched = showIsEnding(myMedia)
    elif myMedia.oStatus.percent < 10:
        Debug('It seems you came back at the begining of the video... so I say to trakt it''s playing')
        pchtrakt.watched = 0
        showStarted(myMedia)

def videoStatusHandle(myMedia):
    if isinstance(myMedia.parsedInfo,mp.MediaParserResultTVShow):
        if scrobbleTvShow:
            videoStatusHandleTVSeries(myMedia)
        pchtrakt.isTvShow = 1
    elif isinstance(myMedia.parsedInfo,mp.MediaParserResultMovie):
        if scrobbleMovie:
            videoStatusHandleMovie(myMedia)
        pchtrakt.isMovie = 1
