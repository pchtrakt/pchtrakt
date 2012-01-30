from os.path import isfile
import ConfigParser
import logging

StopTrying = 0
oStatus = 0
stop = 0
currentPath = ''
currentTime = 0
watched = 0
DAEMON = 0
nbr = 0
config_file = 'pchtrakt.ini'
debug = True

logger = logging.getLogger('pchtrakt')
hdlr = logging.FileHandler('pchtrakt.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s\r')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.INFO)

def newConfig():
    config = ConfigParser.RawConfigParser()
    config.add_section('PCHtrakt')
    config.set('PCHtrakt', 'pch_ip', '127.0.0.1        ; do not change if installed directly on the popcorn')
    config.set('PCHtrakt', 'trakt_login', 'put_your_trakt.tv_login_here')
    config.set('PCHtrakt', 'trakt_pwd', 'put_your_trakt.tv_pwd_here')
    config.set('PCHtrakt', 'sleep_time', '8')
    config.set('PCHtrakt', 'refresh_time', '15')
    config.set('PCHtrakt', 'log_file', 'pchtrakt.log')
    # config.set('PCHtrakt', 'enable_movie_scrobbling', 'true')
    # config.set('PCHtrakt', 'enable_tvshow_scrobbling', 'true')
    
    with open(config_file, 'w') as configfile:
        config.write(configfile)

if isfile(config_file):
    pass
    #todo save config and create new one
else:
    newConfig()
