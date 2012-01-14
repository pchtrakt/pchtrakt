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

from xml.etree import ElementTree 
from string import split
from urllib2 import Request, urlopen, URLError, HTTPError
from lib.utilities import Debug

class EnumStatus:
	NOPLAY='noplay'
	PLAY='play'
	PAUSE='pause'
	LOAD='buffering'
	STOP='stop'
	UNKNOWN='unknown'
	
class PchStatus:
	def __init__(self):
		self.status=EnumStatus.NOPLAY
		self.fullPath = ""
		self.fileName = ""
		self.currentTime = 0
		self.totalTime = 0
		self.percent = 0
		self.error = None 
		
class PchRequestor:
	
	def parseResponse(self, response):
		oPchStatus = PchStatus()
		try:
			oXml = ElementTree.XML(response) 
			if oXml.tag == "theDavidBox": # theDavidBox should be the root
				if oXml.find("returnValue").text == '0':
					oPchStatus.status = oXml.find("response/currentStatus").text
					oPchStatus.fullPath = oXml.find("response/fullPath").text
					oPchStatus.fileName = oPchStatus.fullPath.split('/')[::-1][0]
					oPchStatus.currentTime = float(oXml.find("response/currentTime").text)
					oPchStatus.totalTime = float(oXml.find("response/totalTime").text)
					if oPchStatus.totalTime!=0:
						oPchStatus.percent = int(oPchStatus.currentTime / oPchStatus.totalTime * 100)
					else:
						oPchStatus.percent = 0
				else:
					oPchStatus.status=EnumStatus.NOPLAY
			else:
				oPchStatus.status = EnumStatus.UNKNOWN	
		except ElementTree.ParseError, e:
			oPchStatus.error = e
			oPchStatus.status = EnumStatus.UNKNOWN		
		return oPchStatus
		
	def getStatus(self,ip,timeout):
		oPchStatus = PchStatus()
		try:
			oResponse = urlopen("http://" + ip + ":8008/playback?arg0=get_current_vod_info",None,timeout)
			oPchStatus = self.parseResponse(oResponse)
		except HTTPError, e:
			oPchStatus.error = e
			oPchStatus.status = EnumStatus.UNKNOWN
			#Debug("Fail to contact server : " + str(e.reason))		
		except URLError, e:
			oPchStatus.error = e
			oPchStatus.status = EnumStatus.UNKNOWN
			#Debug("Fail to contact server : " + str(e.reason))			
		return oPchStatus
		
	
