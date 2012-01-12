from elementtree.ElementTree import parse

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
