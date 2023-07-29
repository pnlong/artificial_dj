# artificial_dj
Uses artificial intelligence to mix together songs from an inputted playlist.

---

Note the Conda environment `artificial_dj.yml`. Create the environment on your system with the following command:

```
conda env create --file artificial_dj.yml
```

---

## Background

A short background on me: as of June 2023 (when I started this project), I will be going to college in the fall at the University of California, San Diego (UCSD). Once I arrive, one of my goals is to become a fraternity DJ. With four months of experience under my belt, I have realized that the significant majority of DJs never progress beyond a few certain core skills (on which I will later elaborate), and certainly for the purposes of frat parties, a DJ needs only to be lower-intermediate -- **at best**. For a while, I had been wondering if I could use machine learning to create an Artificial-Intelligence (AI) DJ. Discussing this with my dad over lunch during our vacation in Toronto, he actually suggested the idea independently, and we went into depth on the topic.

Inspired by the new ideas from this conversation as well as my plan to conduct AI-Music research in [Professor Julian McAuley's lab](https://cseweb.ucsd.edu/~jmcauley/) at UCSD (largely under his PhD student Zachary Novack, if anyone was wondering), I decided I would try to create my own AI DJ. I thought Spotify had already managed to do it, but [their AI DJ](https://newsroom.spotify.com/2023-02-22/spotify-debuts-a-new-ai-dj-right-in-your-pocket/) is a bit different, and instead of generating a seamless mix from a playlist of songs, it really just provides commentary between songs. What follows is an outline of the steps I plan to take to tackle this challenge (a *gameplan*, per se).


## Tempo

DJs need to know the tempo of a song, typically measured in Beats Per Minute (BPM), if they want to incorporate the track into their mix. For instance, a fast song will not mix well with a slow song, but two fast songs can sound quite good together. I will use machine learning to take an audio file (.MP3) as input and output the song's BPM. See more info on this phase of the project in my GitHub repository [determine_tempo](https://github.com/pnlong/determine_tempo).


## Key

Though perhaps not as important as tempo, musical key comes in at a close second. If DJs do not mix into songs with certain correct keys, to an untrained ear, their mix will sound cacauphonous. To a trained ear, it just sounds bad. I will use machine learning to take an audio file (.MP3) as input and output a song's musical key through two values:

1. The song's relative key / key signature (Ex. "A Major / f# minor")
2. Whether the song is in a Major or minor key

See more info on this phase of the project in my GitHub repository [determine_key](https://github.com/pnlong/determine_key).


## Dividing Up a Song

In the conversation with my dad, we discussed the fact that a lot of recent AI research has been focused on data rather than the actual mechanisms of machine learning. He wondered what kind of data I would use to train an AI DJ...where would I find data with a bunch of strong transitions? At first, I thought downloading a bunch of [Big Bootie Mixes](https://soundcloud.com/two-friends/sets/big-bootie-mixes) off of SoundCloud would do the trick. But after some deeper thought, I realized the following: DJing is less

> *How* do I mix between songs?

and more

> *Where* do I transition into the next track?

Most DJs use the same few mixing processes to transition between songs, all of which can be approached programmatically. The greater struggle is finding where to mix between two songs. I will use machine learning to identify the different sections of a song, labelling the chorus, verse, buildup, outro -- the list goes on. I will need to label the sections of a bunch of songs in my personal music library that I will use as training data. This progress will be analogous to setting Hot Cues for anyone interested in the DJing terminology. See more info on this phase of the project in my GitHub repository [analyze_sections](https://github.com/pnlong/analyze_sections).


## Putting it All Together

Given a playlist of songs, I will first determine their tempos and keys, which I will then use use to algorithmically determine the best order in which to mix the playlist. On its own, this data would be quite an impressive and valuable output, and would make DJing semiautonomous.

Next, I will identify the sections of all the songs in the playlist. For each song but the last, I will determine at which section to begin the transition into the next song, speeding-up/slowing-down or changing the key of the current/next song accordingly. For now, I will use only a simple transition to mix between two songs: replace the low end then replace the high end. To be more precise, I will:

1. Fade out song 1's low frequencies
2. Fade in song 2's low frequencies
3. Fade out song 1's high frequencies
4. Fade in song 2's high frequencies

For most songs, mixing with this formula generally creates a seamless mix. The final output will be a single audio file that has mixed all the songs on the original inputted playlist together.


---

If anything, I should learn a lot about music information retrieval and machine learning from this project. Perhaps I could one day develop my AI DJ into a product, though for now, I don't see it going that far. Let's hope this project goes well.

Phillip Long

---

## Software

### *data_collection.py*

Scrapes [Bing](https://www.bing.com) and [musicstax.com](https://musicstax.com/) for tempo and key data of songs. In the event of a Selenium targetting error, the program will automatically restart where it failed, and can only be cancelled with *Ctrl + C*.

If you have already run this script on the bulk of your music library and your music library is updated, you will need to rename the original output file `tempo_key_data.tsv` to something new (ex. `tempo_key_data.2.tsv`) and then rerun the script on your new music library, perhaps writing a script beforehand that indicates already-processed songs. Once this process is complete, you will need to load both outputs (the original and the new) into your language of choice and append the new to the old, making sure to remove duplicate entries. As it currently exists, this program cannot handle an evolving music library. I plan to implement this in the future.

```
python ./data_collection.py music_library_filepath output_directory chrome_driver_path
```

- `music_library_filepath` is the filepath to a list of .MP3 files, all of which's metadata has been edited such that the ID3 tags include the name, artist, and genre of a song.
- `output_directory` is the directory to which the program will output any data. The program updates its output with every iteration such that if the program crashes, any previously scraped data will be written to the output file and when rerun, the program can pick up where it left off.
- `chrome_driver_path` is the filepath to Selenium Chrome Web Driver. The Chrome Web Driver can be downloaded at (https://chromedriver.chromium.org/downloads). **Note that Chrome Driver version must match the version of Chrome installed on the computer**.