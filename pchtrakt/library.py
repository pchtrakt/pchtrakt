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
from lib import utilities as utils
from lib.tvdb_api import tvdb_api 

mediaparser = mp.MediaParser()
tvdb = tvdb_api.Tvdb()

class library:
    def add(self, path):
        mySerieDict = {}
        for root, subFolders, files in os.walk(path):
            for file in files:
                if not file.endswith('srt'):
                    parsedInfo = mediaparser.parse(file)
                    if isinstance(parsedInfo,mp.MediaParserResultTVShow):
                        for episode in parsedInfo.episode_numbers:
                            myEpisode = { 'season': parsedInfo.season_number, 
                                          'episode': episode}
                            if parsedInfo.series_name in mySerieDict:
                                mySerieDict[parsedInfo.series_name].append(myEpisode)
                            else:
                                mySerieDict[parsedInfo.series_name] = [myEpisode]
                    elif isinstance(parsedInfo,mp.MediaParserResultMovie):
                        pass
                        
        for serie, episodes in mySerieDict.iteritems():
            id = tvdb[serie]['id']
            year = tvdb[serie]['firstaired'].split('-')[0]
            episodes = sorted(episodes, key=lambda student: student['episode'])
            episodes = sorted(episodes, key=lambda student: student['season'])
            print '%s: %s %s' % (serie,id,year)
            print episodes
            # print utils.setEpisodesInLibraryOnTrakt(id,serie,year,episodes)


    