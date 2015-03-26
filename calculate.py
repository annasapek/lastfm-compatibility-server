from requests import get
import json, operator
from config import LASTFM_API_KEY

ARTIST_API_CALL = 'http://ws.audioscrobbler.com/2.0/?method=user.gettopartists&user=%s&api_key=%s&format=json&period=%s'

def get_score(me, friend):
	""" Returns a music compatibility score and a list of common artists in JSON for
		the two given Last.fm usernames.
	"""
	
	# JSON result
	result = {'status' : 0}
	
	# artist compatability
	result = get_artist_score(me, friend, result)
	
	# final result
	return result

def get_artist_score(me, friend, result):
	""" Returns JSON containing an artist compatibility score and a list of top
		common artists for the given two users. The JSON result will also contain
		a status code indicating success of the response (0=success, 1=failure), 
		and a list of error messages upon failure.
	"""
	
	period = '1month'
	data = {me: api_call_artists(me, period), friend: api_call_artists(friend, period)}
	
	# check for errors
	errors = check_json_response(data)
	if errors:
		result['error_messages'] = []
		result['status'] = 1
		for name in errors:
			result['error_messages'].append('%s is not a valid Last.fm username.' % name)
	
	# return if there were errors
	if result['status'] != 0: 
		return result
	
	result['result'] = {'user_1': me, 'user_2': friend}
	
	# dictionaries from artist to {rank, image}
	my_artists = get_artist_dictionary(data[me])
	friend_artists = get_artist_dictionary(data[friend])
	
	# min_length = n + 1, so (min_length - rank) ranges from 1 to n
	min_length = min(len(my_artists), len(friend_artists)) + 1	
	
	# (n + 1)(n) 
	max = min_length * (min_length - 1)
	
	# common artists, a dictionary, {'score': {'name', 'image'}}
	common_artists = {}
	
	# topartists, a list of dictionaries, [{'name', 'image'}]
	result['result']['topartists'] = []
	
	# compute a cumulative score for each shared artist
	for artist, data in my_artists.iteritems():
		
		# check if the other user also listens to this artist
		if artist in friend_artists.iterkeys():
			my_score = min_length - int(data['rank'])
			friend_score = min_length - int(friend_artists[artist]['rank'])
			sum_score = my_score + friend_score
			common_artists[sum_score] = {'name': artist, 'image': data['image']}
			#score += sum_score
	
	# cumulative score
	score = sum(x for x in common_artists.iterkeys())
	
	# sort the common artists based on the cumulative score
	result['result']['topartists'] = [v for (k, v) \
		in sorted(common_artists.items(), reverse=True)]
	result['result']['score'] = (100 * score) / max
	
	return result

def api_call_artists(username, period):
	""" Gets the user's top 50 artists for the given time period
	"""

	r = get(ARTIST_API_CALL % (username, LASTFM_API_KEY, period))
	return r.json()

def get_artist_dictionary(data):
	""" Parses the given JSON data and returns a dictionary from artist
		to {rank, image}
	"""
	
	result = {}
	for artist in data['topartists']['artist']:
		rank = artist['@attr']['rank']
		name = artist['name']
		image = artist['image'][1]['#text']		# 1 for medium image size
		result[name] = {'rank': rank, 'image': image}
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
