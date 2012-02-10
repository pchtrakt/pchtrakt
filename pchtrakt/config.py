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

#PchTrakt
config.read(pchtrakt.config_file)
ipPch = config.get('PCHtrakt', 'pch_ip') 
sleepTime = float(config.get('PCHtrakt', 'sleep_time'))

#Trakt
TraktUsername = config.get('Trakt', 'login') 
TraktPwd = config.get('Trakt', 'password') 
TraktScrobbleTvShow = config.get('Trakt', 'enable_tvshow_scrobbling') 
TraktScrobbleMovie = config.get('Trakt', 'enable_movie_scrobbling') 
TraktRefreshTime = config.get('Trakt', 'refresh_time')

# Betaseries
BetaSeriesUsername = config.get('BetaSeries', 'login') 
BetaSeriesPwd = config.get('BetaSeries', 'password') 
BetaSeriesScrobbleTvShow = config.get('BetaSeries', 'enable_tvshow_scrobbling') 

pathYAMJ='' #not used yet
