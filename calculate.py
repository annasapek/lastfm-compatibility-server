from requests import get
import json
from config import LASTFM_API_KEY

def get_score(me, friend):
	#me_data = api_call(me)
	#friend_data = api_call(friend)
	period = '1month'
	data = [api_call(me, period), api_call(friend, period)]
	
	score = 0
	
	# dictionaries from artist to rank
	my_artists = get_artist_dictionary(data[0])
	friend_artists = get_artist_dictionary(data[1])
	
	for artist, rank in my_artists.iteritems():
		if artist in friend_artists.iterkeys():
			print artist, rank, friend_artists[artist]
	
	'''
	for data_set in data:
		# pretty printed data
		prettyjson = json.dumps(data_set, sort_keys=True, indent=4, separators=(',', ': '))

		# elements
		root = data_set['topartists']
		artists = root['artist']

		# artist info
		for artist in artists:
			rank = artist['@attr']['rank']
			name = artist['name']
			print rank, name
		#return artists
	'''
	return data

# Makes a last.fm api call for the given user, returning their top 50 artists for the past month
def api_call(username, period):
	# make the last.fm api request
	r = get('http://ws.audioscrobbler.com/2.0/?method=user.gettopartists&user=%s&api_key=%s&format=json&period=%s' % (username, LASTFM_API_KEY, period))
	
	# parsed data
	json_data = r.json()
	
	return json_data

# Returns a dictionary from artist to rank from the given JSON data
def get_artist_dictionary(data):
	result = {}
	for artist in data['topartists']['artist']:
		rank = artist['@attr']['rank']
		name = artist['name']
		print rank, name
		result[name] = rank
	return result