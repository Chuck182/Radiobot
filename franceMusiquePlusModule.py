import requests 
import json 
import pprint 
import time 
from radioMetadataExtrator import AbstractRadioMetadataExtractor

class RadioMetadataExtractor(AbstractRadioMetadataExtractor):
    def __init__(self):
        self._url = "https://www.francemusique.fr/livemeta/pull/402" 
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
        req = requests.get(self._url)
        current_timestamp = time.time() 
        songs = json.loads(req.text)  # Parses the json file provided by the webradio editor
        for song in songs["steps"]: # This json file contains a list of songs in a chronological order
            start = songs["steps"][song]["start"]
            end = songs["steps"][song]["end"]
            if current_timestamp > start and current_timestamp < end: # If now is between the start time and the end time of a song, let's fetch the info
                self._artist = songs["steps"][song]["composers"]
                self._title = songs["steps"][song]["title"]
                if len(songs["steps"][song]["authors"]) > 0:
                    self._interpreter = songs["steps"][song]["authors"]
                elif len(songs["steps"][song]["performers"]) > 0:
                    self._interpreter = songs["steps"][song]["performers"]
                songFound = True # If we can retrieve infos, let's inform the caller that a song info is available
                break # No need to loop on other songs because we found the current one.
        return songFound
