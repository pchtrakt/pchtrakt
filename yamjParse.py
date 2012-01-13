from xml.etree import ElementTree 

class yamjParse:
	def __init__(self,xml):
		self.oXml = parse(xml).getroot()
		self.year = self.oXml.findall('movie/year')[0].text
		TvOrMovie = self.oXml.findall('movie/id')
		for node in TvOrMovie:
			print node.attrib['moviedb'] + ': ' + node.text
			if node.attrib['moviedb'] == 'thetvdb':
				self.theTvDb = node.text
			if node.attrib['moviedb'] == 'imdb':
				self.imdb = node.text

				
		"""
		nameSplited = self.path.split('/')[::-1][0].strip()
		if tvserie
		si seriexepisode  !!! double episode???
			self.name = nameSplited.split('-')[0].strip()
			self.title = nameSplited.split('-')[::-1][0].replace('.mkv','').strip()
		si SxE!!! S01E01!!!
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
		"""