from os.path import isfile
import ConfigParser
import logging

StopTrying = 0
stop = 0
lastPath = ''
currentTime = 0
watched = 0
DAEMON = 0
nbr = 0
config_file = 'pchtrakt.ini'
debug = True
isTvShow = 0
isMovie = 0
idOK = 0
allowedPauseTime = 0

logger = logging.getLogger('pchtrakt')
hdlr = logging.FileHandler('pchtrakt.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s\r')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.INFO)
config = ConfigParser.RawConfigParser()

def loadOldConfig():
    config.read(config_file)

def newConfig():
    if not isfile(config_file):
        config.add_section('PCHtrakt')
    if not config.has_option('PCHtrakt','pch_ip'):
        config.set('PCHtrakt', 'pch_ip', '127.0.0.1        ; do not change if installed directly on the popcorn')
    if not config.has_option('PCHtrakt','sleep_time'):
        config.set('PCHtrakt', 'sleep_time', '5')
    if not config.has_option('PCHtrakt','log_file'):
        config.set('PCHtrakt', 'log_file', 'pchtrakt.log')
    if not config.has_option('PCHtrakt','ignored_repertory'):
        config.set('PCHtrakt', 'ignored_repertory', '')
    
    if not config.has_section('Trakt'):
        config.add_section('Trakt')
    if not config.has_option('Trakt','enable_movie_scrobbling'):
        config.set('Trakt', 'enable_movie_scrobbling', True)
    if not config.has_option('Trakt','enable_tvshow_scrobbling'):
        config.set('Trakt', 'enable_tvshow_scrobbling', True)      
    if not config.has_option('Trakt','login'):
        config.set('Trakt', 'login', 'your_trakt_login')
    if not config.has_option('Trakt','password'):
        config.set('Trakt', 'password', 'your_password')
    if not config.has_option('Trakt','refresh_time'):
        config.set('Trakt', 'refresh_time', '15')
        
    if not config.has_section('BetaSeries'):
        config.add_section('BetaSeries')
    if not config.has_option('BetaSeries','enable_tvshow_scrobbling'):
        config.set('BetaSeries', 'enable_tvshow_scrobbling', False)   
    if not config.has_option('BetaSeries','login'):
        config.set('BetaSeries', 'login', 'your_login')
    if not config.has_option('BetaSeries','password'):
        config.set('BetaSeries', 'password', 'your_password')
        
    if not config.has_section('YAMJ'):
        config.add_section('YAMJ')
    if not config.has_option('YAMJ','watched'):
        config.set('YAMJ', 'watched', False)
    if not config.has_option('YAMJ','watched_path'):
        config.set('YAMJ', 'watched_path', '')
    if not config.has_option('YAMJ','watched_with_video'):
        config.set('YAMJ', 'watched_with_video', True)
    if not config.has_option('YAMJ','ignored_category'):
        config.set('YAMJ', 'ignored_category', '')
    if not config.has_option('YAMJ','path'):
        config.set('YAMJ', 'path', '')
        
    with open(config_file, 'w') as configfile:
        config.write(configfile)

if isfile(config_file):
    loadOldConfig()
newConfig()
