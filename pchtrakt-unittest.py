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

import unittest
from pch import *
from urllib2 import Request, urlopen, URLError, HTTPError
from xml.etree import ElementTree 
from lib import tvdb_api 
from lib import parser
from lib import regexes
import re


class TestPchRequestor(unittest.TestCase):

	def setUp(self):
		self.oPchRequestor = PchRequestor()

	"""def test_getStatus(self):
		self.assertEqual(self.oPchRequestor.getStatus("1.1.1.1").status, EnumStatus.UNKNOWN,
                         'Should be UNKNOWN')
	"""
						 
	def test_tvdbapi(self):
		t = tvdb_api.Tvdb()
		episode = t['Dexter'][6][9] # get season 1, episode 3 of show
		print episode['id'] # Print episode name
		print t['Dexter']['id'] # Print seadon name
		"""self.assertEqual(self.oPchRequestor.getStatus("1.1.1.1").status, EnumStatus.UNKNOWN,
                         'Should be UNKNOWN')
		""" 
		
	def test_me(self):
		o = parser.NameParser()
		Debug(o.parse("Breaking Bad - 2x03 - Bit by a Dead Bee.mkv"))
		Debug(o.parse("Breaking Bad - 2x03 - Bit by a Dead Bee.mkv").series_name)
		Debug(o.parse("Terra Nova - 1x11x12 - Occupation & Resistance.mkv").episode_numbers)
		Debug(o.parse("Terra Nova - 1x11x12 - Occupation & Resistance.mkv").series_name)
						 
	"""def test_parseResponse(self):
		self.assertEqual(self.oPchRequestor.parseResponse("<root><returnValue>0</returnValue></root>"), EnumStatus.NOPLAY,
                         'Should be NOPLAY')
	"""

if __name__ == '__main__':
    unittest.main()