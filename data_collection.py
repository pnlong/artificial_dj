# README
# Phillip Long
# June 21, 2023

# Collects audio data (.mp3 files) that will be used to train neural networks that determine the
# tempo, key, and sections of a given song.

# python ./data_collection.py music_library_filepath output_directory chrome_driver_path

import sys
import pandas as pd
from tqdm import tqdm # for progress bar
from re import sub
# sys.argv = ("./data_collection.py", "/Volumes/Seagate/Music", "/Users/philliplong/Desktop/Coding/artificial_dj/data", "/Users/philliplong/Desktop/Coding/chromedriver")


# GET LIST OF SONGS, EXTRACT METADATA
######################################

# create filepath for dataframe
from os.path import join, exists
from os import makedirs
if not exists(sys.argv[2]): # create output directory if it is not yet created
    makedirs(sys.argv[2])
output_filepath = join(sys.argv[2], "tempo_key_data.tsv")


# get filepaths of mp3s in music library
from os.path import abspath, isfile # for getting the absolute filepath
from glob import iglob # recursively access all files in main music library
filepaths = tuple(filepath for filepath in iglob(abspath(sys.argv[1]) + '**/**', recursive = True) if filepath.endswith("mp3") and isfile(filepath))

# get metadata from previously accessed filepaths
metadata = {
    "title": ["",] * len(filepaths),
    "artist": ["",] * len(filepaths),
    "album": ["",] * len(filepaths),
    "genre": ["",] * len(filepaths),
    "path": filepaths
}
from mutagen import File as extract_metadata # for accessing mp3 metadata
print("")
for i in tqdm(range(len(filepaths)), desc = "Extracting metadata from MP3 files"):
    file_metadata = extract_metadata(filepaths[i], easy = True)
    for attribute in (key for key in metadata.keys() if key in file_metadata.keys()):
        metadata[attribute][i] = file_metadata[attribute][0].replace("\n", " ").strip()
metadata["tempo"] = [0.0,] * len(filepaths) # add tempo column
metadata["key"] = ["",] * len(filepaths) # add key column

# special case for songs with their tempo in the title
tempo_indicies = [i for i in range(len(metadata["title"])) if "bpm" in metadata["title"][i].lower()]
for i in tempo_indicies:
    title_split = sub("[^A-Za-z0-9 ]", " ", metadata["title"][i]).lower().split()
    metadata["tempo"][i] = float(title_split[title_split.index("bpm") - 1])
    metadata["key"][i] = None
    del title_split
del tempo_indicies

# convert metadata into a pandas dataframe
data = pd.DataFrame(metadata)
if exists(output_filepath):
    original_data = pd.read_csv(output_filepath, sep = "\t", header = 0, index_col = False, keep_default_na = False, na_values = "NA")
    data = pd.concat([original_data, data]).drop_duplicates(subset = "path").reset_index(drop = True) # the effect of this is that we append any new entries to the end of the dataframe
    del original_data
del metadata

# filter out genres that in general have variable tempo, individual songs will be dealt with later (if Tunebat cannot find them)
data = data[~data["genre"].isin(("Classical", "Jazz"))] # tilde means "NOT", so I am filtering out the mentioned genres
data = data[data["album"].str.lower() != "remixes"] # filter out remixes
data = data[~data["title"].str.lower().str.contains("slowed|sped up|reverb")] # filter out songs that are slowed or sped up
data = data.reset_index(drop = True) # reset indicies

# write basic dataframe
data.to_csv(output_filepath, sep = "\t", header = True, index = False, na_rep = "NA")

######################################

# GET KEY AND BPM DATA
######################################

# imports
from selenium import webdriver
from time import sleep as wait
from random import uniform
from unidecode import unidecode as remove_accents

# a function that types in a given text into a given text entry element like an actual human (one letter at a time)
def simulate_typing(text_entry_element, text):
    for letter in text:
        text_entry_element.send_keys(letter)
        wait(uniform(0.02, 0.05))

# a function to simplify text for string comparison of song titles/artist
simplify_text = lambda text: [word for word in sub("[^A-Za-z0-9 ]", "", remove_accents(text)).lower().strip().split() if word not in ("feat", "ft", "featuring", "with", "and", "&", "remix", "mix", "edit", "the", "a")]

while True: # Selenium has a tendency to suffer from targeting errors, so this while loop automatically restarts it
    try: # try to complete everything

        # set up chrome driver
        driver = webdriver.Chrome(executable_path = sys.argv[3])
        driver.maximize_window() # maximize the driver window
        driver.get("https://www.bing.com")
        wait(2)

        print("")
        for i in tqdm(data[(data["tempo"] == 0.0) & (data["key"] == "")].index, desc = "Scraping the web for music data", mininterval = 8): # iterate over rows that have not been 

            # search bing
            wait(5)
            search_field = driver.find_element_by_name("q") # get the search textbox
            driver.execute_script("return arguments[0].scrollIntoView(true);", search_field) # scroll up to search box
            search_field.clear() # delete any previous text from search box
            search_query = f"{data.at[i, 'artist']} {data.at[i, 'title']} site:musicstax.com" # determine search query
            simulate_typing(text_entry_element = search_field, text = search_query) # type in query
            search_field.submit() # submit search query
            del search_field, search_query

            # find relevant pages
            wait(2)
            search_results = driver.find_elements("xpath", "//li[contains(@class, 'b_algo')]//h2/a") # gets the list item -> header -> page link for each search result
            search_results = [result for result in search_results if "key, tempo of " in result.text.lower()] # filter out totally irrelevant search results
            wait(2)

            # if there are any relevant results, extract track data from musicstax.com
            if len(search_results) > 0: # if there are any relevant results
                driver.execute_script("return arguments[0].scrollIntoView(true);", search_results[0]) # scroll to most relevant link
                search_results[0].click() # click on the most relevant (top) link
                wait(2)

                try: # will fail if 404 error on musicstax
                    # check if song is the right song
                    title_web = simplify_text(text = driver.find_element("xpath", "//h1[@class='song-title']").text) # get the title from the web
                    artist_web = sum([simplify_text(text = artist.text) for artist in driver.find_elements("xpath", "//div[@class='song-artist']/a")], []) # flatten list of artists from the web
                    song_description_web = title_web + artist_web # create a list describing the song description found on the website
                    song_description_actual = simplify_text(text = data.at[i, "title"]) + simplify_text(text = data.at[i, "artist"]) # create a list describing the actual song from the dataset
                    actual_words_in_web_description = [word for word in song_description_actual if word in song_description_web] # return the words from the actual song description that are in the web song description
                    is_probably_right_song = ((len(actual_words_in_web_description) / len(song_description_actual)) >= 0.7)
                    del artist_web, title_web, song_description_web, song_description_actual, actual_words_in_web_description

                    # if it is the right song, extract song data
                    if is_probably_right_song:
                        track_info = [song_fact.text.strip() for song_fact in driver.find_elements("xpath", "//div[@class='song-fact-container']/div[@class='song-fact-container-stat']")] # extract song information (length, tempo, key, loudness)
                        data.at[i, "tempo"] = float(track_info[1]) # set the tempo value
                        data.at[i, "key"] = track_info[2] # set the key value
                        del track_info
                        wait(1)
                    else: # set the tempo and key values to NA
                        data.at[i, "tempo"], data.at[i, "key"] = None, None # set the tempo and key values

                    driver.back() # back to bing
                
                except: # in the event of failure set values as NA and return to Bing
                    data.at[i, "tempo"], data.at[i, "key"] = None, None # set the tempo and key values
                    driver.back() # back to bing
            
            # if there are no results
            else:
                data.at[i, "tempo"], data.at[i, "key"] = None, None # set the tempo and key values

            # write current data to output
            data.to_csv(output_filepath, sep = "\t", header = True, index = False, na_rep = "NA")

        # quit webdriver
        driver.quit()

    except: # if a page doesn't load right because of a target error

        # quit webdriver
        driver.quit()

        print("\nRestarting program.\n")

        wait(5) # give time for Ctrl + C

        # restart iteration and try again

    else:
        break # break out of loop when finished

print("")

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
# data = data[(~data["tempo"].isnull()) | (~data["key"].isnull())] # filter out empty rows that lack both tempo and key values
# data = data.reset_index(drop = True) # reorder columns

# final output data
# print(f"\nWriting output to {output_filepath}.")
# data.to_csv(output_filepath, sep = "\t", header = True, index = False, na_rep = "NA")

######################################