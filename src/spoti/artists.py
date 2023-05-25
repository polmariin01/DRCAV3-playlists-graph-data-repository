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
querying_properties = ["id", "name"]


# HERE WORKS WITH SPOTIPY 
def get_artist(artist_name : str):
    results = spotify.search(q='artist:' + artist_name, type='artist')
    items = results['artists']['items']
    if len(items) > 0:
        return items[0]
    return 0

'''
def save_artist(artist_name='Nirvana', path=PATH_DB_ARTISTS):
    with open(path+artist_name+".json", 'w') as f:
        artist = get_artist(artist_name=artist_name)
        json.dump(artist,f, indent=4)
        return artist
'''
def save_artist(artist_name='Nirvana', path=PATH_DB_ARTISTS):
    artist = get_artist(artist_name=artist_name)
    file_name = artist['id']+".json"
    file_path = path+file_name
    if os.path.exists(file_path):
        return None , file_name
    else:
        with open(file_path, 'w') as f:
            json.dump(artist,f, indent=4)
            return artist , file_name

def crear_json_artistes():
    for artist in artists:
        flag , file_name = save_artist(artist_name=artist)
        if flag is not None:
            print(f"Created json for {artist} - {file_name}")
        else:
            print(f"Json for {artist} already existed - {file_name}")


def artist(artist_id, search_by = "id"):
    # The properties can be accessed using the name of the artist or the ID
    # search_by can be 'id' or 'name'
    if search_by == "id":                                   #If by id
        llista_artistes = os.listdir(PATH_DB_ARTISTS)
        #print(llista_artistes)
        if artist_id in llista_artistes:                    #If id exists in local cache
            with open(PATH_DB_ARTISTS+artist_id,'r') as f:
                data = json.load(f)
                return data
        else:
            try:
                artista = spotify.artist(artist_id)
                save_artist(artista['name'])
                return artista
            except Exception as e:                          #Id invalida
                print(e)
            
    elif search_by in querying_properties:                  # Searching by name
        if artist_id in artists: 
            id = get_artist(artist_id)['id']
            with open(PATH_DB_ARTISTS+id+".json",'r') as f:
                data = json.load(f)
                return data
        else:
            artists.append(artist_id)
            flag , file_name = save_artist(artist_name=artist_id)
            if flag is not None:
                print(f"Created json for {artist_id} - {file_name}")
                return flag
            else:
                #print(f"Json for {artist_id} already existed - {file_name}")
                return get_artist(artist_id)
    else:
        raise NameError("Invalid sear_by parameter")


def get_artist_property(artist_id, property = "id", search_by = "id"):
    artista = artist(artist_id, search_by=search_by)
    return artista[property]

'''
def get_artist_property(artist_id, property = "id", search_by = "id"):
    # The properties can be accessed using the name of the artist or the ID
    # search_by can be 'id' or 'name'
    if search_by == "id":                                   #If by id
        llista_artistes = os.listdir(PATH_DB_ARTISTS)
        #print(llista_artistes)
        if artist_id in llista_artistes:                    #If id exists in local cache
            with open(PATH_DB_ARTISTS+artist_id,'r') as f:
                data = json.load(f)
                return data[property]
        else:
            try:
                artista = spotify.artist(artist_id)
                save_artist(artista['name'])
                return artista[property]
            except Exception as e:
                print(e)
            
    elif search_by in querying_properties:
        if artist_id in artists: 
            id = get_artist(artist_id)['id']
            with open(PATH_DB_ARTISTS+id+".json",'r') as f:
                data = json.load(f)
                return data[property]
        else:
            artists.append(artist_id)
            flag , file_name = save_artist(artist_name=artist_id)
            if flag is not None:
                print(f"Created json for {artist_id} - {file_name}")
                return flag[property]
            else:
                print(f"Json for {artist_id} already existed - {file_name}")
                return get_artist(artist_id)[property]
    else:
        raise NameError("Invalid sear_by parameter")
'''

    
def get_id(artist_id, search_by = "id"):
    return get_artist_property(artist_id, search_by=search_by)

def get_uri(artist_id, search_by = "id"):
    return get_artist_property(artist_id, property="uri", search_by=search_by)

def get_photo_url(artist_id, search_by = "id"):
    images = get_artist_property(artist_id, "images", search_by=search_by)
    return images[0]['url']

def get_top_ten_tracks(artist_name, search_by = "id"):
    artist_uri = get_uri(artist_name, search_by=search_by)
    return spotify.artist_top_tracks(artist_uri)


#crear_json_artistes()

'''
print("Nom no esta pero si")
print(get_artist_property("David Bisbal", search_by="name"))
print("Nom no esta")
print(get_artist_property("Miley Cyrus", search_by="name"))
print("Nom esta")
print(get_artist_property("Eminem", search_by="name"))
print("Id esta")
print(get_artist_property("6olE6TJLqED3rqDCT0FyPh"))
print("Id no esta")
print(get_artist_property("6olE6TJLqED3rqDCT0Fy4h"))
'''

print(get_top_ten_tracks("rosalia", search_by='name'))


'''
    arxius = os.listdir()
    for a in arxius:
        with open(a,'r') as f:
            data = json.load(f)

    return
'''

