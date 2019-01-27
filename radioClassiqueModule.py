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
        tree = etree.XML(req.text) 
        songFound = False
        self._artist = None 
        self._title = None 
        self._interpreter = None 
        for song in tree.xpath("/xml/playlist/song"):
            if song.findtext("Status").lower() == "en ce moment":
                if int(song.findtext("type")) >= 21 and int(song.findtext("type")) <= 29:
                    self._artist = song.findtext("name")
                    self._title = song.findtext("title")
                    self._interpreter = song.findtext("Interpretes")
                    songFound = True
                break
        return songFound
