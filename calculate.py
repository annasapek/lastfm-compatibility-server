from requests import get
import json
from config import LASTFM_API_KEY

def get_score(me, friend):
	#me_data = api_call(me)
	#friend_data = api_call(friend)
	period = '1month'
	data = [api_call(me, period), api_call(friend, period)]
	
	# dictionaries from artist to rank
	my_artists = get_artist_dictionary(data[0])
	friend_artists = get_artist_dictionary(data[1])
	
	# score
	score = 0
	
	# n + 1, so min_length - rank ranges from
	min_length = min(len(my_artists), len(friend_artists)) + 1	
	
	# (n + 1)(n) 
	max = min_length * (min_length - 1)
	
	# common artists
	common_artists = {}
	top_artists = []
	
	# compute a cumulative score for each shared artist
	for artist, rank in my_artists.iteritems():
		if artist in friend_artists.iterkeys():
			my_score = min_length - int(rank)
			friend_score = min_length - int(friend_artists[artist])
			sum_score = my_score + friend_score
			common_artists[sum_score] = artist
			score += sum_score
			print rank, artist, friend_artists[artist], my_score, friend_score, my_score + friend_score
	
	# sort the common artists based on the cumulative score
	top_artists = sorted(common_artists.iteritems(), reverse=True)
	
	print 'Max score:', max
	print 'Point score:', score
	print 'Score:', (100 * score) / max
	print top_artists
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
		#print rank, name
		result[name] = rank
	return result