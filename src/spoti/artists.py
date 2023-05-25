import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json
import os

HOME_NAME="DRCAV3-playlists-network-data-repository"
while os.getcwd().split('\\')[-1] != HOME_NAME:
    #print(os.getcwd())
    #print(os.path.dirname(os.getcwd()))
    os.chdir("..")
PATH_DB_SPOTIFY="db/spotify/"
PATH_DB_ARTISTS=PATH_DB_SPOTIFY+"artists/"
artists = ['Nirvana', 'Chick Corea','Rosalia','Quevedo','Queen','Bad Gyal','Martin Garrix','Eminem','ACDC', 'Gigi D\'Agostino', 'Snoop Dogg', 'Rosario', 'El Pony Pisador', 'Gabriel Fauré', 'Albert Pla', 'Avicii', 'El Payo Juan Manuel', 'ZOO', 'Britney Spears']
spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials())

# HERE WORKS WITH SPOTIPY 
def get_artist(artist_name : str):
    results = spotify.search(q='artist:' + artist_name, type='artist')
    items = results['artists']['items']
    if len(items) > 0:
        return items[0]
    return 0

def save_artist(artist_name='Nirvana', path=PATH_DB_ARTISTS):
    with open(path+artist_name+".json", 'w') as f:
        artist = get_artist(artist_name=artist_name)
        json.dump(artist,f, indent=4)
        return artist

def crear_json_artistes():
    for artist in artists:
        save_artist(spotify, artist_name=artist)
        print("Created json for {artist}")

def get_artist_property(artist_name, property = "id"):
    if artist_name in artists: 
        with open(PATH_DB_SPOTIFY+artist_name,'r') as f:
            data = json.load(f)
            return data[property]
    else:
        artist = save_artist(artist_name)
        return artist[property]

    
def get_id(artist_name):
    get_artist_property(artist_name)

def get_uri(artist_name):
    get_artist_property(artist_name, property="uri")

def get_photo_url(artist_name):
    images = get_artist_property(artist_name, "images")
    return images[0]['url']

def get_top_ten_tracks(artist_name):
    artist_uri = get_uri(artist_name)
    return spotify.artist_top_tracks(artist_uri)


'''
    arxius = os.listdir()
    for a in arxius:
        with open(a,'r') as f:
            data = json.load(f)

    return
'''

