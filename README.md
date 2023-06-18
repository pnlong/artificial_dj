# artificial_dj
Uses artificial intelligence to mix together songs from an inputted playlist.

---

## Background

A short background on me: as of June 2023 (when I started this project), I will be going to college in the fall at University of California, San Diego (UCSD). Once I arrive, one of my goals is to become a fraternity DJ. With four months of experience under my belt, I have realized that the significant majority of DJs never progress beyond a few certain core skills (on which I will later elaborate), and certainly for the purposes of frat parties, a DJ needs only to be lower-intermediate -- **at best**. For a while, I had been wondering if I could use machine learning (ML) to create an Artificial-Intelligence (AI) DJ. Discussing this with my dad over tacos during our vacation to Toronto, he actually suggested the idea independently, and we went into depth on the topic.

Inspired by these new ideas as well as my plan to conduct AI-Music Research in [Professor Julian McAuley's lab](https://cseweb.ucsd.edu/~jmcauley/) at UCSD (largely under his PhD student Zachary Novack, if anyone was wondering), I decided I would try to create my own AI DJ. Though I thought Spotify had already managed to do it, their AI DJ is a bit different, and instead of generating a seamless mix from a playlist of songs, it really just provides [commentary between songs](https://newsroom.spotify.com/2023-02-22/spotify-debuts-a-new-ai-dj-right-in-your-pocket/). What follows is an outline of the steps I plan to take to tackle this challenge (a *gameplan*, per se).


## Tempo

DJs need to know the tempo of a song, typically measured in Beats Per Minute (BPM), if they want to incorporate the track into their mix. For instance, a fast song will not mix well with a slow song, but two fast songs can sound quite good together. I will use machine learning to take an audio file (.mp3) as input and output the song's BPM. See more info on this phase of the project in my GitHub repository [determine_tempo](https://github.com/pnlong/determine_tempo).


## Key

Though perhaps not as important as tempo, musical key is a close second. If DJs do not mix into songs of certain correct keys, to an untrained ear, something will sound obviously wrong and extremely cacauphonous. To a trained ear, a DJ who does not utilize simple music theory and mix into new songs with the correct key just sounds bad. I will use machine learning to take an audio file (.mp3) as input and output a song's musical key with two values:

1. The song's relative key / key signature (Ex. "A Major / f# minor").
2. Whether the song is in a Major or minor key.

See more info on this phase of the project in my GitHub repository [determine_key](https://github.com/pnlong/determine_key).


## Dividing Up a Song

In the conversation with my dad, we discussed the fact that a lot of recent AI research has been focused on data rather than the actual mechanisms of machine learning. He wondered what kind of data I would use to train an AI DJ. Where would I find all these transitions? At first, I suggested downloading a bunch of [Big Bootie Mixes](https://soundcloud.com/two-friends/sets/big-bootie-mixes) off of SoundCloud. But after some deeper thought, I realized the following: DJing is less

> How do I mix between songs?

and more

> Where do I transition into the next track?

Most DJs use the same few mixing processes to transition between songs, all of which can be easily approached programmatically. The greater struggle is finding where to mix two songs. I will use machine learning to identify the different sections of a song, labelling the chorus, verse, buildup, outro -- the list goes on. I need to label the sections of a bunch of songs in my personal music library that I will use as training data. This progress will be analogous to setting Hot Cues for anyone interested in the DJing terminology. See more info on this phase of the project in my GitHub repository [analyze_sections](https://github.com/pnlong/analyze_sections).


## Putting it All Together

Given a playlist of songs, I will first determine their tempos and keys, which I will then use use to algorithmically determine the best order in which to play them. On its own, this data would be quite an impressive and valuable output. Next, I will identify the sections of all the songs. For each song but the last, I will determine at which section to begin the transition into the next song, speeding-up/slowing-down or changing the key of the current/next song accordingly. For now, I will use only a simple transition to mix between two songs: first replace the low end,next replace the high end. To be more precise, I will:

1. Fade out song 1's low frequencies
2. Fade in song 2's low frequencies
3. Fade out song 1's high frequencies
4. Fade in song 2's high frequencies

The final output will be a single audio file that has mixed all the songs on the original inputted playlist together.


---

If anything, I should learn a lot about music information retrieval and machine learning from this project. Perhaps I could one day develop my AI DJ into a product, though for now, I don't see it going that far. Let's hope this project goes well.

Phillip Long