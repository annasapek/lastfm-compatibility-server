from requests import get
import json
from config import LASTFM_API_KEY

def get_score(me, friend):
	period = '1month'
	data = [api_call_artists(me, period), api_call_artists(friend, period)]
	result = {'user_1': me, 'user_2': friend}
	
	# dictionaries from artist to rank
	my_artists = get_artist_dictionary(data[0])
	friend_artists = get_artist_dictionary(data[1])
	
	# score
	score = 0
	
	# min_length = n + 1, so (min_length - rank) ranges from 1 to n
	min_length = min(len(my_artists), len(friend_artists)) + 1	
	
	# (n + 1)(n) 
	max = min_length * (min_length - 1)
	
	# common artists
	common_artists = {}
	result['topartists'] = []
	
	# compute a cumulative score for each shared artist
	for artist, rank in my_artists.iteritems():
		if artist in friend_artists.iterkeys():
			my_score = min_length - int(rank)
			friend_score = min_length - int(friend_artists[artist])
			sum_score = my_score + friend_score
			common_artists[artist] = sum_score
			score += sum_score
			print rank, artist, friend_artists[artist], my_score, friend_score, my_score + friend_score
	
	# sort the common artists based on the cumulative score
	result['topartists'] = sorted(common_artists.items(), key=lambda (k, v): common_artists[k], reverse=True)
	result['score'] = (100 * score) / max
	
	print 'Max score:', max
	print 'Point score:', score
	print 'Score:', result['score']
	print result['topartists']
	return result

# Makes a last.fm api call for the given user, returning their top 50 artists for the past month
def api_call_artists(username, period):
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