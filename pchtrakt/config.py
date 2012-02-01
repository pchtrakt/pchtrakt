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
import ConfigParser
import pchtrakt
config = ConfigParser.RawConfigParser()

config.read(pchtrakt.config_file)
ipPch = config.get('PCHtrakt', 'pch_ip') 
username = config.get('PCHtrakt', 'trakt_login') 
pwd = config.get('PCHtrakt', 'trakt_pwd') 
scrobbleTvShow = config.get('PCHtrakt', 'enable_tvshow_scrobbling') 
scrobbleMovie = config.get('PCHtrakt', 'enable_movie_scrobbling') 
sleepTime = float(config.get('PCHtrakt', 'sleep_time'))
refreshTime = config.get('PCHtrakt', 'refresh_time')

pathYAMJ='' #not used yet
