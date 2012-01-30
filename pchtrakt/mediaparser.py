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

from lib import parser
from movieparser import *

class MediaParserResult():
    def __init__(self,file_name):
        self.file_name = file_name
class MediaParserResultAnime(MediaParserResult):
    def __init__(self,file_name,series_name,episode_numbers):
        self.file_name = file_name
        self.series_name = series_name
        self.episode_numbers = episode_numbers
        
class MediaParserResultTVShow(MediaParserResult):
    def __init__(self,file_name,series_name,season_number,episode_numbers):
        self.file_name = file_name
        self.series_name = series_name
        self.season_number = season_number
        self.episode_numbers = episode_numbers
        
class MediaParserResultMovie(MediaParserResult):
    def __init__(self,file_name,movie_title,year,imdbid):
        self.file_name = file_name
        self.movie_title = movie_title
        self.year = year
        self.imdbid = imdbid
        
class MediaParserUnableToParse(Exception):
    def __init__(self, file_name):
        self.file_name = file_name
    
class MediaParser():
    def __init__(self):
        self.TVShowParser = parser.NameParser()
        self.MovieParser = MovieParser()
        
    def parse(self, file_name):
        #TODO(achtus): try to detect tv show with 00x00 or 0x00 or s00e00 or s0e0 or s0e00
        try:
            oMovie = self.MovieParser.parse(file_name)
            return oMovie
        except MovieResultNotFound,e:
            parsedResult = self.TVShowParser.parse(file_name)
            oResultTVShow = MediaParserResultTVShow(file_name,parsedResult.series_name,parsedResult.season_number,parsedResult.episode_numbers)
            return oResultTVShow
        raise MediaParserUnableToParse("Unable to parse the filename and detecte an movie or a tv show")
        
    
        