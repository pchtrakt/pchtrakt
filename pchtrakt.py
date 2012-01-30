#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Authors: Jonathan Lauwers / Frederic Haumont
# URL: http://github.com/pchtrakt/pchtrakt
#
# This file is part of pchtrakt.
#
# pchtrakt is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pchtrakt is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pchtrakt.  If not, see <http://www.gnu.org/licenses/>.

# pchtrakt - Connect your PCH 200 Series to trakt.tv :)
# pchtrakt uses some pyhton lib :
#    - tvdb_api (https://github.com/dbr/tvdb_api)
#    - nbrhttpconnection (another project)
#     - some classes from Sick Beard (http://sickbeard.com/)

import sys 
import getopt
import pchtrakt
import os

from pchtrakt.pch import *
from pchtrakt.scrobble import *
from pchtrakt.config import *
from time import sleep
from lib.tvdb_api import tvdb_api 
from lib.tvdb_api import tvdb_exceptions
from lib import parser
from lib import regexes
from lib import utilities as utils
from datetime import date

tvdb = tvdb_api.Tvdb()
MAXFD = 1024

pchtrakt.oPchRequestor = PchRequestor()
pchtrakt.oNameParser =  parser.NameParser()

def printHelp():
    print 'Usage %s <options>' % 'pchtrak.py'
    print 'Options:'
    print '    -d,--daemon:    launches pchtrakt in the background'


def getParams():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "dh", ['daemon','help']) #@UnusedVariable
    except getopt.GetoptError:
        print "Available options: -d, --daemon"
        sys.exit()

    for o, a in opts:
        # Run as a daemon
        if o in ('-d', '--daemon'):
            if sys.platform == 'win32':
                print "Daemonize not supported under Windows, starting normally"
            else:
                pchtrakt.DAEMON = True
                pchtrakt.debug = False
        
        if o in ('-h', '--help'):
            printHelp()
            sys.exit()

            
def daemonize():
    """
    Fork off as a daemon
    """

    # Make a non-session-leader child process
    try:
        pid = os.fork() #@UndefinedVariable - only available in UNIX
        if pid != 0:
            sys.exit(0)
    except OSError, e:
        raise RuntimeError("1st fork failed: %s [%d]" %
                   (e.strerror, e.errno))

    os.setsid() #@UndefinedVariable - only available in UNIX

    # Make sure I can read my own files and shut out others
    prev = os.umask(0)
    os.umask(prev and int('077', 8))

    # Make the child a session-leader by detaching from the terminal
    try:
        pid = os.fork() #@UndefinedVariable - only available in UNIX
        if pid != 0:
            sys.exit(0)
    except OSError, e:
        raise RuntimeError("2st fork failed: %s [%d]" % (e.strerror, e.errno))

    dev_null = file('/dev/null', 'r')
    os.dup2(dev_null.fileno(), sys.stdin.fileno())

def main():
    pchtrakt.oStatus = pchtrakt.oPchRequestor.getStatus(ipPch,5)
    if pchtrakt.currentPath != pchtrakt.oStatus.fullPath:
        pchtrakt.StopTrying = 0
    if not pchtrakt.StopTrying:
        if pchtrakt.oStatus.status != EnumStatus.NOPLAY and pchtrakt.oStatus.status != EnumStatus.UNKNOWN:
            if pchtrakt.oStatus.status != EnumStatus.LOAD:
                parsedInfo = pchtrakt.oNameParser.parse(pchtrakt.oStatus.fileName)
                if parsedInfo.season_number == 0:
                    # anime = tvdb[parsedInfo.series_name].search(parsedInfo.episode_numbers[0], key = 'absolute_number')
                    # Debug(anime[0]['episodenumber'])
                    # Debug(anime[0]['seasonnumber'])
                    raise BaseException('No season - maybe anime?')
                Debug('TV Show : %s - Season:%s - Episode:%s - %s%% - %s - TvDB: %s' 
                    %(parsedInfo.series_name,parsedInfo.season_number,
                    parsedInfo.episode_numbers,pchtrakt.oStatus.percent,
                    pchtrakt.oStatus.status,tvdb[parsedInfo.series_name]['id']))
                videoStatusHandle(pchtrakt.oStatus,str(tvdb[parsedInfo.series_name]['id']),str(tvdb[parsedInfo.series_name]['firstaired']).split('-')[0],parsedInfo)
        else:
            if pchtrakt.currentPath != '':
                if not pchtrakt.watched:
                    videoStopped()
                pchtrakt.watched = 0
                pchtrakt.currentPath = ''
            Debug("PCH status = %s" %pchtrakt.oStatus.status)

def videoStatusHandle(oStatus,id,year,parsedInfo):
    if len(parsedInfo.episode_numbers)>1:
        doubleEpisode = 1
    else:
        doubleEpisode = 0
    if pchtrakt.currentPath != oStatus.fullPath:
        pchtrakt.watched = 0
        pchtrakt.currentPath = oStatus.fullPath
        pchtrakt.currentTime = oStatus.currentTime
        pchtrakt.idxEpisode = 0
        if pchtrakt.currentPath != '':
            if doubleEpisode:
                pchtrakt.idxEpisode = 0
                while oStatus.percent > (pchtrakt.idxEpisode + 1) * 90.0/len(parsedInfo.episode_numbers):
                    pchtrakt.idxEpisode += 1
                id2 = tvdb[parsedInfo.series_name][parsedInfo.season_number][parsedInfo.episode_numbers[pchtrakt.idxEpisode]]['id']
                videoStarted(oStatus,id2,year,parsedInfo,pchtrakt.idxEpisode)
            else:
                videoStarted(oStatus,id,year,parsedInfo)
                
    if oStatus.currentTime > pchtrakt.currentTime + refreshTime*60:
        pchtrakt.currentTime = oStatus.currentTime
        videoStillRunning(oStatus,id,year,parsedInfo,pchtrakt.idxEpisode)        
    elif doubleEpisode and oStatus.percent > (pchtrakt.idxEpisode+1) * 90.0/len(parsedInfo.episode_numbers) and pchtrakt.idxEpisode+1 < len(parsedInfo.episode_numbers):
        videoIsEnding(oStatus,id,year,parsedInfo,pchtrakt.idxEpisode)
        sleep(5)
        pchtrakt.idxEpisode += 1
        id2 = tvdb[parsedInfo.series_name][parsedInfo.season_number][parsedInfo.episode_numbers[pchtrakt.idxEpisode]]['id']
        videoStarted(oStatus,id2,year,parsedInfo,pchtrakt.idxEpisode)
    elif oStatus.percent > 90:
        if not pchtrakt.watched:
            if doubleEpisode:
                pchtrakt.watched = videoIsEnding(oStatus,id,year,parsedInfo,pchtrakt.idxEpisode)
            else:
                 pchtrakt.watched = videoIsEnding(oStatus,id,year,parsedInfo)

def stopTrying():
    pchtrakt.StopTrying = 1
    pchtrakt.currentPath = pchtrakt.oStatus.fullPath
    

if __name__ == '__main__':
    getParams()
    if pchtrakt.DAEMON:
        daemonize()
    while not pchtrakt.stop:
        try:
            main()
            sleep(sleepTime)
        except (KeyboardInterrupt, SystemExit):
            Debug(':::Stopping pchtrakt:::')
            pchtrakt.stop = 1
        except parser.InvalidNameException:
            stopTrying()
            Debug(':::What is this movie? %s Stop trying:::' %(pchtrakt.currentPath))
        except tvdb_exceptions.tvdb_shownotfound as e:
            stopTrying()
            msg = ':::TheTvDB - Show not found %s :::' %(pchtrakt.currentPath)
            Debug(msg)
            pchtrakt.logger.warning(msg)
        except utils.AuthenticationTraktError as e:
            stopTrying()
            Debug(':::%s:::' % e.msg)
            pchtrakt.logger.error(e.msg)
        except utils.MaxScrobbleError as e:
            stopTrying()
            Debug(':::%s:::' % e.msg)
            pchtrakt.logger.error(e.msg)
        # except BaseException as e:
            # stopTrying()
            # Debug( '::: %s :::' %(pchtrakt.currentPath)
            # Debug( '::: %s :::' %(e)
            # pchtrakt.logger.exception(e)
