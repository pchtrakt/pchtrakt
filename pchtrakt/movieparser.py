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

from lib import regexes
import re
import mediaparser

regexes_movies = [ 
					("imdbid", # not works
						# foobar.[ID ttxxxxxx]
						"""
						^[\[]ID[ ](?P<imdbid>.+?[.])[\]]
						"""
					)
					,				
					("movie_year", # bug sometimes 1080 = year 
						# Movie.Title.(year) or Movie.Title.[year]
						"""
						^(?P<movie_title>.+?)[. _-]+
						[\(\[]{0,1}(?P<year>[0-9]{4})[\)\]]{0,1}
						"""
					)
				]

class MovieParser():
	def __init__(self):
		self.compiled_regexes = []
		self._compile_regexes()
		
	def _compile_regexes(self):
		for (cur_pattern_name, cur_pattern) in regexes_movies:
			try:
				cur_regex = re.compile(cur_pattern, re.VERBOSE | re.IGNORECASE)
			except re.error, errormsg:
				Debug(u"WARNING: Invalid movie_pattern, %s. %s" % (errormsg, cur_regex.pattern))
			else:
				self.compiled_regexes.append((cur_pattern_name, cur_regex))		
	
	def parse(self,file_name):
		oResult = None
		for (name,regex) in self.compiled_regexes:
			match = regex.match(file_name)
			if not match:
					continue
			
			tmp_movie_title = ""
			tmp_year = None
			tmp_imdbid = None
			named_groups = match.groupdict().keys()
			
			if 'movie_title' in named_groups:
				tmp_movie_title = self.clean_movie_name(match.group('movie_title'))
				
			if 'year' in named_groups:
				tmp_year = match.group('year')
				
			if 'imdbid' in named_groups:
				tmp_imdbid = match.group('imdbid')				
				
			#Debug(name + "=" + str(regex.search(file_name).groupdict()) + '	   [' + file_name + ']')
			return mediaparser.MediaParserResultMovie(file_name,tmp_movie_title,tmp_year,tmp_imdbid)
			break	
		raise MovieResultNotFound(file_name)

	def clean_movie_name(self, movie_name):
		"""Cleans up name by removing any . and _
		characters, along with any trailing hyphens.

		Is basically equivalent to replacing all _ and . with a
		space, but handles decimal numbers in string, for example:

		>>> cleanRegexedSeriesName("an.example.1.0.test")
		'an example 1.0 test'
		>>> cleanRegexedSeriesName("an_example_1.0_test")
		'an example 1.0 test'
		
		Stolen from dbr's tvnamer
		"""
		
		movie_name = re.sub("(\D)\.(?!\s)(\D)", "\\1 \\2", movie_name)
		movie_name = re.sub("(\d)\.(\d{4})", "\\1 \\2", movie_name) # if it ends in a year then don't keep the dot
		movie_name = re.sub("(\D)\.(?!\s)", "\\1 ", movie_name)
		movie_name = re.sub("\.(?!\s)(\D)", " \\1", movie_name)
		movie_name = movie_name.replace("_", " ")
		movie_name = re.sub("-$", "", movie_name)
		return movie_name.strip()
			
class MovieResultNotFound(Exception):
	def __init__(self, file_name):
		self.file_name = file_name		