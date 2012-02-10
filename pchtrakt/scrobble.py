from lib import utilities
from lib.utilities import Debug
import pchtrakt
from pchtrakt import mediaparser as mp
from pchtrakt import betaseries as bs
from pchtrakt.config import *
from time import sleep
from pchtrakt.pch import EnumStatus

def showStarted(myMedia):
    if TraktScrobbleTvShow:
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
    if pchtrakt.isTvShow and TraktScrobbleTvShow:
        showStopped()
    elif pchtrakt.isMovie and TraktScrobbleMovie:
        movieStopped()
    
    
def showStillRunning(myMedia):
    showStarted(myMedia)
    
    
def movieStillRunning(myMedia):
    movieStarted(myMedia)
    
    
def showIsEnding(myMedia):
    result = 0
    if BetaSeriesScrobbleTvShow:
        serieXml = bs.getSerieUrl(myMedia.parsedInfo.series_name)
        Debug(serieXml)
        token = bs.getToken()
        Debug(token)
        isWatched = bs.isEpisodeWatched(serieXml,token,myMedia.parsedInfo.season_number
                                    ,myMedia.parsedInfo.episode_numbers[myMedia.idxEpisode])
        result = True
        if not isWatched:
            Debug('Adding show: {0}'.format(bs.addShow(serieXml,token)))
            result = 'BetaSerie Scrobble: {0}'.format(
                            bs.scrobbleEpisode(serieXml
                                                ,token,
                                                myMedia.parsedInfo.season_number,
                                                myMedia.parsedInfo.episode_numbers[myMedia.idxEpisode]))
            msg = '(BetaSeries) Video is ending'
            Debug(msg)
            pchtrakt.logger.info(msg)
            result = 1
            bs.destroyToken(token)
    
    if TraktScrobbleTvShow:
        responce = utilities.scrobbleEpisodeOnTrakt(myMedia.id,
                                                    myMedia.parsedInfo.series_name,
                                                    myMedia.year,
                                                    str(myMedia.parsedInfo.season_number),
                                                    str(myMedia.parsedInfo.episode_numbers[myMedia.idxEpisode]),
                                                    str(myMedia.oStatus.totalTime),
                                                    str(myMedia.oStatus.percent))
        if responce != None:
            msg = '(Trakt) Video is ending: %s - %s ' %(responce['status'],responce['message'])
            Debug(msg)
            pchtrakt.logger.info(msg)
            result = 1
            
    return result
    
    
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
        if myMedia.oStatus.currentTime > pchtrakt.currentTime + int(TraktRefreshTime)*60:
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
    elif myMedia.oStatus.percent < 10 and myMedia.oStatus.status != EnumStatus.STOP:
        Debug('It seems you came back at the begining of the video... so I say to trakt it''s playing')
        pchtrakt.watched = 0
        pchtrakt.currentTime = myMedia.oStatus.currentTime
        showStarted(myMedia)

def videoStatusHandle(myMedia):
    if isinstance(myMedia.parsedInfo,mp.MediaParserResultTVShow):
        if TraktScrobbleTvShow or BetaSeriesScrobbleTvShow:
            videoStatusHandleTVSeries(myMedia)
        pchtrakt.isTvShow = 1
    elif isinstance(myMedia.parsedInfo,mp.MediaParserResultMovie):
        if TraktScrobbleMovie:
            videoStatusHandleMovie(myMedia)
        pchtrakt.isMovie = 1
