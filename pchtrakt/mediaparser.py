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

from os.path import basename, isfile
from urllib import quote_plus
from urllib2 import urlopen, HTTPError, URLError
import json
from lib import parser
from movieparser import *
from lib.tvdb_api import tvdb_exceptions
from pchtrakt.config import *
from lib.tvdb_api import tvdb_api,tvdb_exceptions
from lib.utilities import Debug

tvdb = tvdb_api.Tvdb()

class MediaParserResult():
    def __init__(self,file_name):
        self.file_name = file_name
        
class MediaParserResultTVShow(MediaParserResult):
    def __init__(self,file_name,name,season_number,episode_numbers):
        self.file_name = file_name
        self.name = name
        self.season_number = season_number
        self.episode_numbers = episode_numbers
        if self.name in cacheSerie.dictSerie:
            self.id = cacheSerie.dictSerie[self.name]['TvDbId']
            self.year = cacheSerie.dictSerie[self.name]['Year']
        else:
            self.id = tvdb[self.name]['id']
            if tvdb[self.name]['firstaired'] != None:
                self.year = tvdb[self.name]['firstaired'].split('-')[0]
            else:
                self.year = None
            cacheSerie.dictSerie[self.name]={'Year':self.year,
                                            'TvDbId':self.id}

            with open('cache.json','w') as f:
                json.dump(cacheSerie.dictSerie, f, separators=(',',':'), indent=4)
        
class MediaParserResultMovie(MediaParserResult):
    def __init__(self,file_name,name,year,imdbid):
        self.file_name = file_name
        self.name = name
        self.year = year
        
        ImdbAPIurl = ('http://www.omdbapi.com/?t={0}&y={1}'.format(
                                        quote_plus(self.name),
                                        self.year))
        Debug("Trying search 1: "+ImdbAPIurl)
        try:
            oResponse = urlopen(ImdbAPIurl,None,5)
            myMovieJson = json.loads(oResponse.read())
            self.id = myMovieJson['imdbID']
            Debug("Found Movie match using: "+ImdbAPIurl)
        except URLError, HTTPError:
            ImdbAPIurl = ('http://www.deanclatworthy.com/' \
                          'imdb/?q={0}&year={1}'.format(
                                quote_plus(self.name),
                                self.year))
            Debug("Trying search 2: "+ImdbAPIurl)
            try:
                oResponse = urlopen(ImdbAPIurl,None,5)
                myMovieJson = json.loads(oResponse.read())
                self.id = myMovieJson['imdbid']
                Debug("Found Movie match using: "+ImdbAPIurl)
            except:
                try: 
                    address = ('http://www.google.com/search?q=www.imdb.com:site+{0}&num=1&start=0'.format(quote_plus(self.name)))
                    Debug("Trying search 3: "+address)
                    request = Request(address, None, {'User-Agent':'Mosilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11'})
                    urlfile = urlopen(request)
                    page = urlfile.read()
                    entries = re.findall("/title/tt(\d{7})/", page)
                    self.id = "tt"+str(entries[0])
                    Debug('Search address = '+ address + ' ID = ' + self.id)
                except URLError, HTTPError:
                    pass
    #Might be able to use third search as only search?    
class MediaParserUnableToParse(Exception):
    def __init__(self, file_name):
        self.file_name = file_name
    
class MediaParser():
    def __init__(self):
        self.TVShowParser = parser.NameParser()
        self.MovieParser = MovieParser()
        
    def parse(self, file_name):
        try:
            parsedResult = self.TVShowParser.parse(file_name)
            oResultTVShow = MediaParserResultTVShow(file_name,parsedResult.series_name,parsedResult.season_number,parsedResult.episode_numbers)
            return oResultTVShow
        except parser.InvalidNameException as e:
            oMovie = self.MovieParser.parse(file_name)
            return oMovie
        raise MediaParserUnableToParse("Unable to parse the filename and detecte an movie or a tv show")
        
    
        
