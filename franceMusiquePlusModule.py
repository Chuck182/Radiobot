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

    def getArtist(self):
        return self._artist

    def getInterpreter(self):
        return self._interpreter

    def getTitle(self):
        return self._title

    def retrieveCurrentMetadata(self):
        songFound = False
        req = requests.get(self._url)
        current_timestamp = time.time() 
        songs = json.loads(req.text) 
        for song in songs["steps"]:
            start = songs["steps"][song]["start"]
            end = songs["steps"][song]["end"]
            if current_timestamp > start and current_timestamp < end:
                self._artist = songs["steps"][song]["composers"]
                self._title = songs["steps"][song]["title"]
                if len(songs["steps"][song]["authors"]) > 0:
                    self._interpreter = songs["steps"][song]["authors"]
                elif len(songs["steps"][song]["performers"]) > 0:
                    self._interpreter = songs["steps"][song]["performers"]
                songFound = True
                break 
        return songFound
