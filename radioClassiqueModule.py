from lxml import etree 
import requests
from radioMetadataExtrator import AbstractRadioMetadataExtractor

class RadioMetadataExtractor(AbstractRadioMetadataExtractor):
    def __init__(self):
        self._url = "https://data.radioclassique.fr/XML_Metadata/direct_2.xml" 
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
        req = requests.get(self._url)
        tree = etree.XML(req.text) # Let's open the xml file provided by radio classique 
        songFound = False
        self._artist = None 
        self._title = None 
        self._interpreter = None 
        for song in tree.xpath("/xml/playlist/song"): # The xml file contains the list of songs 
            if song.findtext("Status").lower() == "en ce moment": # Each song entry has a flag status. One song should have the "en ce moment" flag, which indicates it is the current song. 
                if int(song.findtext("type")) >= 21 and int(song.findtext("type")) <= 29: # Song entries also have a type. It appears that types between 20 and 30 are related to songs. Others can be advertisement or talks.
                    self._artist = song.findtext("name")
                    self._title = song.findtext("title")
                    self._interpreter = song.findtext("Interpretes")
                    songFound = True 
                break
        return songFound
