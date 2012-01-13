# -*- coding: utf-8 -*-
# Authors: Jonathan Lauwers / Frederic Haumont
# URL: http://github.com/PCHtrakt/PCHtrakt
#
# This file is part of PCHtrakt.
#
# PCHtrakt is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PCHtrakt is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PCHtrakt.  If not, see <http://www.gnu.org/licenses/>.

from utilities import *
from regexes import *
import datetime
import os.path
import re

class MediaParser:

	def parseFileName(self,fileName):
		""" 
		Stolen from Sick Beard
		"""
		for (cur_pattern_name, cur_pattern) in ep_regexes:
			p=re.compile(cur_pattern, re.VERBOSE | re.IGNORECASE)
			match = p.match(fileName)
			if not match:
				continue
			res = p.findall(fileName)
		return res #("Lol",151,515) # p.findall(fileName)
		
