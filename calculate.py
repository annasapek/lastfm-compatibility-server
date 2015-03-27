from requests import get
import json, operator
from config import LASTFM_API_KEY

URL = 'http://ws.audioscrobbler.com/2.0/'
ARTIST_API_CALL = URL + '?method=user.gettopartists&user=%s&api_key=%s&format=json&period=%s'
ALBUM_API_CALL = URL + '?method=user.gettopalbums&user=%s&api_key=%s&format=json&period=%s'
ERROR_USER = '%s is not a valid Last.fm username.'

def get_score(me, friend):
	""" Returns a music compatibility score and a list of common artists in JSON for
		the two given Last.fm usernames.
	"""
	
	result = {'status' : 0, 'user_1': me, 'user_2': friend}
	period = '1month'
	
	# artist compatability
	artists = get_artist_score(me, friend, period)
	if artists['status'] != 0:
		result['status'] = artists['status']
		result['error_messages'] = artists['error_messages']
		return result
	result['artists'] = artists['artists']
	
	# album compatibility
	albums = get_album_score(me, friend, period)
	if albums['status'] != 0:
		result['status'] = albums['status']
		result['error_messages'] = albums['error_messages']
		return result
	result['albums'] = albums['albums']
	
	# final result
	return result

def get_artist_score(me, friend, period):
	""" Returns a dictionary containing an artist compatibility score and a list of
		top common artists for the given users. The result will also contain a
		status code indicating success of the response (0=success, 1=failure), 
		and a list of error messages upon failure.
	"""
	
	result = {'status' : 0, 'user_1': me, 'user_2': friend, 'artists': {}}
	data = {me: api_call_artists(me, period), friend: api_call_artists(friend, period)}
	
	# check for errors
	errors = check_json_response(data)
	if errors:
		result['error_messages'] = []
		result['status'] = 1
		for name in errors:
			result['error_messages'].append(ERROR_USER % name)
		return result
		
	# dictionaries from artist to {rank, image}
	my_artists = get_artist_dictionary(data[me])
	friend_artists = get_artist_dictionary(data[friend])
	
	# min_length = n + 1, so (min_length - rank) ranges from 1 to n
	min_length = min(len(my_artists), len(friend_artists)) + 1	
	
	# (n + 1)(n) 
	max = min_length * (min_length - 1)
	
	# common artists, a dictionary, {score: {name, image}}
	common_artists = {}
	
	# topartists, a list of dictionaries, [{name, image}]
	result['artists']['top'] = []
	
	# compute a cumulative score for each shared artist
	for artist, data in my_artists.iteritems():
		
		# check if the other user also listens to this artist
		if artist in friend_artists.iterkeys():
			my_score = min_length - int(data['rank'])
			friend_score = min_length - int(friend_artists[artist]['rank'])
			sum_score = my_score + friend_score
			common_artists[sum_score] = {'name': artist, 'image': data['image'], 'url': data['url']}
			#score += sum_score
	
	# cumulative score
	result['artists']['score'] = (100 * sum(x for x in common_artists.iterkeys())) / max
	
	# sort the common artists based on the cumulative score
	result['artists']['top'] = [v for (k, v) \
		in sorted(common_artists.items(), reverse=True)][0:10]
	
	return result

def get_album_score(me, friend, period):
	""" Returns a dictionary containing an album compatibility score and a list of 
		common albums for the given users. The result will also contain a
		status code indicating success of the response (0=success, 1=failure), 
		and a list of error messages upon failure.
	"""
	
	result = {'status': 0, 'user_1': me, 'user_2': friend, 'albums': {}}
	data = {me: api_call_albums(me, period), friend: api_call_albums(friend, period)}
	
	# check for errors
	errors	 = check_json_response(data)
	if errors:
		result['status'] = 1
		result['error_messages'] = []
		for error in errors:
			result['error_messages'].append(ERROR_USER % error)
		return result

	result['user_1'] = me
	result['user_2'] = friend
	
	my_albums = get_album_dictionary(data[me])
	friend_albums = get_album_dictionary(data[friend])
	
	min_length = min(len(my_albums), len(friend_albums)) + 1
	max = (min_length) * (min_length - 1)
	
	# dict of albums, {score: {name, artist, image}}
	common_albums = {}
	
	# list of top albums, [{name, artist, image}]
	result['albums']['top'] = []
	
	for album, info in my_albums.iteritems():
		if album in friend_albums.iterkeys():
			my_score = min_length - int(info['rank'])
			friend_score = min_length - int(friend_albums[album]['rank'])
			common_albums[my_score + friend_score] = \
				{'name': album[0], 'artist': album[1], 'image': info['image'], 'url': info['url']}
	
	# cumulative album score
	result['albums']['score'] = (sum(x for x in common_albums.iterkeys()) * 100) / max
	
	# sort the common albums based on their score
	result['albums']['top'] = [v for (k, v) \
		in sorted(common_albums.items(), reverse=True)][0:10]
	
	return result

def api_call_artists(username, period):
	""" Gets the user's top 50 artists for the given time period
	"""

	r = get(ARTIST_API_CALL % (username, LASTFM_API_KEY, period))
	return r.json()

def api_call_albums(username, period):
	""" Gets the user's top 50 albums for the given time period
	"""
	
	r = get(ALBUM_API_CALL % (username, LASTFM_API_KEY, period))
	return r.json()

def get_artist_dictionary(data):
	""" Parses the given JSON data and returns a dictionary from artist
		to {rank, image}
	"""
	
	result = {}
	for artist in data['topartists']['artist']:
		rank = artist['@attr']['rank']
		name = artist['name']
		image = artist['image'][1]['#text']	# 1 for medium image size
		url = artist['url']
		result[name] = {'rank': rank, 'image': image, 'url': url}
	return result

def get_album_dictionary(data):
	result = {}
	for album in data['topalbums']['album']:
		rank = album['@attr']['rank']
		name = album['name']
		artist = album['artist']['name']
		image = album['image'][1]['#text']	# 1 for medium image size
		url = album['url']
		result[(name, artist)] = {'rank': rank, 'image': image, 'url': url}
	return result

def check_json_response(data):
	""" Returns a list of tokens from the given JSON data that returned an 
		error code
	"""
	
	errors = []
	for item, response in data.iteritems():
		if 'error' in response and response['error'] == 6:
			errors.append(item)
	return errors
