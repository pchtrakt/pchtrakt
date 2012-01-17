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

from xml.etree import ElementTree 
from string import split
from urllib2 import Request, urlopen, URLError, HTTPError
from lib.utilities import Debug
import math

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
		self.mediaType = ""
		self.currentChapter = 0 # For Blu-ray Disc only
		self.totalChapter = 0 # For Blu-ray Disc only
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
					oPchStatus.currentTime = int(oXml.find("response/currentTime").text)
					oPchStatus.totalTime = int(oXml.find("response/totalTime").text)
					if oXml.find("response/mediatype")!= None:
						self.mediaType = oXml.find("response/mediatype").text
					if(self.mediaType == "BD"): # Blu-ray Disc are not handle like .mkv or .avi files
						oPchStatus.fileName = oPchStatus.fullPath.split('/')[::-1][1] # add a / on last position when ISO
						oPchStatus.currentChapter = int(oXml.find("response/currentchapter").text)
						oPchStatus.totalChapter = int(oXml.find("response/totalchapter").text)
						if oPchStatus.totalChapter!= 0:
							oPchStatus.percent = int(math.ceil(float(oPchStatus.currentChapter) / float(oPchStatus.totalChapter) * 100.0)) # approximation because chapters are differents
					else:
						oPchStatus.fileName = oPchStatus.fullPath.split('/')[::-1][0]
						if oPchStatus.totalTime!=0:
							oPchStatus.percent = int(math.ceil(float(oPchStatus.currentTime) / float(oPchStatus.totalTime) * 100.0))
				else:
					oPchStatus.status=EnumStatus.NOPLAY
			else:
				oPchStatus.status = EnumStatus.UNKNOWN	
		except ElementTree.ParseError, e:
			oPchStatus.error = e
			oPchStatus.status = EnumStatus.UNKNOWN		
		return oPchStatus
		
	def getStatus(self,ip,timeout=5.0):
		oPchStatus = PchStatus()
		try:
			oResponse = urlopen("http://" + ip + ":8008/playback?arg0=get_current_vod_info",None,timeout)
			oPchStatus = self.parseResponse(oResponse.readlines()[0])
		except HTTPError, e:
			oPchStatus.error = e
			oPchStatus.status = EnumStatus.UNKNOWN
			#Debug("Fail to contact server : " + str(e.reason))		
		except URLError, e:
			oPchStatus.error = e
			oPchStatus.status = EnumStatus.UNKNOWN
			#Debug("Fail to contact server : " + str(e.reason))			
		return oPchStatus
		
	
