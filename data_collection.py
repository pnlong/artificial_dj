# README
# Phillip Long
# June 21, 2023

# Collects audio data (.mp3 files) that will be used to train neural networks that determine the
# tempo, key, and sections of a given song.

# python ./data_collection.py music_library_filepath output_directory

import sys
# sys.argv = ("./data_collection.py", "/Volumes/Seagate/Music", "/Users/philliplong/Desktop/Coding/artificial_dj")


# GET LIST OF SONGS, EXTRACT METADATA
######################################

# get filepaths of mp3s in music library
from os.path import abspath, isfile # for getting the absolute filepath
from glob import iglob # recursively access all files in main music library
filepaths = tuple(filepath for filepath in iglob(abspath(sys.argv[1]) + '**/**', recursive = True) if filepath.endswith("mp3") and isfile(filepath))

# get metadata from previously accessed filepaths
metadata = {
    "path": filepaths,
    "title": ["",] * len(filepaths),
    "artist": ["",] * len(filepaths),
    "genre": ["",] * len(filepaths),
    "tempo": [None,] * len(filepaths),
    "key": [int(-1),] * len(filepaths)
    }
from mutagen import File as extract_metadata # for accessing mp3 metadata
for i in range(len(filepaths)):
    file_metadata = extract_metadata(filepaths[i], easy = True)
    for attribute in (key for key in metadata.keys() if key in file_metadata.keys()):
        metadata[attribute][i] = file_metadata[attribute][0]
metadata["tempo"] = list(float(tempo) if tempo else 0.0 for tempo in metadata["tempo"]) # convert bpm list to float

# convert metadata into a pandas dataframe
import pandas as pd
data = pd.DataFrame(metadata)
del metadata

# filter out genres that in general have variable tempo, individual songs will be dealt with later (if Tunebat cannot find them)
data = data[~data["genre"].isin(("Classical", "Jazz"))] # tilde means "NOT", so I am filtering out the mentioned genres

######################################

# GET KEY AND BPM DATA
######################################

# authenticate Spotify API access
import spotipy # for accessing Spotify's API
from spotipy.oauth2 import SpotifyOAuth # request authenticator; create app @ https://developer.spotify.com/dashboard
spotify = spotipy.Spotify( # construct spotify API instance
    auth_manager = SpotifyOAuth( # authenticate request
        client_id = "3ba64c24fa0141cf8fe99ccae2b77ad1", # https://developer.spotify.com/dashboard/3ba64c24fa0141cf8fe99ccae2b77ad1/settings
        client_secret = "ce33aa36672d4d5da585d682102649c2",
        redirect_uri = "http://localhost:8080"
    )
)

# get data from Spotify
from time import sleep as wait
for i in range(len(data.index)):
    results = spotify.search(q = f"{data.at[i, 'artist']} {data.at[i, 'title']}".replace(" ", "%20"), # search query
                             type = ["track"],
                             limit = 1 # how many results to show
                             )["tracks"]["items"] # will put the top results in a list of dictionaries
    if len(results) > 0: # if there is a result
        track_info = spotify.audio_features(tracks = [results[0]["id"]])[0] # get Spotify ID of top result (0th index in results)
        data.at[i, "key"] = track_info["key"]
        data.at[i, "tempo"] = float(track_info["tempo"])

    wait(5) # to avoid making too many API calls at once

######################################

# OUTPUT DATA TO TSV
######################################

# filter data
data = data[data["key"] != -1]

# output data
from os.path import join
data.to_csv(join(sys.argv[2], "tempo_key_data.tsv"), sep = "\t")

######################################