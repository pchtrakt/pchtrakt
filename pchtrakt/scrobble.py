from sys import version_info
from os.path import isfile
from os import listdir
from xml.etree import ElementTree
# from xml.dom.minidom import parse not sure if used

from lib import utilities
from lib.utilities import Debug
import pchtrakt
from pchtrakt.exception import BetaSerieAuthenticationException
from pchtrakt import mediaparser as mp
from pchtrakt import betaseries as bs
from pchtrakt.config import *
from time import sleep
from pchtrakt.pch import EnumStatus
import pchtrakt, glob, os, re


class EnumScrobbleResult:
    KO = 0
    TRAKTOK = 1
    BETASERIESOK= 2

def showStarted(myMedia):
    if TraktScrobbleTvShow:
        response = utilities.watchingEpisodeOnTrakt(myMedia.parsedInfo.id,
                                                    myMedia.parsedInfo.name,
                                                    myMedia.parsedInfo.year,
                                                    str(myMedia.parsedInfo.season_number),
                                                    str(myMedia.parsedInfo.episode_numbers[myMedia.idxEpisode]),
                                                    str(myMedia.oStatus.totalTime),
                                                    str(myMedia.oStatus.percent))
        msg = u'Sending play: {0} {1} {2} {3}' \
              ' {4} {5} {6}'.format(myMedia.parsedInfo.id,
                                    myMedia.parsedInfo.name,
                                    myMedia.parsedInfo.year,
                                    str(myMedia.parsedInfo.season_number),
                                    str(myMedia.parsedInfo.episode_numbers[myMedia.idxEpisode]),
                                    str(myMedia.oStatus.totalTime),
                                    str(myMedia.oStatus.percent))
        Debug(msg)
        pchtrakt.logger.info(msg)
        if response != None:
            msg = 'Video playing: %s - %s' %(response['status'],response['message'])
            
        else:
            msg = 'No response from Trakt.tv'
        Debug(msg)
        pchtrakt.logger.info(msg)
    
def movieStarted(myMedia):
    response = utilities.watchingMovieOnTrakt(myMedia.parsedInfo.id,
                                               myMedia.parsedInfo.name,
                                               myMedia.parsedInfo.year,
                                               str(myMedia.oStatus.totalTime),
                                               str(myMedia.oStatus.percent))
    if response != None:
        msg = 'Video playing: %s - %s' %(response['status'],response['message'])
    else:
        msg = 'No response from Trakt.tv'    
    Debug(msg)
    pchtrakt.logger.info(msg)
    
    
def showStopped():
    response = utilities.cancelWatchingEpisodeOnTrakt()
    if response != None:
        msg = 'Video stopped: %s - %s' %(response['status'],response['message'])
    else:
        msg = 'No response from Trakt.tv' 
    Debug(msg)
    pchtrakt.logger.info(msg)
    
    
def movieStopped():
    response = utilities.cancelWatchingMovieOnTrakt()
    if response != None:
        msg = 'Video stopped: %s - %s' %(response['status'],response['message'])
    else:
        msg = 'No response from Trakt.tv' 
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
            Debug('(BetaSeries) Is episode watched: {0}'.format(isWatched))
            msg = '(BetaSeries) Video is '
            if not isWatched:
                result = bs.scrobbleEpisode(serieXml
                                                    ,token,
                                                    myMedia.parsedInfo.season_number,
                                                    myMedia.parsedInfo.episode_numbers[myMedia.idxEpisode])
                bs.destroyToken(token)
                msg += 'ending: '
            else:
                msg += 'already watched: '
            if result or isWatched:
                myMedia.ScrobResult |=  EnumScrobbleResult.BETASERIESOK
                msg += '{0} {1}x{2}'.format(myMedia.parsedInfo.name,
                                           myMedia.parsedInfo.season_number,
                                           myMedia.parsedInfo.episode_numbers[myMedia.idxEpisode]
                                           )
                Debug(msg)
                pchtrakt.logger.info(msg)
                
        else:
            myMedia.ScrobResult |= EnumScrobbleResult.BETASERIESOK
    except BetaSerieAuthenticationException as e:
        Debug(e)
        pchtrakt.logger.info(e)
    except Exception as e:
        Debug(e)
        pchtrakt.logger.exception(e)
    if TraktScrobbleTvShow:
        result = 0
        response = utilities.scrobbleEpisodeOnTrakt(myMedia.parsedInfo.id,
                                                    myMedia.parsedInfo.name,
                                                    myMedia.parsedInfo.year,
                                                    str(myMedia.parsedInfo.season_number),
                                                    str(myMedia.parsedInfo.episode_numbers[myMedia.idxEpisode]),
                                                    str(myMedia.oStatus.totalTime),
                                                    str(myMedia.oStatus.percent))
        if response:
            msg = '(Trakt) Video is ending: %s - %s ' %(response['status'],response['message'])
            Debug(msg)
            pchtrakt.logger.info(msg)
            result = 1
        
        if result == 1:
            myMedia.ScrobResult |= EnumScrobbleResult.TRAKTOK
    else:  
        myMedia.ScrobResult |= EnumScrobbleResult.TRAKTOK
    return myMedia.ScrobResult == EnumScrobbleResult.TRAKTOK | EnumScrobbleResult.BETASERIESOK
    
    
def movieIsEnding(myMedia):
    response = utilities.scrobbleMovieOnTrakt(myMedia.parsedInfo.id,
                                               myMedia.parsedInfo.name,
                                               myMedia.parsedInfo.year,
                                               str(myMedia.oStatus.totalTime),
                                               str(myMedia.oStatus.percent))
    if response != None:
        msg = 'Video is ending: %s - %s ' %(response['status'],response['message'])
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
            if myMedia.oStatus.percent > 90:
                pchtrakt.watched  = 1
                Debug('Started at more than 90%! I''m not doing anything!')
            else:
                movieStarted(myMedia)
    if not pchtrakt.watched:
        if myMedia.oStatus.percent > 90:
            pchtrakt.watched = movieIsEnding(myMedia)
        elif myMedia.oStatus.currentTime > pchtrakt.currentTime + int(TraktRefreshTime)*60:
            pchtrakt.currentTime = myMedia.oStatus.currentTime
            movieStillRunning(myMedia)
    elif myMedia.oStatus.percent < 10 and myMedia.oStatus.status != EnumStatus.STOP:
        Debug('It seems you came back at the begining of the video... so I say to trakt it\'s playing')
        pchtrakt.watched = 0
        pchtrakt.currentTime = myMedia.oStatus.currentTime
        movieStarted(myMedia)
            
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
        if myMedia.oStatus.percent > 90:
            pchtrakt.watched = showIsEnding(myMedia)
        elif myMedia.oStatus.currentTime > pchtrakt.currentTime + int(TraktRefreshTime)*60:
            pchtrakt.currentTime = myMedia.oStatus.currentTime
            showStillRunning(myMedia)        
        elif doubleEpisode and myMedia.oStatus.percent > (myMedia.idxEpisode+1) * 90.0/len(myMedia.parsedInfo.episode_numbers) and myMedia.idxEpisode+1 < len(myMedia.parsedInfo.episode_numbers):
            showIsEnding(myMedia)
            myMedia.idxEpisode += 1
            showStarted(myMedia)
                
    elif myMedia.oStatus.percent < 10 and myMedia.oStatus.status != EnumStatus.STOP:
        Debug('It seems you came back at the begining of the video... so I say to trakt it\'s playing')
        pchtrakt.watched = 0
        pchtrakt.currentTime = myMedia.oStatus.currentTime
        showStarted(myMedia)

def videoStatusHandle(myMedia):
    if isinstance(myMedia.parsedInfo,mp.MediaParserResultTVShow):
        if TraktScrobbleTvShow or BetaSeriesScrobbleTvShow:
            videoStatusHandleTVSeries(myMedia)
        pchtrakt.isTvShow = 1 #would be better to do this when parsing
    elif isinstance(myMedia.parsedInfo,mp.MediaParserResultMovie):
        if TraktScrobbleMovie:
            videoStatusHandleMovie(myMedia)
        pchtrakt.isMovie = 1
    pchtrakt.lastPath = myMedia.oStatus.fullPath


def isIgnored(myMedia):
    ignored = False
    
    msg = u'File: {0}'.format(myMedia.oStatus.fileName)
    Debug(msg)
    pchtrakt.logger.info(msg)
    
    ignored = isKeywordIgnored(myMedia.oStatus.fileName)
    
    if not ignored and ignored_repertory[0] != '':
        for el in myMedia.oStatus.fullPath.split('/'):
            if el <> '' and el in ignored_repertory:
                msg = 'This video is in a ignored repertory: {0}'.format(el)
                ignored = True
                break

    if not ignored and YamjIgnoredCategory[0] != '':
        if isinstance(myMedia.parsedInfo, mp.MediaParserResultTVShow):
            files = listdir(YamjPath)
            for file in files:
                if file.endswith('xml'):
                    file = unicode(file, errors='replace')
                    if file.find(myMedia.parsedInfo.name) >= 0:
                        oXml = ElementTree.parse(YamjPath + file)
                        ignored = isGenreIgnored(oXml.findall('.//genre'))
                        if ignored:
                            break
        else:
            file = unicode(myMedia.oStatus.fileName.rsplit('.',1)[0] + '.xml', errors='replace')
            oXml = ElementTree.parse(YamjPath + file)
            genres = oXml.findall('.//genre')
            
            ignored = isGenreIgnored(genres)
    return ignored

def isKeywordIgnored(title):
    if ignored_keywords[0] != '':
        for keyword in ignored_keywords:
            if keyword.lower() in title.lower():
                msg = u'This file contains a ignored keyword. Waiting for next file to start.'
                Debug(msg)
                pchtrakt.logger.info(msg)
                return True
    return False
    
def isGenreIgnored(genres):
    txt = 'The ignored genres are :{0}'.format(YamjIgnoredCategory)
    Debug(txt)
    pchtrakt.logger.info(txt)
    for genre in genres:
        genre = genre.text.strip().lower()
        txt = 'This genre is {0}'.format(genre)
        txt += ' --- Should it be ignored? {0}'.format(genre in YamjIgnoredCategory)
        Debug(txt)
        pchtrakt.logger.info(txt)
        if genre in YamjIgnoredCategory:
            txt = 'This video is in the ignored genre {0}'.format(genre)
            Debug(txt)
            pchtrakt.logger.info(txt)
            return True
    return False
    
def watchedFileCreation(myMedia):
    if myMedia.oStatus.percent > 90:
        path = myMedia.oStatus.fileName
        if YamJWatchedVithVideo:
            path = myMedia.oStatus.fullPath
            if not OnPCH:
                path = path.replace('/opt/sybhttpd/localhost.drives/','')
                path = path.split('/', 2)[2]
                path = '{0}{1}'.format(YamjWatchedPath, path)
        else:
            path = '{0}{1}'.format(YamjWatchedPath, path)
        watchedPath = '{0}.watched'.format(path)
        if not isfile(watchedPath):
            f = open(watchedPath, 'w')
            f.close()
            msg = 'I have created the file {0}'.format(watchedPath)
            Debug(msg)
            pchtrakt.logger.info(msg)
            if  updatexmlwatched !="":
                msg = 'Starting xml update in '+updatexmlwatched
                Debug(msg)
                pchtrakt.logger.info(msg)
                if pchtrakt.isMovie:
                    if version_info >= (2,7):
                        pass #todo
                    previous = None
                    for xmlword in moviexmlfind:
                        fileinfo = updatexmlwatched + xmlword + "*.xml"
                        for name in glob.glob(fileinfo):
                            if myMedia.oStatus.fileName[:-4] in open(name).read():#gets xml file name as name
                                tree = ElementTree.parse(name)
                                for movie in tree.findall('movies/movie'):
                                    if movie.find('baseFilenameBase').text == myMedia.oStatus.fileName[:-4]:#for  content in penContents:
                                        movie.find('watched').text = 'true'
                                        for mfile in movie.findall('files/file'):
                                            mfile.set('watched', 'true')
                                            bak_name = name[:-4]+'.bak'
                                            tree.write(bak_name)
                                            os.rename(bak_name, name)
                                            txt = name.replace(updatexmlwatched, '') + ' has been modified as watched for ' + myMedia.oStatus.fileName
                                            pchtrakt.logger.info(txt)
                                            previous = xmlword
                                        break
                                break
                elif pchtrakt.isTvShow:
                    epno = str(myMedia.parsedInfo.episode_numbers).replace('[', '').replace(']', '')
                    if version_info >= (2,7): #[@...=...] only available with python >= 2.7 
                        xpath = "*/movie/files/file[@firstPart='{0}'][@season='{1}']".format(
                                                    ep_no,str(myMedia.parsedInfo.season_number))
                    else:
                        xpath = "*/movie/files/file"
                    a = re.split("([-|.]*[Ss]\\d\\d[Ee]\\d\\d.)", myMedia.oStatus.fileName)
                    if len(a) == 1:
                        a = re.split("(?P<season_num>\d+)[. _-]*", myMedia.oStatus.fileName)
                    ep_name = a[2][:-4].replace(".", " ").replace("- ", "")
                    season_xml = a[0][:-3].replace(".", " ").replace(" - ", "")
                    # f_size = str(os.path.getsize(myMedia.oStatus.fullPath))
                    ep_no = '01'
                    fileinfo = updatexmlwatched + "Set_" + season_xml + "*.xml"
                    Debug(fileinfo)
                    for name in glob.glob(fileinfo):
                        Debug(name)
                        if myMedia.oStatus.fileName in open(name).read():
                            tree = ElementTree.parse(name)
                            for movie in tree.findall(xpath):
                                Debug(movie.get('firstPart'))
                                if movie.get('firstPart') == epno and movie.get('season') == str(myMedia.parsedInfo.season_number):
                                    movie.set('watched', 'true')
                                    bak_name = name[:-4]+'.bak'
                                    tree.write(bak_name)
                                    os.rename(bak_name, name)
                                    txt = name.replace(updatexmlwatched, '') + ' has been modified as watched for ' + myMedia.oStatus.fileName
                                    pchtrakt.logger.info(txt)
                                    break
                    previous = None
                    for xmlword in tvxmlfind:
                        Debug(xmlword)
                        fileinfo = updatexmlwatched + xmlword + "*.xml"
                        for name in glob.glob(fileinfo):
                            Debug(name)
                            if myMedia.oStatus.fileName in open(name).read():
                                tree = ElementTree.parse(name)
                                for movie in tree.findall(xpath):
                                    if movie.get('firstPart') == epno and movie.get('season') == str(myMedia.parsedInfo.season_number):
                                        movie.set('watched', 'true')
                                        bak_name = name[:-4]+'.bak'
                                        tree.write(bak_name)
                                        os.rename(bak_name, name)
                                        txt = name.replace(updatexmlwatched, '') + ' has been modified as watched for ' + myMedia.oStatus.fileName
                                        pchtrakt.logger.info(txt)
                                        previous = xmlword#break
                                break
