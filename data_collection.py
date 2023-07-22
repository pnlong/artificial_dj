# README
# Phillip Long
# June 21, 2023

# Collects audio data (.mp3 files) that will be used to train neural networks that determine the
# tempo, key, and sections of a given song.

# python ./data_collection.py music_library_filepath output_directory chrome_driver_path

import sys
# sys.argv = ("./data_collection.py", "/Volumes/Seagate/Music", "/Users/philliplong/Desktop/Coding/artificial_dj", "/Users/philliplong/Desktop/Coding/chromedriver")


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
from tqdm import tqdm # for progress bar
print("")
for i in tqdm(range(len(filepaths)), desc = "Extracting metadata from MP3 files"):
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
from selenium import webdriver
from time import sleep as wait
from random import uniform

# a function that types in a given text into a given text entry element like an actual human (one letter at a time)
def simulate_typing(text_entry_element, text):
    for letter in text:
        text_entry_element.send_keys(letter)
        wait(uniform(0.05, 0.20))

# set up chrome driver
driver = webdriver.Chrome(executable_path = sys.argv[3])
driver.maximize_window() # maximize the driver window
driver.get("https://www.bing.com")
wait(2)

print("")
for i in tqdm(range(len(data.index)), desc = "Scraping the web for music data", mininterval = 6.5):

    # search bing
    search_field = driver.find_element_by_name("q") # get the search textbox
    search_field.clear() # delete any previous text from search box
    search_query = f"{data.at[i, 'artist']} {data.at[i, 'title']} site:musicstax.com" # determine search query
    simulate_typing(text_entry_element = search_field, text = search_query)
    search_field.submit() # submit search query

    # find relevant pages
    search_results = driver.find_elements("xpath", "//li[contains(@class, 'b_algo')]") # gets the list item for each search result
    search_results = [result.find_element("xpath", ".//h2/a") for result in search_results] # gets the page link
    search_results = [result for result in search_results if "key, tempo of " in result.text.lower()] # filter out totally irrelevant search results
    wait(2.5)

    # if there are any relevant results, extract track data from musicstax.com
    if len(search_results) > 0: # if there are any relevant results
        search_results[0].click() # click on the most relevant (top) link
        wait(2)
        track_info = driver.find_elements("xpath", "//div[@class='song-fact-container']/div[@class='song-fact-container-stat']") # extract song information (length, tempo, key, loudness)
        data.at[i, "tempo"] = float(track_info[1].text.strip()) # set the tempo value
        data.at[i, "key"] = track_info[2].text.strip() # set the key value
        wait(1)
        driver.back() # back to bing


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
output_filepath = join(sys.argv[2], "tempo_key_data.tsv")
print(f"\nWriting output to {output_filepath}.")
data.to_csv(output_filepath, sep = "\t", header = True, index = False)

######################################