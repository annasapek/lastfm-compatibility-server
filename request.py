from requests import get
import json

from config import LASTFM_API_KEY

# request variables
period = '7day'
username = 'christophersu'

# make the last.fm api request
r = get('http://ws.audioscrobbler.com/2.0/?method=user.gettopartists&user=%s&api_key=%s&format=json&period=%s' % (username, LASTFM_API_KEY, period))

# parsed data
json_data = r.json()

# pretty printed data
prettyjson = json.dumps(json_data, sort_keys=True, indent=4, separators=(',', ': '))

# elements
root = json_data['topartists']
artists = root['artist']

# artist info
for artist in artists:
	rank = artist['@attr']['rank']
	name = artist['name']