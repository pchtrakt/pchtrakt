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

import os
import mediaparser as mp
from movieparser import MovieResultNotFound
from json import dump
from urllib import quote
from urllib2 import urlopen
from xml.etree import ElementTree
from xml.parsers.expat import ExpatError
from lib import utilities as utils
from lib.tvdb_api import tvdb_api 


mediaparser = mp.MediaParser()
tvdb = tvdb_api.Tvdb()

class library:
    def add(self, path):
        mySerieDict = {}
        myMovieList = []
        for root, subFolders, files in os.walk(path):
            for file in files:
                if (file.endswith('mkv') or file.endswith('avi') or file.endswith('mp4')):
                    utils.Debug(file)
                    try:
                        parsedInfo = mediaparser.parse(file)
                    except MovieResultNotFound:
                        utils.Debug('Error for file %s' % file)
                        continue
                    if isinstance(parsedInfo,mp.MediaParserResultTVShow):
                        for episode in parsedInfo.episode_numbers:
                            myEpisode = { 'season': parsedInfo.season_number, 
                                          'episode': episode}
                            if parsedInfo.series_name in mySerieDict:
                                mySerieDict[parsedInfo.series_name].append(myEpisode)
                            else:
                                mySerieDict[parsedInfo.series_name] = [myEpisode]
                    elif isinstance(parsedInfo,mp.MediaParserResultMovie):
                        ImdbAPIurl = ('http://www.imdbapi.com/?t={0}&y={1}&r=xml'
                                            .format(quote(parsedInfo.movie_title),
                                            parsedInfo.year))
                        oResponse = urlopen(ImdbAPIurl)
                        try:   
                            oXml = ElementTree.XML(oResponse.read())
                        except ExpatError: 
                            utils.Debug('Error for movie %s' % (parsedInfo.movie_title))
                            continue
                        id = oXml.find('movie').get('id')
                        matchedTitle = oXml.find('movie').get('title')
                        utils.Debug('Matching %s:' % parsedInfo.movie_title)
                        myMovie = { 'imdb_id': id,
                                    'title': matchedTitle,
                                    'year': parsedInfo.year }
                        myMovieList.append(myMovie)
                        print myMovie
        
        # for serie, episodes in mySerieDict.iteritems():
            # id = tvdb[serie]['id']
            # year = tvdb[serie]['firstaired'].split('-')[0]
            # episodes = sorted(episodes, key=lambda student: student['episode'])
            # episodes = sorted(episodes, key=lambda student: student['season'])
            # utils.setEpisodesInLibraryOnTrakt(id,serie,year,episodes)
   
        
        f = open('output.txt', 'w')
        dump(myMovieList, f)
        f.close()
    