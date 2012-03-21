import json

from lib.utilities import Debug
from urllib import quote
from urllib2 import urlopen
from xml.etree import ElementTree 
from hashlib import md5
from pchtrakt.config import *
from pchtrakt.exception import BetaSerieAuthenticationException

login = BetaSeriesUsername
pwdmd5 = md5(BetaSeriesPwd).hexdigest()

BETASERIE_API = 'C244D9326837'
BetaSerieUrl = 'http://api.betaseries.com/#path#?key={0}'.format(BETASERIE_API)

def getUrl(myPath):
    return BetaSerieUrl.replace('#path#', myPath)

def destroyToken(Token):
    url = getUrl('members/destroy.xml') + '&token={0}'.format(Token)
    oResponse = urlopen(url)
    oXml = ElementTree.XML(oResponse.read())
    if oXml.find('code').text == '1':
        return True
    else:
        return oXml.find('errors/error/content').text

def getSerieUrl(SerieName):
    quotedSerieName = quote(SerieName)
    url = getUrl('shows/search.json') + '&title={0}'.format(quotedSerieName)
    oResponse = urlopen(url)
    myJson = json.loads(oResponse.read())
    myKey= '0'
    for key, subdict in myJson['root']['shows'].iteritems():
        if (subdict['title'] == SerieName):
            myKey = key
            break
    myUrl = myJson['root']['shows'][myKey]['url']
    return quote('{0}.xml'.format(myUrl))

def getToken():
    url = (getUrl('members/auth.xml') 
                + '&login={0}&password={1}'.format(
                                                login,
                                                pwdmd5))
    oResponse = urlopen(url)
    oXml = ElementTree.XML(oResponse.read()) 
    if not oXml.find("member/token"):
        raise BetaSerieAuthenticationException('No token')
    return oXml.find("member/token").text
    
def scrobbleEpisode(SerieXml,Token,Saison,Episode):
    url = getUrl('members/watched/{0}'.format(SerieXml))
    url += '&season={0}&episode={1}&token={2}'.format(
                                                Saison,
                                                Episode,
                                                Token)
    oResponse = urlopen(url)
    oXml = ElementTree.XML(oResponse.read())
    
    if oXml.find("code").text == '1':
        return True
    else:
        return False 
        #todo(jlauwers) error message

def addShow(SerieXml,Token):
    url = getUrl('shows/add/{0}'.format(SerieXml)) + '&token={0}'.format(Token)
    oResponse = urlopen(url)
    oXml = ElementTree.XML(oResponse.read())
    if oXml.find("code").text == '1':
        return True
    else:
        return oXml.find("errors/error/content").text

def isEpisodeWatched(SerieXml,Token,Saison,Episode):
    url = getUrl('shows/episodes/{0}'.format(SerieXml))
    url += '&token={0}&season={1}&episode={2}'.format(Token,Saison,Episode)
    oResponse = urlopen(url)
    oXml = ElementTree.XML(oResponse.read())
    if oXml.find("seasons/season/episodes/episode/has_seen").text == '1':
        return True
    else:
        return False