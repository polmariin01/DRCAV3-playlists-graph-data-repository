import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json


def get_artist(spotify, artist_name : str):
    results = spotify.search(q='artist:' + artist_name, type='artist')
    items = results['artists']['items']
    if len(items) > 0:
        return items[0]
    return 0

def get_image_url(spotify, artist_name : str = 'Nirvana') -> str:
    results = spotify.search(q='artist:' + artist_name, type='artist')
    items = results['artists']['items']
    if len(items) > 0:
        artist = items[0]
        print(artist['name'], artist['images'][0]['url'])
import sys

def save_artist(spotify, artist_name='Nirvana', path="db/spotify/artists/"):
    with open(path+artist_name+".json", 'w') as f:
        artist = get_artist(spotify=spotify, artist_name='Nirvana')
        json.dump(artist,f, indent=4)


spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials())

#artists = ['Nirvana', 'Chick Corea','Rosalia','Quevedo','Queen','Bad Gyal','Martin Garrix','Eminem','ACDC', 'Gigi D\'Agostino', 'Snoop Dogg', 'Rosario', 'El Pony Pisador', 'Gabriel Fauré', 'Albert Pla', 'Avicii', 'El Payo Juan Manuel', 'ZOO', 'Britney Spears']
for artist in artists:
    save_artist(spotify, artist_name=artist)


#print(type(artist))
#print(artist)

