import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from neo4j import GraphDatabase
import matplotlib.pyplot as plt
import pandas as pd
import credentials as c
#import graphdatascience as gds

# ------------------------------------ Configuration parameters ------------------------------------ #
user_id = c.SPOTIFY_USER_ID                      # Spotify user ID.
client = c.SPOTIFY_CLIENT_ID                     # Spotify client ID.
secret = c.SPOTIFY_CLIENT_SECRET                 # Spotify client secret.
playlist_uri = "PLAYLIST"                        # public playlist with songs to be sorted.
neo4j_url = c.NEO4J_URL                          # bolt url of the neo4j database.
neo4j_username = c.NEO4J_USERNAME                # neo4j username. defaults to 'neo4j'.
neo4j_password = c.NEO4J_PASSWORD                # neo4j password.
scope = 'playlist-modify-private'                                   # Spotify scope required to manage playlists.
redirect_uri = c.SPOTIFY_REDIRECT_URL            # Spotify callback url. Set to localhost for development.
cache_path = "spotify_cache.tmp"                                    # Where spotify caches the session variables.
create_constraints = True                                 # Whether to create constraints.
spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=client, client_secret=secret))
write_to_spotify = True                                             # Whether to write back the generated playlists to spotify.
plot_kmeans_clusters = False                                        # Whether to plot the kmeans clusters used for playlists.
min_playlist_size = 40                                              # Cut off for playlists to be grouped as 'misc'
playlist_split_limit = 160                                          # size for playlists to be chopped up in smaller ones.
playlist_desc = 'Generated using neo4j-playlist-builder.'           # Description of the generated playlists.
playlist_keywords_count = 3                                         # Number of keywords to use in dynamic playlist names.
filtered_keywords = '"and", "pop", "mellow", "new", "rock", "folk"' # generic keywords to not include in playlist names
playlist_prefix = '[NPB]'                                           # Prefix to put in front of your spotify playlists.
# ------------------------------------ Configuration parameters end --------------------------------- #

def load_graph_using_spotify_api():
    neo4j = create_neo4j_session(url=neo4j_url, user=neo4j_username, password=neo4j_password)
    # print("dropping and creating constraints...")
    # recreate_contraints(neo4j)

    # print("creating tracks...")
    # tracks = get_tracks()
    # tracks = get_track_audio_features(tracks)
    # neo4j.run("UNWIND $tracks as track CREATE (t:Track{id: track.id}) SET t = track",
    #           parameters={'tracks': list(tracks.values())})

    # print("creating albums...")
    # albums = get_album_info(tracks)
    # neo4j.run("UNWIND $albums as album CREATE (a:Album{id: album.id}) SET a = album",
    #           parameters={'albums': list(albums.values())})

    # print("creating artists...")
    # artists = get_artist_info(tracks)
    # neo4j.run("UNWIND $artists as artist CREATE (a:Artist{id: artist.id}) SET a = artist",
    #           parameters={'artists': list(artists.values())})

    # print("finding related artists..")
    # related_artists = get_related_artists(artists)
    # neo4j.run("""UNWIND $relatedartists as artist  MERGE (a:Artist {id: artist.id}) SET a = artist """,
    #           parameters={'relatedartists': list(related_artists.values())})
    # neo4j.run("""MATCH (a:Artist) WHERE (a.original_artist) IS NOT NULL WITH a
    #                MATCH (a2:Artist{id: a.original_artist})
    #                MERGE (a)-[:SPOTIFY_RELATES_TO]->(a2)""")
            
    # print("creating genres..")
    # genres = get_genres(albums, artists)
    # neo4j.run("UNWIND $genres as genre MERGE (g:Genre{name: genre})",
    #           parameters={'genres': list(genres)})

    # print("Linking tracks to albums, genres, and artists...")
    # neo4j.run("MATCH (t:Track), (a:Album{id: t.album}) CREATE (t)-[:TRACK_IN_ALBUM]->(a);")
    # neo4j.run("MATCH (t:Track) UNWIND t.artists as artist MATCH (a:Artist{id: artist}) CREATE (t)-[:TRACK_HAS_ARTIST]->(a)")
    # neo4j.run("MATCH (a:Artist) UNWIND a.genres as genre MATCH (g:Genre{name: genre}) CREATE (a)-[:ARTIST_HAS_GENRE]->(g)")
    # neo4j.run("MATCH (a1:Artist)<--(t:Track)-->(a2:Artist) WHERE id(a1)<id(a2) MERGE (a1)-[:WORKED_WITH {track:t.uri}]->(a2)")
    # neo4j.run("MATCH (ar:Artist)<--(t:Track)-->(al:Album) MERGE (al)-[:ALBUM_HAS_ARTIST]->(ar)")

    #print("Clustering genres using the GDS library and creating super-genres...")
    #cluster_genres_with_gds(neo4j)

    print("Creating playlists based on supergenres and song properties...")
    #generate_playlists(neo4j)

    print("Naming playlists...")
    #name_playlists_based_on_keywords(neo4j)

    if write_to_spotify:
        print("Writing new playlists back to Spotify...")
        create_playlists_in_spotify(neo4j)
    print("Done!")
 

print("Starting the loading!")

def recreate_contraints(neo4j):
    # recreate constraints / indices and clear existing database.
    results = neo4j.run("SHOW CONSTRAINTS")
    for constraint in results:
        result = neo4j.run("DROP " + constraint['description'])
    neo4j.run("CREATE CONSTRAINT FOR (g:Genre) REQUIRE g.name IS UNIQUE")
    neo4j.run("CREATE CONSTRAINT FOR (a:Album) REQUIRE a.id IS UNIQUE")
    neo4j.run("CREATE CONSTRAINT FOR (a:Artist) REQUIRE a.id IS UNIQUE")
    neo4j.run("CREATE CONSTRAINT FOR (t:Track) REQUIRE t.id IS UNIQUE")
    neo4j.run("MATCH (n) DETACH DELETE n;")

def get_tracks():
    results = spotify.playlist(playlist_uri)['tracks']
    items = {}
    while results['next'] or results['previous'] is None:
        for track in results["items"]:
            if track['track']['id']:
                track['track']['artists'] = [artist if type(artist) == str else artist['id'] for artist in
                                             track['track']['artists']]
                track['track']['album'] = track['track']['album'] if type(track['track']['album']) == str else \
                    track['track']['album']['id']
                items[track['track']['id']] = track['track']
            for field in track['track']:
                if track is not None and type(track['track'][field]) == dict:
                    track['track'][field] = None
        if not results['next']:
            break
        results = spotify.next(results)
    return items

def get_track_audio_features(tracks, page_size=100):
    page_count = len(tracks) / page_size
    for i in range(int(page_count) + 1):
        ids = list(tracks.keys())[i * page_size:(i + 1) * page_size]
        if len(ids) == 0:
            break
        audio_features = spotify.audio_features(tracks=ids)
        for track_features in audio_features:
            if track_features is None:
                continue
            track_id = track_features['id']
            for feature, value in track_features.items():
                if feature != 'type':
                    tracks[track_id][feature] = value
    return tracks

def get_album_info(tracks, page_size=20):
    album_ids = set()
    for track_id in tracks.keys():
        album_ids.add(tracks[track_id]['album'])

    all_albums = {}
    page_count = len(album_ids) / page_size
    for i in range(int(page_count) + 1):
        ids = list(album_ids)[i * page_size:(i + 1) * page_size]
        results = spotify.albums(ids)

        for album in results['albums']:
            album['artists'] = [artist['id'] for artist in album['artists']]
            album['images'] = album['images'][1]['url']
            album['external_ids'] = None
            album['external_urls'] = None
            album['tracks'] = len(album['tracks'])
            album['copyrights'] = len(album['copyrights'])
            all_albums[album['id']] = album
    return all_albums

def get_artist_info(items, page_size=50):
    all_artists = {}
    artist_ids = set()
    for track_id in items.keys():
        for artist_nr in items[track_id]['artists']:
            artist_id = artist_nr
            artist_ids.add(artist_id)

    # after we have a list of all artists, get the details from the API
    page_count = len(artist_ids) / page_size
    for i in range(int(page_count) + 1):
        ids = list(artist_ids)[i * page_size:(i + 1) * page_size]
        results = spotify.artists(ids)
        for artist in results['artists']:
            if artist["images"]:
                artist['images'] = artist['images'][1]['url']
            artist['followers'] = artist['followers']['total']
            artist['external_urls'] = None
            all_artists[artist['id']] = artist
    return all_artists

def get_related_artists(items, page_size=50):
    page_count = len(items) / page_size
    new_artists = {}
    for i in range(int(page_count) + 1):
        ids = list(items)[i * page_size:(i + 1) * page_size]
        for id in ids:
            related_artists = spotify.artist_related_artists(id)
            for related_artist in related_artists['artists']:
                related_artist['original_artist'] = id
                if related_artist["images"]:
                    related_artist['images'] = related_artist['images'][1]['url']
                related_artist['followers'] = related_artist['followers']['total']
                related_artist['external_urls'] = None
                new_artists[related_artist['id']] = related_artist
    return new_artists

def get_genres(albums, artists):
    genres = set()
    for item in albums:
        for genre in albums[item]['genres']:
            genres.add(genre)
    for item in artists:
        for genre in artists[item]['genres']:
            genres.add(genre)
    return genres

def create_neo4j_session(url, user, password):
    driver = GraphDatabase.driver(url, auth=(user, password))
    return driver.session()

def cluster_genres_with_gds(neo4j):
    result = neo4j.run("""
    CALL gds.graph.exists($name) YIELD exists WHERE exists CALL gds.graph.drop($name) YIELD graphName
    RETURN graphName + " was dropped." as message
    """, name='genre-has-artist')

    result = neo4j.run("""
    CALL gds.graph.exists($name) YIELD exists WHERE exists CALL gds.graph.drop($name) YIELD graphName
    RETURN graphName + " was dropped." as message
    """, name='genre-similar-to-genre')

    result = neo4j.run("""CALL gds.graph.create.cypher(
          'genre-has-artist',
          'MATCH (p) WHERE p:Artist OR p:Genre RETURN id(p) as id',
          'MATCH (t:Artist)-[:HAS_GENRE]->(g:Genre) RETURN id(g) AS source, id(t) AS target')
    """)
    result = neo4j.run("""CALL gds.nodeSimilarity.write('genre-has-artist', {
                 writeRelationshipType: 'SIMILAR_TO',
                 writeProperty: 'score' })
    """)
    result = neo4j.run("""CALL gds.graph.create(
                'genre-similar-to-genre',
                'Genre',{SIMILAR_TO: {orientation: 'NATURAL'}},
                { relationshipProperties: 'score'})
    """)
    result = neo4j.run("""CALL gds.louvain.write('genre-similar-to-genre', 
    { relationshipWeightProperty: 'score', writeProperty: 'community' })
    """)

    # Post-processing -a decent playlist should have at least 40 songs. The rest we cluster together as 'misc'.
    result = neo4j.run("""
            MATCH (g:Genre)<-[:HAS_GENRE]-(a:Artist)<-[:HAS_ARTIST]-(t:Track)
            WITH g.community as community, collect(g) as genres, count(DISTiNCT t) as trackCount
            WHERE trackCount < """ + str(min_playlist_size) + """
            UNWIND genres as g
            SET g.community = -1
    """)

    # Create "superGenre" nodes as parents of genres.
    neo4j.run("""
    MATCH (g:Genre)
    WITH DISTINCT g.community as community
    CREATE (s:SuperGenre{id: community})
    WITH s
    MATCH (g:Genre{community: s.id})
    CREATE (g)-[:PART_OF]->(s)
    """)

    neo4j.run("""
    MATCH (t:Track)-[:HAS_ARTIST]->()-[:HAS_GENRE]->()-[:PART_OF]->(s:SuperGenre)
    WITH DISTINCT t,s
    CREATE (t)-[:HAS_SUPER_GENRE]->(s)
    """)

    neo4j.run("""
    MATCH (s:SuperGenre)--(t:Track)
    WITH s, avg(t.valence) as valence, avg(t.energy) as energy
    SET s.valence = valence, s.energy = energy
    """)

def name_playlists_based_on_keywords(neo4j):
    # Time for cypher magic - give our communities some names
    neo4j.run("""    
    MATCH (g:Genre)<-[:ARTIST_HAS_GENRE]-(a:Artist)<-[:TRACK_HAS_ARTIST]-(t:Track)
    WITH  g, t
    MATCH (t:Track)-[:IN_PLAYLIST]->(p:Playlist)
    WITH p, collect(split(g.name, ' ')) as names
    WITH p, reduce(allwords = [], n IN names | allwords + n) AS keywords
    UNWIND keywords as keyword
    WITH p, keyword
    WHERE not keyword  in [""" + filtered_keywords + """]
    WITH p, keyword, count(*) as wordcount order by wordcount desc
    WITH p, reduce(name = '', n IN collect(keyword)[0..""" + str(playlist_keywords_count) + """]| name + ' ' + n) AS name
    WITH p, name,
    CASE WHEN p.energy <= 0.25 THEN 'serene' WHEN p.energy <= 0.50 THEN 'calm' 
    WHEN p.energy <= 0.75 THEN 'active' ELSE 'energetic' END AS energy,
    CASE WHEN p.valence <= 0.25 THEN 'heavy-hearted' WHEN p.valence <= 0.50 THEN 'low'
    WHEN p.valence <= 0.75 THEN 'lively' ELSE 'cheerful' END AS mood
    SET p.name = \"""" + playlist_prefix + """ \" + name + " - " + energy +", " + mood
    """)

def generate_playlists(neo4j):
    result = neo4j.run("""MATCH (p:Playlist) DETACH DELETE p""").data()
    result = neo4j.run("""MATCH (s:SuperGenre)--(t:Track) RETURN s.id, count(t) as count""").data()

    # big_super_genres = [x['s.id'] for x in result if x['count'] >= playlist_split_limit]
    # for super_genre in big_super_genres:
    #     make_playlists_for_big_supergenre(neo4j, super_genre_id=super_genre)

    # small_super_genres = [x['s.id'] for x in result if x['count'] < playlist_split_limit]
    # for super_genre in small_super_genres:
    #     make_playlist_for_small_supergenre(neo4j, super_genre_id=super_genre)
    small_super_genres = [x['s.id'] for x in result]
    for super_genre in small_super_genres:
        make_playlist_for_small_supergenre(neo4j, super_genre_id=super_genre)

def make_playlists_for_big_supergenre(neo4j, super_genre_id=313):
    result = neo4j.run("""
    MATCH (s:SuperGenre{id: $superGenre})--(t:Track)
    RETURN t.id, t.danceability as danceability, t.valence as valence, t.energy as energy
    """, parameters={'superGenre': super_genre_id}).data()
    x = pd.DataFrame.from_records(result)

    kmeans = KMeans(n_clusters=int(len(result) / playlist_split_limit) + 1, random_state=0).fit(
        x[['energy', 'valence']])
    if plot_kmeans_clusters:
        plt.scatter(x['energy'], x['valence'], c=kmeans.labels_, s=50, cmap='viridis')
        plt.show()
    x['label'] = kmeans.labels_

    output = x[['t.id', 'label']].values.tolist()
    neo4j.run("""UNWIND $output as row 
    MATCH (s:SuperGenre{id: $superGenre})--(t:Track{id: row[0]})
    MERGE (p:Playlist{id: $superGenre + "-" + row[1]})
    SET p.energy = $centers[row[1]][0]
    SET p.valence = $centers[row[1]][1]
    CREATE (t)-[:IN_PLAYLIST]->(p)""",
              parameters={'output': output, 'superGenre': super_genre_id, 'centers': kmeans.cluster_centers_.tolist()})
    
def make_playlist_for_small_supergenre(neo4j, super_genre_id):
    result = neo4j.run("""
        MATCH (s:SuperGenre{id: $superGenre})--(t:Track)
        MERGE (p:Playlist{id: $superGenre})
        SET p.energy = s.energy
        SET p.valence = s.valence
        CREATE (t)-[:IN_PLAYLIST]->(p)
        """, parameters={'superGenre': super_genre_id}).data()

def create_playlists_in_spotify(neo4j, page_size=100):
    spotify = spotipy.Spotify(
        auth_manager=SpotifyOAuth(client_id=client, client_secret=secret, scope=scope, redirect_uri=redirect_uri,
                                  cache_path=cache_path))

    result = neo4j.run("""
    MATCH (n:Playlist)-[:IN_PLAYLIST]-(t:Track) 
    RETURN n.name as name, n.valence as valence, n.energy as energy, n.id as playlist, collect(t.id) as tracks
    """).data()

    for item in result:
        playlist = spotify.user_playlist_create(user_id, item['name'], public=False,
                                                description=playlist_desc + ' Energy: ' +
                                                            str(item['energy']) + " Mood: " + str(item['valence']))
        tracks_chunks = [item['tracks'][x:x + page_size] for x in range(0, len(item['tracks']), page_size)]
        for chunk in tracks_chunks:
            spotify.user_playlist_add_tracks(user_id, playlist['id'], chunk)    

if __name__ == '__main__':
    load_graph_using_spotify_api()

print("Done!")