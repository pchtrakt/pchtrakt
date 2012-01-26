from os.path import isfile

StopTrying = 0
oStatus = 0
stop = 0
currentPath = ''
currentTime = 0
watched = 0
DAEMON = 0
nbr = 0
config_file = 'config.ini'

def newConfig():
	config.add_section('PCHtrakt')
	config.set('PCHtrakt', 'pch_ip', '127.0.0.1')
	config.set('PCHtrakt', 'tratk.tv_login', 'put_your_trakt.tv_login_here')
	config.set('PCHtrakt', 'tratk.tv_pwd', 'put_your_trakt.tv_pwd_here')
	config.set('PCHtrakt', 'enable_movie_scrobbling', 'true')
	config.set('PCHtrakt', 'enable_tvshow_scrobbling', 'true')

if not isfile(config_file):
	