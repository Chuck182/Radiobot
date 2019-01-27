from abc import ABC,abstractmethod

class AbstractRadioMetadataExtractor(ABC):
    """Classe définissant un extracteur 
    de metadata pour une webradio. 
    Ces metadata permettent de récupérer le titre, 
    l'artiste et l'interprete d'une musique en cours
    de lecture."""

    @abstractmethod
    def retrieveCurrentMetadata(self):
        pass

    @abstractmethod
    def getArtist(self):
        pass

    @abstractmethod
    def getTitle(self):
        pass

    @abstractmethod
    def getInterpreter(self):
        pass
