from __future__ import print_function  # (at top of module)
from spotipy.oauth2 import SpotifyClientCredentials
import json
import spotipy
import time
import sys
import pandas as pd
import spotipy.util as util
from spotipy.oauth2 import SpotifyOAuth

scope = 'user-library-read'
if __name__ == '__main__':
    # util.prompt_for_user_token("12167283276", scope, client_id='582a7ae4bd534e93ba02c6fba4e7eea3',
    #                            client_secret='43fdeb78520142d1899bc49506e1aa26', redirect_uri='http://localhost:1410/')
    # client_credentials_manager = SpotifyClientCredentials()
    # sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    file1 = open("MyFile.txt", "w")

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, client_id='582a7ae4bd534e93ba02c6fba4e7eea3',
                                                   client_secret='43fdeb78520142d1899bc49506e1aa26',
                                                   redirect_uri='http://localhost:1410/'))
    sp.trace = False

    # read and output the inputted excel sheet
    songs_array = pd.read_csv('songs_only.csv')
    file1.write(songs_array.to_json())
    file1.write("\n\n")
    jsonDict = {}
    song_name = ''
    start = time.time()

    # Go through each song in the song column (index corresponds with the row, row = track name in that row)
    for index, row in songs_array.iterrows():
        track_name = (row['songs'])

        # search for a song named 'track_name' in Spotify
        results = sp.search(q=track_name, limit=1)
        tids = []

        # if no song was found in Spotify, output the song name that was read in and empty fields
        if not results['tracks']['items']:
            song_name = track_name
            jsonDict[index] = [song_name, '', '', '', '', '', '', '', '', '', '']
            file1.write(song_name)
            file1.write("\n")

        # if song was found on Spotify
        else:

            # Find the track's ID to get audio features
            tids.append(results['tracks']['items'][0]['uri'])
            file1.write(str(tids))
            file1.write("\n")

            # Find the artist in the JSON object to do an artist search
            artists = results['tracks']['items'][0]['artists']

            # Search for the artist in Spotify (using just the top artist)
            artistSearch = sp.search(q=artists[0]['name'], type='artist', limit=1)

            # take the genre that is associated with the artist
            genres = artistSearch['artists']['items'][0]['genres']

            # Get audio features using the track's ID stored in TIDS
            features = sp.audio_features(tids)

            if features[0] is not None:
                # define each variable needed from the "get audio features" "search for a track" query for the project
                song_name = results['tracks']['items'][0]['name']
                popularity = results['tracks']['items'][0]['popularity']
                energy = features[0]['energy']
                dance = features[0]['danceability']
                liveness = features[0]['liveness']
                valence = features[0]['valence']
                tempo = features[0]['tempo']
                instrumental = features[0]['instrumentalness']
                acoustic = features[0]['acousticness']
                artistName = artists[0]['name']

                # store all values in a JSON
                jsonDict[index] = [song_name, artistName, energy, dance, liveness, valence, tempo, instrumental,
                                   acoustic, popularity, genres]
                file1.write(json.dumps(features, indent=4))
                file1.write("\n\n")

    # store the JSON object into a Pandas array
    df = pd.DataFrame(jsonDict).T

    # output these column titles in excel
    df.columns = ['song', 'artist', 'energy', 'dance', 'liveness', 'valence', 'tempo', 'instrumental', 'acoustic',
                  'popularity', 'genres']

    # #Join original songs and metrics
    result = songs_array.join(df)

    # output the file to csv
    result.to_csv('song_metrics.csv')

    # end timer and output how long the entire search took
    delta = time.time() - start
    file1.write("features retrieved in %.2f seconds" % (delta,))
    file1.write("\n\n")
    file1.close()
