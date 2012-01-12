from xml.etree import ElementTree 
from string import split
#from yamjParse import *
from os import listdir
from urllib import urlopen
from utilities import Debug

pathYAMJ='/media/raid5/Video/Yamj/Jukebox/'

class EnumStatus:
	NOPLAY='noplay'
	PLAY='play'
	PAUSE='pause'
	LOAD='buffering'
	STOP='stop'
	UNKNOWN='unknown'
class PchRequest:
	def __init__(self,ipPch):
		oStream = urlopen("http://" + ipPch + ":8008/playback?arg0=get_current_vod_info")
		self.oXml = ElementTree.parse(oStream).getroot()
		#print self.oXml.getElementsByTagName('theDavidBox')[0].getElementsByTagName('response')[0].getElementsByTagName('fullPath')[0].firstChild.data
		
		if self.oXml.findall('returnValue')[0].text == '1':
			self.status=EnumStatus.NOPLAY
		else:
			self.status = self.oXml.findall('response/currentStatus')[0].text
			self.path = self.oXml.findall('response/fullPath')[0].text
			self.currentTime = int(self.oXml.findall('response/currentTime')[0].text)
			self.totalTime = int(self.oXml.findall('response/totalTime')[0].text)
			
			nameSplited = self.path.split('/')[::-1][0].strip()
			
			#if tvserie
			
			#si seriexepisode  !!! double episode???
			self.name = nameSplited.split('-')[0].strip()
			self.title = nameSplited.split('-')[::-1][0].replace('.mkv','').strip()
			#si SxE!!! S01E01!!!
			self.SxE = nameSplited.split('-')[1].strip()
			self.season = self.SxE.split('x')[0].strip()
			
			if len(self.SxE.split('x'))==2:
				self.episode = self.SxE.split('x')[::-1][0].strip()
			else:
				self.episode = self.SxE.split('x')[::-1][0].strip()
				self.episode2 = self.SxE.split('x')[::-1][1].strip()
			if self.totalTime!=0:
				self.percent = int((float(self.currentTime) / float(self.totalTime)) * 100)
			else:
				self.percent = 0
			def isRelatedXml(n):
				return n.count('.xml')>=1 and n.count(self.name)>=1 and n.count(self.season + 'x')>=1 
	
			dirList=listdir(pathYAMJ)

			Debug(filter(isRelatedXml, dirList)[0])
			
			#reqYamj = yamjParse(pathYAMJ+filter(isRelatedXml, dirList)[0])
			#self.year = reqYamj.year
			#self.theTvDb = reqYamj.theTvDb
		
