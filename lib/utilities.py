# -*- coding: utf-8 -*-
# From https://github.com/Manromen/script.TraktUtilities

import os, sys
import time, socket
from pchtrakt.config import *
import pchtrakt
try: import simplejson as json
except ImportError: import json

from nbhttpconnection import *
from hashlib import sha1
import urllib, re

try:
    # Python 3.0 +
    import http.client as httplib
except ImportError:
    # Python 2.7 and earlier
    import httplib
  
__author__ = "Ralph-Gordon Paul, Adrian Cowan"
__credits__ = ["Ralph-Gordon Paul", "Adrian Cowan", "Justin Nemeth",  "Sean Rudford"]
__license__ = "GPL"
__maintainer__ = "Ralph-Gordon Paul"
__email__ = "ralph-gordon.paul@uni-duesseldorf.de"
__status__ = "Production"

username = TraktUsername
apikey = 'def6943c09e19dccb4df715bd4c9c6c74bc3b6d7'
pwdsha1 = sha1(TraktPwd).hexdigest()

headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}

class TraktError(Exception):
    pass
class AuthenticationTraktError(TraktError):
    def __init__(self):
        Exception.__init__(self, 'Trakt.tv - Login or password incorrect')
class MaxScrobbleError(TraktError):
	def __init__(self):
		Exception.__init__(self, 'Trakt.tv - Shows per hour limit reached')

def Debug(msg, force=False):
    myMsg = unicode(msg)
    if (pchtrakt.debug or force):
        try:
            print myMsg
        except UnicodeEncodeError:
            print myMsg.encode( "utf-8", "replace" )

def checkSettings(daemon=False):
    if username != 'your_trakt_login':
        data = traktJsonRequest('POST', '/account/test/%%API_KEY%%', silent=True)
        if data == None: #Incorrect trakt login details
            return False
        print('True')  
        return True

# SQL string quote escaper
def xcp(s):
    return re.sub('''(['])''', r"''", str(s))

# get a connection to trakt
def getTraktConnection():
    try:
        conn = NBHTTPConnection('api.trakt.tv')
    except socket.timeout:
        Debug("getTraktConnection: can't connect to trakt - timeout")
        # notification("Trakt Utilities", __language__(1108).encode( "utf-8", "ignore" ) + ": timeout") # can't connect to trakt
        return None
    return conn
    
# make a JSON api request to trakt
# method: http method (GET or POST)
# req: REST request (ie '/user/library/movies/all.json/%%API_KEY%%/%%USERNAME%%')
# args: arguments to be passed by POST JSON (only applicable to POST requests), default:{}
# returnStatus: when unset or set to false the function returns None apon error and shows a notification,
#   when set to true the function returns the status and errors in ['error'] as given to it and doesn't show the notification,
#   use to customise error notifications
# anon: anonymous (dont send username/password), default:False
# connection: default it to make a new connection but if you want to keep the same one alive pass it here
# silent: default is False, when true it disable any error notifications (but not debug messages)
# passVersions: default is False, when true it passes extra version information to trakt to help debug problems
def traktJsonRequest(method, req, args={}, returnStatus=False, anon=False, conn=False, silent=False, passVersions=False):
    closeConnection = False
    if not conn:
        conn = getTraktConnection()
        closeConnection = True
    if conn == None:
        if returnStatus:
            data = {}
            data['status'] = 'failure'
            data['error'] = 'Unable to connect to trakt'
            return data
        return None

    try:
        req = req.replace("%%API_KEY%%",apikey)
        req = req.replace("%%USERNAME%%",username)
        if method == 'POST':
            if not anon:
                args['username'] = username
                args['password'] = pwdsha1
            if passVersions:
                args['plugin_version'] = 0 #__settings__.getAddonInfo("version")
                args['media_center'] = 'popcorn hour' #Todo get pch version
                args['media_center_version'] = 0 
                args['media_center_date'] = '10/01/2012' 
            jdata = json.dumps(args)
            conn.request('POST', req, jdata)
        elif method == 'GET':
            conn.request('GET', req)
        else:
            return None
        # print "trakt json url: "+req
        # print "json: " + jdata
    except socket.error:
        Debug("traktQuery: can't connect to trakt")
        # if not silent: notification("Trakt Utilities", __language__(1108).encode( "utf-8", "ignore" )) # can't connect to trakt
        if returnStatus:
            data = {}
            data['status'] = 'failure'
            data['error'] = 'Socket error, unable to connect to trakt'
            return data;
        return None
     
    conn.go()
    
    while True:
        if conn.hasResult():
            if closeConnection:
                conn.close()
            break
        time.sleep(1)
    
    response = conn.getResult()
    if closeConnection:
        conn.close()
    
    try:
        raw = response.read()
        data = json.loads(raw)
    except ValueError:
        Debug("traktQuery: Bad JSON responce: "+raw)
        if returnStatus:
            data = {}
            data['status'] = 'failure'
            data['error'] = 'Bad responce from trakt'
            return data
        # if not silent: notification("Trakt Utilities", __language__(1109).encode( "utf-8", "ignore" ) + ": Bad responce from trakt") # Error
        return None

    if 'status' in data:
        if data['status'] == 'failure':
            print "traktQuery: Error: " + str(data['error'])
            if data['error'] == 'failed authentication':
                raise AuthenticationTraktError()
            if data['error'] == 'shows per hour limit reached':
                raise MaxScrobbleError()
            if returnStatus:
                return data;
            #if not silent: notification("Trakt Utilities", __language__(1109).encode( "utf-8", "ignore" ) + ": " + str(data['error'])) # Error
            return None
    
    return data
   
# get movies from trakt server
def getMoviesFromTrakt(daemon=False):
    data = traktJsonRequest('POST', '/user/library/movies/all.json/%%API_KEY%%/%%USERNAME%%')
    if data == None:
        Debug("Error in request from 'getMoviesFromTrakt()'")
    return data

# get movie that are listed as in the users collection from trakt server
def getMovieCollectionFromTrakt(daemon=False):
    data = traktJsonRequest('POST', '/user/library/movies/collection.json/%%API_KEY%%/%%USERNAME%%')
    if data == None:
        Debug("Error in request from 'getMovieCollectionFromTrakt()'")
    return data

# get easy access to movie by imdb_id
def traktMovieListByImdbID(data):
    trakt_movies = {}

    for i in range(0, len(data)):
        if data[i]['imdb_id'] == "": continue
        trakt_movies[data[i]['imdb_id']] = data[i]
        
    return trakt_movies

# get easy access to tvshow by tvdb_id
def traktShowListByTvdbID(data):
    trakt_tvshows = {}

    for i in range(0, len(data)):
        trakt_tvshows[data[i]['tvdb_id']] = data[i]
        
    return trakt_tvshows

# get seen tvshows from trakt server
def getWatchedTVShowsFromTrakt(daemon=False):
    data = traktJsonRequest('POST', '/user/library/shows/watched.json/%%API_KEY%%/%%USERNAME%%')
    if data == None:
        Debug("Error in request from 'getWatchedTVShowsFromTrakt()'")
    return data

# set episodes seen on trakt
def setEpisodesSeenOnTrakt(tvdb_id, title, year, episodes):
    data = traktJsonRequest('POST', '/show/episode/seen/%%API_KEY%%', {'tvdb_id': tvdb_id, 'title': title, 'year': year, 'episodes': episodes})
    if data == None:
        Debug("Error in request from 'setEpisodeSeenOnTrakt()'")
    return data

# set episodes in library on trakt
def setEpisodesInLibraryOnTrakt(tvdb_id, title, year, episodes):
    data = traktJsonRequest('POST', '/show/episode/library/%%API_KEY%%', {'tvdb_id': tvdb_id, 'title': title, 'year': year, 'episodes': episodes})
    if data == None:
        Debug("Error in request from 'setEpisodesInLibraryOnTrakt()'")
    return data    
    
# set episodes unseen on trakt
def setEpisodesUnseenOnTrakt(tvdb_id, title, year, episodes):
    data = traktJsonRequest('POST', '/show/episode/unseen/%%API_KEY%%', {'tvdb_id': tvdb_id, 'title': title, 'year': year, 'episodes': episodes})
    if data == None:
        Debug("Error in request from 'setEpisodesUnseenOnTrakt()'")
    return data

# set movies seen on trakt
#  - movies, required fields are 'plays', 'last_played' and 'title', 'year' or optionally 'imdb_id'
def setMoviesSeenOnTrakt(movies):
    data = traktJsonRequest('POST', '/movie/seen/%%API_KEY%%', {'movies': movies})
    if data == None:
        Debug("Error in request from 'setMoviesSeenOnTrakt()'")
    return data

# set movies unseen on trakt
#  - movies, required fields are 'plays', 'last_played' and 'title', 'year' or optionally 'imdb_id'
def setMoviesUnseenOnTrakt(movies):
    data = traktJsonRequest('POST', '/movie/unseen/%%API_KEY%%', {'movies': movies})
    if data == None:
        Debug("Error in request from 'setMoviesUnseenOnTrakt()'")
    return data

# get tvshow collection from trakt server
def getTVShowCollectionFromTrakt(daemon=False):
    data = traktJsonRequest('POST', '/user/library/shows/collection.json/%%API_KEY%%/%%USERNAME%%')
    if data == None:
        Debug("Error in request from 'getTVShowCollectionFromTrakt()'")
    return data
    
# returns list of movies from watchlist
def getWatchlistMoviesFromTrakt():
    data = traktJsonRequest('POST', '/user/watchlist/movies.json/%%API_KEY%%/%%USERNAME%%')
    if data == None:
        Debug("Error in request from 'getWatchlistMoviesFromTrakt()'")
    return data

# returns list of tv shows from watchlist
def getWatchlistTVShowsFromTrakt():
    data = traktJsonRequest('POST', '/user/watchlist/shows.json/%%API_KEY%%/%%USERNAME%%')
    if data == None:
        Debug("Error in request from 'getWatchlistTVShowsFromTrakt()'")
    return data

# add an array of movies to the watch-list
def addMoviesToWatchlist(data):
    movies = []
    for item in data:
        movie = {}
        if "imdb_id" in item:
            movie["imdb_id"] = item["imdb_id"]
        if "tmdb_id" in item:
            movie["tmdb_id"] = item["tmdb_id"]
        if "title" in item:
            movie["title"] = item["title"]
        if "year" in item:
            movie["year"] = item["year"]
        movies.append(movie)
    
    data = traktJsonRequest('POST', '/movie/watchlist/%%API_KEY%%', {"movies":movies})
    if data == None:
        Debug("Error in request from 'addMoviesToWatchlist()'")
    return data

# remove an array of movies from the watch-list
def removeMoviesFromWatchlist(data):
    movies = []
    for item in data:
        movie = {}
        if "imdb_id" in item:
            movie["imdb_id"] = item["imdb_id"]
        if "tmdb_id" in item:
            movie["tmdb_id"] = item["tmdb_id"]
        if "title" in item:
            movie["title"] = item["title"]
        if "year" in item:
            movie["year"] = item["year"]
        movies.append(movie)
    
    data = traktJsonRequest('POST', '/movie/unwatchlist/%%API_KEY%%', {"movies":movies})
    if data == None:
        Debug("Error in request from 'removeMoviesFromWatchlist()'")
    return data

# add an array of tv shows to the watch-list
def addTVShowsToWatchlist(data):
    shows = []
    for item in data:
        show = {}
        if "tvdb_id" in item:
            show["tvdb_id"] = item["tvdb_id"]
        if "imdb_id" in item:
            show["tmdb_id"] = item["imdb_id"]
        if "title" in item:
            show["title"] = item["title"]
        if "year" in item:
            show["year"] = item["year"]
        shows.append(show)
    
    data = traktJsonRequest('POST', '/show/watchlist/%%API_KEY%%', {"shows":shows})
    if data == None:
        Debug("Error in request from 'addMoviesToWatchlist()'")
    return data

# remove an array of tv shows from the watch-list
def removeTVShowsFromWatchlist(data):
    shows = []
    for item in data:
        show = {}
        if "tvdb_id" in item:
            show["tvdb_id"] = item["tvdb_id"]
        if "imdb_id" in item:
            show["imdb_id"] = item["imdb_id"]
        if "title" in item:
            show["title"] = item["title"]
        if "year" in item:
            show["year"] = item["year"]
        shows.append(show)
    
    data = traktJsonRequest('POST', '/show/unwatchlist/%%API_KEY%%', {"shows":shows})
    if data == None:
        Debug("Error in request from 'removeMoviesFromWatchlist()'")
    return data

#Set the rating for a movie on trakt, rating: "hate" = Weak sauce, "love" = Totaly ninja
def rateMovieOnTrakt(imdbid, title, year, rating):
    if not (rating in ("love", "hate", "unrate")):
        #add error message
        return
    
    Debug("Rating movie:" + rating)
    
    data = traktJsonRequest('POST', '/rate/movie/%%API_KEY%%', {'imdb_id': imdbid, 'title': title, 'year': year, 'rating': rating})
    if data == None:
        Debug("Error in request from 'rateMovieOnTrakt()'")
    
    # if (rating == "unrate"):
        # notification("Trakt Utilities", __language__(1166).encode( "utf-8", "ignore" )) # Rating removed successfully
    # else :
        # notification("Trakt Utilities", __language__(1167).encode( "utf-8", "ignore" )) # Rating submitted successfully
    
    return data

#Get the rating for a movie from trakt
def getMovieRatingFromTrakt(imdbid, title, year):
    if imdbid == "" or imdbid == None:
        return None #would be nice to be smarter in this situation
    
    data = traktJsonRequest('POST', '/movie/summary.json/%%API_KEY%%/'+str(imdbid))
    if data == None:
        Debug("Error in request from 'getMovieRatingFromTrakt()'")
        return None
        
    if 'rating' in data:
        return data['rating']
        
    print data
    Debug("Error in request from 'getMovieRatingFromTrakt()'")
    return None

#Set the rating for a tv episode on trakt, rating: "hate" = Weak sauce, "love" = Totaly ninja
def rateEpisodeOnTrakt(tvdbid, title, year, season, episode, rating):
    if not (rating in ("love", "hate", "unrate")):
        #add error message
        return
    
    Debug("Rating episode:" + rating)
    
    data = traktJsonRequest('POST', '/rate/episode/%%API_KEY%%', {'tvdb_id': tvdbid, 'title': title, 'year': year, 'season': season, 'episode': episode, 'rating': rating})
    if data == None:
        Debug("Error in request from 'rateEpisodeOnTrakt()'")
    
    # if (rating == "unrate"):
        # notification("Trakt Utilities", __language__(1166).encode( "utf-8", "ignore" )) # Rating removed successfully
    # else :
        # notification("Trakt Utilities", __language__(1167).encode( "utf-8", "ignore" )) # Rating submitted successfully
    
    return data
    
#Get the rating for a tv episode from trakt
def getEpisodeRatingFromTrakt(tvdbid, title, year, season, episode):
    if tvdbid == "" or tvdbid == None:
        return None #would be nice to be smarter in this situation
    
    data = traktJsonRequest('POST', '/show/episode/summary.json/%%API_KEY%%/'+str(tvdbid)+"/"+season+"/"+episode)
    if data == None:
        Debug("Error in request from 'getEpisodeRatingFromTrakt()'")
        return None
        
    if 'rating' in data:
        return data['rating']
        
    print data
    Debug("Error in request from 'getEpisodeRatingFromTrakt()'")
    return None

#Set the rating for a tv show on trakt, rating: "hate" = Weak sauce, "love" = Totaly ninja
def rateShowOnTrakt(tvdbid, title, year, rating):
    if not (rating in ("love", "hate", "unrate")):
        #add error message
        return
    
    Debug("Rating show:" + rating)
    
    data = traktJsonRequest('POST', '/rate/show/%%API_KEY%%', {'tvdb_id': tvdbid, 'title': title, 'year': year, 'rating': rating})
    if data == None:
        Debug("Error in request from 'rateShowOnTrakt()'")
    
    # if (rating == "unrate"):
        # notification("Trakt Utilities", __language__(1166).encode( "utf-8", "ignore" )) # Rating removed successfully
    # else :
        # notification("Trakt Utilities", __language__(1167).encode( "utf-8", "ignore" )) # Rating submitted successfully
    
    return data

#Get the rating for a tv show from trakt
def getShowRatingFromTrakt(tvdbid, title, year):
    if tvdbid == "" or tvdbid == None:
        return None #would be nice to be smarter in this situation
    
    data = traktJsonRequest('POST', '/show/summary.json/%%API_KEY%%/'+str(tvdbid))
    if data == None:
        Debug("Error in request from 'getShowRatingFromTrakt()'")
        return None
        
    if 'rating' in data:
        return data['rating']
        
    print data
    Debug("Error in request from 'getShowRatingFromTrakt()'")
    return None

def getRecommendedMoviesFromTrakt():
    data = traktJsonRequest('POST', '/recommendations/movies/%%API_KEY%%')
    if data == None:
        Debug("Error in request from 'getRecommendedMoviesFromTrakt()'")
    return data

def getRecommendedTVShowsFromTrakt():
    data = traktJsonRequest('POST', '/recommendations/shows/%%API_KEY%%')
    if data == None:
        Debug("Error in request from 'getRecommendedTVShowsFromTrakt()'")
    return data

def getTrendingMoviesFromTrakt():
    data = traktJsonRequest('GET', '/movies/trending.json/%%API_KEY%%')
    if data == None:
        Debug("Error in request from 'getTrendingMoviesFromTrakt()'")
    return data

def getTrendingTVShowsFromTrakt():
    data = traktJsonRequest('GET', '/shows/trending.json/%%API_KEY%%')
    if data == None:
        Debug("Error in request from 'getTrendingTVShowsFromTrakt()'")
    return data

def getFriendsFromTrakt():
    data = traktJsonRequest('POST', '/user/friends.json/%%API_KEY%%/%%USERNAME%%')
    if data == None:
        Debug("Error in request from 'getFriendsFromTrakt()'")
    return data

def getWatchingFromTraktForUser(name):
    data = traktJsonRequest('POST', '/user/watching.json/%%API_KEY%%/%%USERNAME%%')
    if data == None:
        Debug("Error in request from 'getWatchingFromTraktForUser()'")
    return data

###############################
##### Scrobbling to trakt #####
###############################

#tell trakt that the user is watching a movie
def watchingMovieOnTrakt(imdb_id, title, year, duration, percent):
    responce = traktJsonRequest('POST', '/movie/watching/%%API_KEY%%', {'imdb_id': imdb_id, 'title': title, 'year': year, 'duration': duration, 'progress': percent}, passVersions=True)
    if responce == None:
        Debug("Error in request from 'watchingMovieOnTrakt()'")
    return responce

#tell trakt that the user is watching an episode
def watchingEpisodeOnTrakt(tvdb_id, title, year, season, episode, duration, percent):
    responce = traktJsonRequest('POST', '/show/watching/%%API_KEY%%', {'tvdb_id': tvdb_id, 'title': title, 'year': year, 'season': season, 'episode': episode, 'duration': duration, 'progress': percent}, passVersions=True)
    if responce == None:
        print "Error in request from 'watchingEpisodeOnTrakt()'"
    return responce

#tell trakt that the user has stopped watching a movie
def cancelWatchingMovieOnTrakt():
    responce = traktJsonRequest('POST', '/movie/cancelwatching/%%API_KEY%%')
    if responce == None:
        Debug("Error in request from 'cancelWatchingMovieOnTrakt()'")
    return responce

#tell trakt that the user has stopped an episode
def cancelWatchingEpisodeOnTrakt():
    responce = traktJsonRequest('POST', '/show/cancelwatching/%%API_KEY%%')
    if responce == None:
        Debug("Error in request from 'cancelWatchingEpisodeOnTrakt()'")
    return responce

#tell trakt that the user has finished watching an movie
def scrobbleMovieOnTrakt(imdb_id, title, year, duration, percent):
    responce = traktJsonRequest('POST', '/movie/scrobble/%%API_KEY%%', {'imdb_id': imdb_id, 'title': title, 'year': year, 'duration': duration, 'progress': percent}, passVersions=True)
    if responce == None:
        Debug("Error in request from 'scrobbleMovieOnTrakt()'")
    return responce

#tell trakt that the user has finished watching an episode
def scrobbleEpisodeOnTrakt(tvdb_id, title, year, season, episode, duration, percent):
    responce = traktJsonRequest('POST', '/show/scrobble/%%API_KEY%%', {'tvdb_id': tvdb_id, 'title': title, 'year': year, 'season': season, 'episode': episode, 'duration': duration, 'progress': percent}, passVersions=True)
    if responce == None:
        Debug("Error in request from 'scrobbleEpisodeOnTrakt()'")
    return responce

            
            
"""
ToDo:


"""


"""
for later:
First call "Player.GetActivePlayers" to determine the currently active player (audio, video or picture).
If it is audio or video call Audio/VideoPlaylist.GetItems and read the "current" field to get the position of the
currently playling item in the playlist. The "items" field contains an array of all items in the playlist and "items[current]" is
the currently playing file. You can also tell jsonrpc which fields to return for every item in the playlist and therefore you'll have all the information you need.

"""
