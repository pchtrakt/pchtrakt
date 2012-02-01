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

from pchtrakt import media
from pchtrakt.pch import *
from pchtrakt.scrobble import *
from pchtrakt.config import *
from pchtrakt import mediaparser as mp
from time import sleep
from lib.tvdb_api import tvdb_api 
from lib.tvdb_api import tvdb_exceptions
from lib import parser
from lib import regexes
from lib import utilities as utils
from datetime import date
from xml.etree import ElementTree
from urllib2 import Request, urlopen, URLError, HTTPError
from urllib import quote

tvdb = tvdb_api.Tvdb()

pchtrakt.oPchRequestor = PchRequestor()
pchtrakt.mediaparser = mp.MediaParser()

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
    media.oStatus = pchtrakt.oPchRequestor.getStatus(ipPch,5)
    if pchtrakt.lastPath != media.oStatus.fullPath:
        pchtrakt.StopTrying = 0
        pchtrakt.idOK = 0
    if not pchtrakt.StopTrying:
        if media.oStatus.status != EnumStatus.NOPLAY and media.oStatus.status != EnumStatus.UNKNOWN:
            if media.oStatus.status != EnumStatus.LOAD:
                media.parsedInfo = pchtrakt.mediaparser.parse(media.oStatus.fileName)
                if isinstance(media.parsedInfo,mp.MediaParserResultTVShow):
                    if media.parsedInfo.season_number == 0:
                        # anime = tvdb[media.parsedInfo.series_name].search(media.parsedInfo.episode_numbers[0], key = 'absolute_number')
                        # Debug(anime[0]['episodenumber'])
                        # Debug(anime[0]['seasonnumber'])
                        raise BaseException('No season - maybe anime?')
                    Debug('TV Show : %s - Season:%s - Episode:%s - %s%% - %s - TvDB: %s' 
                        %(media.parsedInfo.series_name,media.parsedInfo.season_number,
                        media.parsedInfo.episode_numbers,media.oStatus.percent,
                        media.oStatus.status,tvdb[media.parsedInfo.series_name]['id']))
                    media.id = tvdb[media.parsedInfo.series_name]['id']
                    media.year = (tvdb[media.parsedInfo.series_name]['firstaired']).split('-')[0]
                    videoStatusHandle(media)
                elif isinstance(media.parsedInfo,mp.MediaParserResultMovie):
                    if not pchtrakt.idOK:
                        ImdbAPIurl = ('http://www.imdbapi.com/?t=%s&y=%s&r=xml'
                                            %(quote(media.parsedInfo.movie_title),
                                            media.parsedInfo.year))
                        oResponse = urlopen(ImdbAPIurl)
                        oXml = ElementTree.XML(oResponse.read())
                        media.id = oXml.find('movie').get('id')
                        media.year = media.parsedInfo.year
                        pchtrakt.idOK = 1
                    Debug('Movie : %s - Year : %s - %s%% - IMDB: %s' 
                                            %(media.parsedInfo.movie_title,
                                                media.parsedInfo.year,
                                                media.oStatus.percent,
                                                media.id))
                    videoStatusHandle(media)
        else:
            if pchtrakt.lastPath != '':
                if not pchtrakt.watched:
                    videoStopped()
                pchtrakt.watched = 0
                pchtrakt.lastPath = ''
                pchtrakt.isMovie = 0
                pchtrakt.isTvShow = 0
            Debug("PCH status = %s" %media.oStatus.status)

def stopTrying():
    pchtrakt.StopTrying = 1
    pchtrakt.lastPath = media.oStatus.fullPath
    

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
        # except parser.InvalidNameException:
            # stopTrying()
            # Debug(':::What is this movie? %s Stop trying:::' %(pchtrakt.lastPath))
        except tvdb_exceptions.tvdb_shownotfound as e:
            stopTrying()
            msg = ':::TheTvDB - Show not found %s :::' %(pchtrakt.lastPath)
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
        except BaseException as e:
            stopTrying()
            Debug( '::: %s :::' %(pchtrakt.lastPath))
            Debug( '::: %s :::' %(e))
            pchtrakt.logger.exception(e)
