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
    "key": ["",] * len(filepaths)
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
data = data.reset_index(drop = True)

######################################

# GET KEY AND BPM DATA
######################################

# imports
import bs4, requests
from urllib.parse import quote_plus
from time import sleep as wait

for i in range(len(data.index)):
    # search bing, MAKE SURE USER IS SIGNED IN
    search_query = f"{data.at[i, 'artist']} {data.at[i, 'title']} site:musicstax.com" # determine search query
    search_results_soup = bs4.BeautifulSoup(requests.get("https://www.bing.com/search?q=" + quote_plus(search_query)).text, "html.parser") # create beautiful soup object with the bing search results
    search_results = [result.find("h2", recursive = False).find("a", recursive = False) for result in search_results_soup.find_all("li", class_ = "b_algo")] # gets the page link for each search result
    search_results = [result for result in search_results if "key, tempo of " in result.text.lower()] # filter out totally irrelevant search results
    wait(3)

    # if there are any relevant results, extract track data from musicstax.com
    if len(search_results) > 0: # if there are any relevant results
        soup = bs4.BeautifulSoup(requests.get(search_results[0].get("href")).text, "html.parser") # create beautiful soup object from the top bing result
        track_info = [song_fact.find("div", class_ = "song-fact-container-stat", recursive = False).text.strip() for song_fact in soup.find_all("div", class_ = "song-fact-container")] # extract song information (length, tempo, key, loudness)
        data.at[i, "key"] = int(track_info[1])
        data.at[i, "tempo"] = track_info[2]
        wait(3)


# get data from Spotify
#from time import sleep as wait
#for i in range(len(data.index)):
#    search_query = f"{data.at[i, 'artist']} {data.at[i, 'title']}".replace(" ", "%20")
#    results = spotify.search(q = search_query, type = ["track"], limit = 1)["tracks"]["items"] # will put the top results in a list of dictionaries
#    if len(results) > 0: # if there is a result
#        track_info = spotify.audio_features(tracks = [results[0]["id"]])[0] # get Spotify ID of top result (0th index in results)
#        data.at[i, "key"] = int(track_info["key"])
#        data.at[i, "tempo"] = float(track_info["tempo"])
#    wait(5) # to avoid making too many API calls at once

######################################

# OUTPUT DATA TO TSV
######################################

# filter data
data = data[(data["key"] != -1) & (data["tempo"] > 0.0)]

# reorder columns
data = data[["title", "artist", "genre", "path", "tempo", "key"]]
data = data.reset_index(drop = True)

# output data
from os.path import join
data.to_csv(join(sys.argv[2], "tempo_key_data.tsv"), sep = "\t", header = True, index = False)

######################################