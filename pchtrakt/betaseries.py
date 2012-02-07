from urllib import quote
from urllib2 import Request, urlopen, URLError, HTTPError
from xml.etree import ElementTree 
from HTMLParser import HTMLParser
from hashlib import md5

BETASERIE_URL = 'http://api.betaseries.com'
BETASERIE_API = 'C244D9326837'

LOGIN = 'Dev023'
PASS = 'developer'

def destroyToken(Token):
    url = '{0}/members/destroy.xml?key={1}&token={2}'.format(
                        BETASERIE_URL,
                        BETASERIE_API,
                        Token)
    oResponse = urlopen(url)
    oXml = ElementTree.XML(oResponse.read())
    if oXml.find('code').text == '1':
        return True
    else:
        return oXml.find('errors/error/content').text

def getSerieUrl(SerieName):
    SerieName = quote(SerieName)
    url = '{0}/shows/search.xml?key={1}&title={2}'.format(
                        BETASERIE_URL,
                        BETASERIE_API,
                        SerieName)
    oResponse = urlopen(url)
    oXml = ElementTree.XML(oResponse.read()) 
    return quote('{0}.xml'.format(oXml.find("shows/show/title").text))

def userAuth(l,p):
    url = '{0}/members/auth.xml?key={1}&login={2}&password={3}'.format(
                        BETASERIE_URL,
                        BETASERIE_API,
                        l,
                        md5(p).hexdigest())
    oResponse = urlopen(url)
    oXml = ElementTree.XML(oResponse.read()) 
    return oXml.find("member/token").text
    
def scrobbleEpisode(SerieXml,Token,Saison,Episode):
    #todo(jlauwers) check before if this episode is already seen.
    url = '{0}/members/watched/{1}?key={2}&season={3}&episode={4}&token={5}'.format(
                        BETASERIE_URL,
                        SerieXml,
                        BETASERIE_API,
                        Saison,
                        Episode,
                        Token)
    oResponse = urlopen(url)
    oXml = ElementTree.XML(oResponse.read())
    if oXml.find("code").text:
        return True
    else:
        pass
        #todo(jlauwers) this user don't watch this show

def addShow(SerieXml,Token):
    url = '{0}/shows/add/{1}?key={2}&token={3}'.format(
                        BETASERIE_URL,
                        SerieXml,
                        BETASERIE_API,
                        Token)
    oResponse = urlopen(url)
    oXml = ElementTree.XML(oResponse.read())
    if oXml.find("code"):
        return True
    else:
        return oXml.find("errors/error/content").text
        
SerieXml = getSerieUrl('Sherlock')
print SerieXml
userToken = userAuth(LOGIN,PASS)
print userToken
# print addShow(SerieXml,userToken)
print scrobbleEpisode(SerieXml,userToken,2,1)
destroyToken(userToken)