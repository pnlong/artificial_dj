# README
# Phillip Long
# June 21, 2023

# Collects audio data (.mp3 files) that will be used to train neural networks that determine the
# tempo, key, and sections of a given song.


# IMPORTS
import pandas
import requests
from bs4 import BeautifulSoup


# READ IN A PAGE WITH BEAUTIFUL SOUP
# page = requests.get("https://realpython.github.io/fake-jobs/") # get Raw HTML
# soup = BeautifulSoup(page.content, "html.parser") # creates a soup object


