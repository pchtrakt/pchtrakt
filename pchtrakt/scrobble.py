from os.path import isfile
from os import listdir
from xml.etree import ElementTree

from lib import utilities
from lib.utilities import Debug
import pchtrakt
from pchtrakt.exception import BetaSerieAuthenticationException
from pchtrakt import mediaparser as mp
from pchtrakt import betaseries as bs
from pchtrakt.config import *
from time import sleep
from pchtrakt.pch import EnumStatus


class EnumScrobbleResult:
    KO = 0
    TRAKTOK = 1
    BETASERIESOK= 2

def showStarted(myMedia):
    if TraktScrobbleTvShow:
        responce = utilities.watchingEpisodeOnTrakt(myMedia.id,
                                                    myMedia.parsedInfo.name,
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
                                               myMedia.parsedInfo.name,
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
    try:
        if BetaSeriesScrobbleTvShow:
            result = 0
            serieXml = bs.getSerieUrl(myMedia.parsedInfo.name)
            token = bs.getToken()
            isWatched = bs.isEpisodeWatched(serieXml,token,myMedia.parsedInfo.season_number
                                        ,myMedia.parsedInfo.episode_numbers[myMedia.idxEpisode])      
            if not isWatched:
                result = bs.scrobbleEpisode(serieXml
                                                    ,token,
                                                    myMedia.parsedInfo.season_number,
                                                    myMedia.parsedInfo.episode_numbers[myMedia.idxEpisode])
                bs.destroyToken(token)
                
            if result or isWatched:
                msg = '(BetaSeries) Video is ending :  ' \
                       '{0} {1}x{2}'.format(myMedia.parsedInfo.name,
                                           myMedia.parsedInfo.season_number,
                                           myMedia.parsedInfo.episode_numbers[myMedia.idxEpisode]
                                           )
                Debug(msg)
                pchtrakt.logger.info(msg)
                myMedia.ScrobResult |=  EnumScrobbleResult.BETASERIESOK
        else:
            myMedia.ScrobResult |= EnumScrobbleResult.BETASERIESOK
    except BetaSerieAuthenticationException as e:
        Debug(e)
        pchtrakt.logger.info(e)
    except Exception as e:
        Debug(e)
        pchtrakt.logger.info(e)
    
    if TraktScrobbleTvShow:
        result = 0
        responce = utilities.scrobbleEpisodeOnTrakt(myMedia.id,
                                                    myMedia.parsedInfo.name,
                                                    myMedia.year,
                                                    str(myMedia.parsedInfo.season_number),
                                                    str(myMedia.parsedInfo.episode_numbers[myMedia.idxEpisode]),
                                                    str(myMedia.oStatus.totalTime),
                                                    str(myMedia.oStatus.percent))
        if responce:
            msg = '(Trakt) Video is ending: %s - %s ' %(responce['status'],responce['message'])
            Debug(msg)
            pchtrakt.logger.info(msg)
            result = 1
        
        if result == 1:
            myMedia.ScrobResult |= EnumScrobbleResult.TRAKTOK
    else:  
        myMedia.ScrobResult |= EnumScrobbleResult.TRAKTOK
    return myMedia.ScrobResult == EnumScrobbleResult.TRAKTOK | EnumScrobbleResult.BETASERIESOK
    
    
def movieIsEnding(myMedia):
    responce = utilities.scrobbleMovieOnTrakt(myMedia.id,
                                               myMedia.parsedInfo.name,
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
    if myMedia.oStatus.currentTime > pchtrakt.currentTime + int(TraktRefreshTime)*60:
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
    ignored = False
    if ignored_repertory[0] != '':
        for el in myMedia.oStatus.fullPath.split('/'):
            if el <> '' and el in ignored_repertory:
                msg = 'This video is in a ignored repertory: {0}'.format(el)
                ignored = 1
                break

    if ignored == 0 and YamjIgnoredCategory[0] != '':
        files = listdir(YamjPath)
        for file in files:
            if file.endswith('xml'):
                file = unicode(file, errors='replace')
                if file.find(myMedia.parsedInfo.name) >= 0:
                    oXml = ElementTree.parse(YamjPath + file)
                    genres = oXml.findall('.//genre')
                    for genre in genres:
                        if genre.text.lower() in YamjIgnoredCategory:
                            msg = 'This video is in a ignored category: {0}'.format(genre.text)
                            ignored = 1
                            break
                    if ignored == 1:
                        break
   
    if not ignored:
        if isinstance(myMedia.parsedInfo,mp.MediaParserResultTVShow):
            if TraktScrobbleTvShow or BetaSeriesScrobbleTvShow:
                videoStatusHandleTVSeries(myMedia)
            pchtrakt.isTvShow = 1
        elif isinstance(myMedia.parsedInfo,mp.MediaParserResultMovie):
            if TraktScrobbleMovie:
                videoStatusHandleMovie(myMedia)
            pchtrakt.isMovie = 1
    else:
        msg += ' - {0} {1}x{2}'.format(myMedia.parsedInfo.name,
                                           myMedia.parsedInfo.season_number,
                                           myMedia.parsedInfo.episode_numbers[0]
                                           )
        Debug(msg)
        pchtrakt.logger.info(msg)
        pchtrakt.StopTrying = 1
        pchtrakt.lastPath = myMedia.oStatus.fullPath


def watchedFileCreation(myMedia):
    if YamjWatched and myMedia.oStatus.percent > 90:
        path = myMedia.oStatus.fileName
        if YamJWatchedVithVideo:
            path = myMedia.oStatus.fullPath
            if not OnPCH:
                path = path.replace('/opt/sybhttpd/localhost.drives/','')
                path = path.split('/', 2)[2]
                path = '{0}{1}'.format(YamjWatchedPath, path)
        else:
            path = '{0}{1}'.format(YamjWatchedPath, path)
        path = '{0}.watched'.format(path)
        
        if not isfile(path):
            open(path, 'w')
            msg = 'I have created the file {0}'.format(path)
            Debug(msg)
            pchtrakt.logger.info(msg)
