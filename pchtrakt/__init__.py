from os.path import isfile
import ConfigParser

StopTrying = 0
oStatus = 0
stop = 0
currentPath = ''
currentTime = 0
watched = 0
DAEMON = 0
nbr = 0
config_file = 'pchtrakt.ini'

def newConfig():
	config = ConfigParser.RawConfigParser()
	config.add_section('PCHtrakt')
	config.set('PCHtrakt', 'pch_ip', '127.0.0.1 ; do not change if installed directly on the popcorn')
	config.set('PCHtrakt', 'trakt_login', 'put_your_trakt.tv_login_here')
	config.set('PCHtrakt', 'trakt_pwd', 'put_your_trakt.tv_pwd_here')
	config.set('PCHtrakt', 'sleep_time', '8')
	config.set('PCHtrakt', 'refresh_time', '15')
	# config.set('PCHtrakt', 'enable_movie_scrobbling', 'true')
	# config.set('PCHtrakt', 'enable_tvshow_scrobbling', 'true')
	
	with open(config_file, 'w') as configfile:
		config.write(configfile)

if not isfile(config_file):
	newConfig()