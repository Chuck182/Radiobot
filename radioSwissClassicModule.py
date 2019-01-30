import requests 
import json 
import pprint 
import time 
import re
from radioMetadataExtrator import AbstractRadioMetadataExtractor
from bs4 import BeautifulSoup

class RadioMetadataExtractor(AbstractRadioMetadataExtractor):
    def __init__(self):
        self._url = "http://www.radioswissclassic.ch/fr" 
        self._artist = None
        self._interpreter = None
        self._title = None

    def get_artist(self):
        return self._artist

    def get_interpreter(self):
        return self._interpreter

    def get_title(self):
        return self._title

    def retrieve_current_metadata(self):
        songFound = False
        try:
            req = requests.get(self._url)
            soup = BeautifulSoup(req.text, features="lxml")
            live = soup.find('div', {'id': 'live'})
            artist_span = live.find('span', {'class': 'titletag'})
            self._artist = artist_span.get_text().strip()
            title_span = live.find('span', {'class': 'artist'})
            self._title = title_span.get_text().strip()
            songFound = True
        except:
            self._artist = None
            self._title = None
            self._interpreter = None
        return songFound
