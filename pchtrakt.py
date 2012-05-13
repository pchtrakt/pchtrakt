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
import json

from pchtrakt.pch import *
from pchtrakt.scrobble import *
from pchtrakt.config import *

from pchtrakt.movieparser import MovieResultNotFound

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

class PchTraktException(Exception):
    pass

tvdb = tvdb_api.Tvdb()

pchtrakt.oPchRequestor = PchRequestor()
pchtrakt.mediaparser = mp.MediaParser()
class media(): 
    def __str__(self):
        if isinstance(self.parsedInfo, mp.MediaParserResultTVShow):
            msg = u'TV Show : {0} - Season:{1} - Episode:{2} ' \
                    '- {3}% - {4} - TvDB: {5}'.format(
                    self.parsedInfo.name,
                    self.parsedInfo.season_number,
                    self.parsedInfo.episode_numbers,
                    self.oStatus.percent,
                    self.oStatus.status,
                    self.parsedInfo.id)
        else:
            msg = u'Movie : {0} - Year : {1} - ' \
                    '{2}% - IMDB: {3}'.format(
                    self.parsedInfo.name,
                    self.parsedInfo.year,
                    self.oStatus.percent,
                    self.parsedInfo.id)
        return msg

myMedia = media()

def printHelp():
    print('Usage {0} <options>'.format('pythpn pchtrak.py'))
    print('Options:')
    print('    -h,--help    :    display this message')
    print('    -d,--daemon  :    launches pchtrakt in the background')


def getParams():
    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   "dht:",
                                   ['daemon', 'help'])
    except getopt.GetoptError:
        print("Available options: -d, --daemon")
        sys.exit()

    for o, a in opts:
        # Run as a daemon
        if o in ('-d', '--daemon'):
            if sys.platform == 'win32':
                print('Daemonize not supported under Windows, ' \
                      'starting normally')
            else:
                pchtrakt.DAEMON = True
                pchtrakt.debug = False

        if o in ('-h', '--help'):
            printHelp()
            sys.exit()

        if o in ('-t'):
            try:
                utils.checkSettings()
            except util.AuthenticationTraktError:
                pass
            finally:
                sys.exit()

                
def daemonize():
    """
    Fork off as a daemon
    """

    # Make a non-session-leader child process
    try:
        pid = os.fork()  # @UndefinedVariable - only available in UNIX
        if pid != 0:
            sys.exit(0)
    except OSError as e:
        raise RuntimeError("1st fork failed: %s [%d]" %
                   (e.strerror, e.errno))

    os.setsid()  # @UndefinedVariable - only available in UNIX

    # Make sure I can read my own files and shut out others
    prev = os.umask(0)
    os.umask(prev and int('077', 8))

    # Make the child a session-leader by detaching from the terminal
    try:
        pid = os.fork()  # @UndefinedVariable - only available in UNIX
        if pid != 0:
            sys.exit(0)
    except OSError as e:
        raise RuntimeError("2st fork failed: %s [%d]" % (e.strerror, e.errno))

    dev_null = file('/dev/null', 'r')
    os.dup2(dev_null.fileno(), sys.stdin.fileno())


def doWork():
    myMedia.ScrobResult = 0
    myMedia.oStatus = pchtrakt.oPchRequestor.getStatus(ipPch, 5)
    if pchtrakt.lastPath != myMedia.oStatus.fullPath:
        pchtrakt.StopTrying = 0
        myMedia.parsedInfo = None
    if YamjWatched == True:
        try:
            watchedFileCreation(myMedia)
        except BaseException as e:
            Debug('::: {0} :::'.format(pchtrakt.lastPath))
            Debug('::: {0} :::'.format(e))
            pchtrakt.logger.error(e)
    if not pchtrakt.StopTrying:
        if myMedia.oStatus.status not in   [EnumStatus.NOPLAY, 
                                            EnumStatus.UNKNOWN,
                                            EnumStatus.PAUSE]:
            pchtrakt.allowedPauseTime = TraktMaxPauseTime
            if myMedia.oStatus.status != EnumStatus.LOAD:
                if myMedia.parsedInfo == None:
                    myMedia.parsedInfo = pchtrakt.mediaparser.parse(
                                            myMedia.oStatus.fileName)
                Debug(myMedia.__str__())
                videoStatusHandle(myMedia)
        elif (myMedia.oStatus.status == EnumStatus.PAUSE 
            and pchtrakt.allowedPauseTime > 0):
            pchtrakt.allowedPauseTime -= sleepTime
            Debug(myMedia.__str__())
        else:
            if pchtrakt.lastPath != '':
                if not pchtrakt.watched:
                    videoStopped()
                if pchtrakt.allowedPauseTime <= 0:
                    pchtrakt.logger.info('It seems you paused ' \
                                         'the video for more than {0} minutes: ' \
                                         'I say to trakt you stopped watching ' \
                                         'your video'.format(TraktMaxPauseTime/60))
                pchtrakt.watched = 0
                pchtrakt.lastPath = ''
                pchtrakt.isMovie = 0
                pchtrakt.isTvShow = 0
            Debug("PCH status = {0}".format(myMedia.oStatus.status))


def stopTrying():
    try:
        pchtrakt.StopTrying = 1
        pchtrakt.lastPath = myMedia.oStatus.fullPath
    except Exception as e:
        pass
        

if __name__ == '__main__':
    getParams()
    if pchtrakt.DAEMON:
        daemonize()
    pchtrakt.logger.info('Pchtrakt START')
    while not pchtrakt.stop:
        try:
            try:
                doWork()
                sleep(sleepTime)
            except (KeyboardInterrupt, SystemExit):
                Debug(':::Stopping pchtrakt:::')
                pchtrakt.stop = 1
                videoStopped()
            except tvdb_exceptions.tvdb_shownotfound as e:
                stopTrying()
                msg = (':::TheTvDB - Show not found ' \
                       '{0} :::'.format(pchtrakt.lastPath))
                Debug(msg)
                pchtrakt.logger.warning(msg)
                sleep(sleepTime)
            except utils.AuthenticationTraktError as e:
                stopTrying()
                Debug(':::{0}::'.format(e))
                pchtrakt.logger.error(e)
                sleep(sleepTime)
            except utils.MaxScrobbleError as e:
                stopTrying()
                Debug(':::{0}:::'.format(e))
                pchtrakt.logger.error(e)
                sleep(sleepTime)
            except MovieResultNotFound as e:
                stopTrying()
                msg = ':::Movie not found - {0}:::'.format(e.file_name)
                Debug(msg)
                pchtrakt.logger.error(msg)
                sleep(sleepTime)
            except PchTraktException as e:
                stopTrying()
                msg = ':::PchTraktException - {0}:::'.format(e)
                Debug(msg)
                pchtrakt.logger.error(msg)
                sleep(sleepTime)
        except Exception as e:
           stopTrying()
           Debug(u'::: {0} :::'.format(pchtrakt.lastPath))
           Debug(u'::: {0} :::'.format(e))
           pchtrakt.logger.exception('This should never happend! Please contact me with the error if you read this')
           pchtrakt.logger.exception(pchtrakt.lastPath)
           pchtrakt.logger.exception(e)
           sleep(sleepTime)
    pchtrakt.logger.info('Pchtrakt STOP')
