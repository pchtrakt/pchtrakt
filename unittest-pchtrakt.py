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

import unittest
from pchtrakt.pch import *
from pchtrakt.mediaparser import *
from urllib2 import URLError, HTTPError
from xml.etree import ElementTree 
from lib.tvdb_api import tvdb_api 
from lib import parser
from lib import regexes
import re
import ConfigParser

TVShows = [ 
			# Filename , Serie, #Season, #Episode(s) 
			 ("Dexter - 6x09.mkv","Dexter",6,[9])
			,("Terra Nova - 1x11x12 - Occupation & Resistance.mkv","Terra Nova",1,[11,12])
			,("Dexter - S06E09.mkv","Dexter",6,[9])
			,("Terra Nova - S01E11-12 - Occupation & Resistance.mkv","Terra Nova",1,[11,12])
			,("Dexter.6x09.mkv","Dexter",6,[9])
			,("Terra.Nova.1x11x12.Occupation.&.Resistance.mkv","Terra Nova",1,[11,12])
			,("Breaking.Bad.S02E03.Bit.by.a.Dead.Bee.mkv","Breaking Bad",2,[3])
			,("Dexter.S06E09.mkv","Dexter",6,[9])
			,("Terra.Nova.S01E11-12.Occupation.&.Resistance.mkv","Terra Nova",1,[11,12])
			,("Terra.Nova.S1E11-12.Occupation.&.Resistance.mkv","Terra Nova",1,[11,12])
			,("Dexter.S6E9.mkv","Dexter",6,[9])
			,("The Cleveland Show - S03E01 - BFFs.HDTV.mkv","The Cleveland Show",3,[1])
		]

Movies = [
			# Filename [I should inform the majors that theses files are some examples taken from the net ! ;-)]
			 ("Home.(2009).1080p") 
			,("Home (2009) 1080p")
			,("Home_(2009)_1080p")	
			,("Inception.BDRip.1080p.mkv")
			,("indiana jones and the last crusade 1989 1080p x264 dd5.1-m794.mkv")
			,("Indiana.Jones.and.the.Temple.of.Doom.[1984].HDTV.1080p.mkv")
			,("Inglourious.Basterds.(2009).BDRip.1080p.mkv")		
			,("James.Bond.04.Thunderball.1965.Bluray.1080p.DTSMA.x264.dxva-FraMeSToR.mkv")
			,("James.Bond.08.Live.and.Let.Die.1973.Bluray.1080p.DTSMA.x264.dxva-FraMeSToR.mkv")
			,("The.Godfather.Part.III.(1990).BDRip.1080p.[SET Godfather].mkv")
			,("Underworld.Rise.Of.The.Lycans.(2008).BDRip.1080p.[SET Underworld].mkv")
			,("unstoppable.2010.bluray.1080p.dts.x264-chd.mkv")
			,("UP.(2009).BDRip.720p.mkv") # epic !
			,("127.Hours.2010.1080p.BluRay.x264-SECTOR7.mkv")
			,("13.Assassins.2010.LIMITED.1080p.BluRay.x264-WEST.mkv")
			,("2012.(2009).BDRip.1080p.mkv")
			,("300.(2006).BDRip.1080p.mkv")
			,("Big.Fish.2003.1080p.BluRay.DTS.x264-DON")
			,("inf-fast5-1080p[ID tt1596343].mkv") # Who are looking this shit ?
			,("Le.Fabuleux.Destin.d'Amélie.Poulain.2001.1080p.BluRay.DTS.x264-CtrlHD")
			,("avchd-paul.2011.extended.1080p.x264")
			,("twiz-unknown-1080p")
		]				
				
class TestPchRequestor(unittest.TestCase):

	def setUp(self):
		self.oPchRequestor = PchRequestor()
		self.fakeResponseOTHER = u"<html><body>Not the theDavidBox api ;-)</body></html>"
		self.fakeResponseNOPLAY = u"<theDavidBox><returnValue>1</returnValue></theDavidBox>"
		self.fakeResponseBUFFERING = u"<theDavidBox><request><arg0>get_current_vod_info</arg0><module>playback</module></request><response><bufferStatus>0</bufferStatus><currentStatus>buffering</currentStatus><currentTime>2341</currentTime><downloadSpeed>0</downloadSpeed><fullPath>/opt/sybhttpd/localhost.drives/NETWORK_SHARE/download/Home.(2009).1080p.mkv</fullPath><lastPacketTime>0</lastPacketTime><mediatype>OTHERS</mediatype><seekEnable>true</seekEnable><title>/opt/sybhttpd/localhost.drives/NETWORK_SHARE/download/Home.(2009).1080p.mkv</title><totalTime>5620</totalTime></response><returnValue>0</returnValue></theDavidBox>"
		self.fakeResponsePAUSE = u"<theDavidBox><request><arg0>get_current_vod_info</arg0><module>playback</module></request><response><bufferStatus>0</bufferStatus><currentStatus>pause</currentStatus><currentTime>2341</currentTime><downloadSpeed>0</downloadSpeed><fullPath>/opt/sybhttpd/localhost.drives/NETWORK_SHARE/download/Home.(2009).1080p.mkv</fullPath><lastPacketTime>0</lastPacketTime><mediatype>OTHERS</mediatype><seekEnable>true</seekEnable><title>/opt/sybhttpd/localhost.drives/NETWORK_SHARE/download/Home.(2009).1080p.mkv</title><totalTime>5620</totalTime></response><returnValue>0</returnValue></theDavidBox>"
		self.fakeResponsePLAYING = u"<theDavidBox><request><arg0>get_current_vod_info</arg0><module>playback</module></request><response><bufferStatus>0</bufferStatus><currentStatus>play</currentStatus><currentTime>2341</currentTime><downloadSpeed>0</downloadSpeed><fullPath>/opt/sybhttpd/localhost.drives/NETWORK_SHARE/download/Home.(2009).1080p.mkv</fullPath><lastPacketTime>0</lastPacketTime><mediatype>OTHERS</mediatype><seekEnable>true</seekEnable><title>/opt/sybhttpd/localhost.drives/NETWORK_SHARE/download/Home.(2009).1080p.mkv</title><totalTime>5620</totalTime></response><returnValue>0</returnValue></theDavidBox>"
		self.fakeResponsePLAYING_BD = u"<theDavidBox><request><arg0>get_current_vod_info</arg0><module>playback</module></request><response><currentStatus>play</currentStatus><currentTime>82</currentTime><currentchapter>135</currentchapter><downloadSpeed>0</downloadSpeed><fullPath>/opt/sybhttpd/localhost.drives/SATA_DISK_B4/Video/Films/Home/</fullPath><lastPacketTime>0</lastPacketTime><mediatype>BD</mediatype><seekEnable>true</seekEnable><title>/opt/sybhttpd/localhost.drives/SATA_DISK_B4/Video/Films/Home/</title><totalTime>99</totalTime><totalchapter>909</totalchapter></response><returnValue>0</returnValue></theDavidBox>"
			
	def test_parseResponse(self):
		self.assertEqual(self.oPchRequestor.parseResponse(self.fakeResponseOTHER).status, EnumStatus.UNKNOWN, "Should be UNKNOWN")
		self.assertEqual(self.oPchRequestor.parseResponse(self.fakeResponseNOPLAY).status, EnumStatus.NOPLAY, "Should be NOPLAY")
		self.assertEqual(self.oPchRequestor.parseResponse(self.fakeResponseBUFFERING).status, EnumStatus.LOAD, "Should be LOAD")			
		self.assertEqual(self.oPchRequestor.parseResponse(self.fakeResponsePAUSE).status, EnumStatus.PAUSE, "Should be PAUSE")	
		self.assertEqual(self.oPchRequestor.parseResponse(self.fakeResponsePLAYING).status, EnumStatus.PLAY,"Should be PLAY")
		self.assertEqual(self.oPchRequestor.parseResponse(self.fakeResponsePLAYING).status, EnumStatus.PLAY,"Should be PLAY")
		self.assertEqual(self.oPchRequestor.parseResponse(self.fakeResponsePLAYING).totalTime, 5620,"Should be 5620 seconds")
		self.assertEqual(self.oPchRequestor.parseResponse(self.fakeResponsePLAYING).currentTime, 2341,"Should be 2341 seconds")
		self.assertEqual(self.oPchRequestor.parseResponse(self.fakeResponsePLAYING).percent, 42,"Should be 42%")
		self.assertEqual(self.oPchRequestor.parseResponse(self.fakeResponsePLAYING).fileName, "Home.(2009).1080p.mkv","Should be [Home.(2009).1080p.mkv]")
		self.assertEqual(self.oPchRequestor.parseResponse(self.fakeResponsePLAYING_BD).fileName, "Home","Should be [Home]")
		self.assertEqual(self.oPchRequestor.parseResponse(self.fakeResponsePLAYING_BD).percent, 15,"Should be 15%")
									
	def test_getStatus(self):
		self.assertEqual(self.oPchRequestor.getStatus("1.1.1.1",0.1).status, EnumStatus.UNKNOWN, "Should be UNKNOWN (cannot connect to pch)")
		
	def test_getStatusRemote(self):
		oStatus = self.oPchRequestor.getStatus("83.134.24.223",0.1)
		if(oStatus.status != EnumStatus.UNKNOWN):
			Debug(u"Remote PCH is [" + oStatus.status + "]")
			Debug(u"	FileName=" + oStatus.fileName)
			Debug(u"	CurrentTime=" + str(oStatus.currentTime) + "s")
			Debug(u"	TotalTime=" + str(oStatus.totalTime) + "s")
			Debug(u"	PercentTime=" + str(oStatus.percent) + "%")

class TestMediaParser(unittest.TestCase):

	def setUp(self):
		self.mediaparser = MediaParser()

	def test_TVShows(self):
		for (fileName,serie_name,season,episode_numbers) in TVShows:
			self.assertEqual(isinstance(self.mediaparser.parse(fileName),MediaParserResultTVShow),True)
			self.assertEqual(self.mediaparser.parse(fileName).series_name,serie_name)
			self.assertEqual(self.mediaparser.parse(fileName).season_number,season)
			self.assertEqual(self.mediaparser.parse(fileName).episode_numbers,episode_numbers)
			
	def test_Movies(self):
		for (fileName) in Movies:
			self.assertEqual(isinstance(self.mediaparser.parse(fileName),MediaParserResultMovie),True)
			#Debug("Title=" + self.mediaparser.parse(fileName).movie_title +" (" + str(self.mediaparser.parse(fileName).year + ") - IMDB=" + str(self.mediaparser.parse(fileName).imdbid)))

class TestTVDBAPIUsage(unittest.TestCase):
	
	def test_tvdb_api(self):
		tvdb = tvdb_api.Tvdb()
		for (fileName,serie_name,season,episode_numbers) in TVShows:
			serie_info = tvdb[serie_name]
			season_info = tvdb[serie_name][season]
			episode_info = tvdb[serie_name][season][episode_numbers[0]]
			#Debug("TvShow ID on tvdb = " + str(serie_info['id']))
			#Debug("FirstAired= " + str(serie_info['firstaired']))
			#Debug("Episode ID on tvdb = " + str(episode_info['id']))
		
if __name__ == '__main__':
    unittest.main()