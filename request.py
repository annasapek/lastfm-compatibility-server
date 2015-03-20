from requests import get
import json

from config import LASTFM_API_KEY

period = '7day'
username = 'christophersu'
r = get('http://ws.audioscrobbler.com/2.0/?method=user.gettopartists&user=%s&api_key=%s&format=json&period=%s' % (username, LASTFM_API_KEY, period))

print r