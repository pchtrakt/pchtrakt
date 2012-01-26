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
from lib import regexes

class MediaTypeEnum:
	MOVIE="movie"
	TVSHOW="tvshow"
	UNKNOWN="unknown"

class MediaParserResult():
	def __init__(self,fileName):
		self.mediaType = MediaTypeEnum.UNKNOWN
		self.fileName = fileName
	
class MediaParser():
	def __init__(self):
		self.TVShowParser = parser.NameParser()
		
	def parse(self, fileName):
		oMediaParserResult = MediaParserResult(fileName)
		try:
			oTVShow = self.TVShowParser.parse(fileName)
			return oTVShow
		except parser.InvalidNameException,e:
			#TODO(achtus) Parse the movie file name
			return MediaTypeEnum.MOVIE
		#return oMediaParserResult
		