from abc import ABC,abstractmethod

class AbstractRadioMetadataExtractor(ABC):
    """
        This abstract class defines a metadata extractor module for a specific webradio
        As all the webradios are different, a dedicated module must be
        developped to retrieve the metadata (artist, title, interpreter(s)). 
    """

    @abstractmethod
    def retrieve_current_metadata(self):
        """
            This method tries to fetch the current 
            metadata, related to the current playing song
            of a webradio.
            Returns False if no metadata available.
            or True if available. 
            The content of the metadata must, then, be 
            retrieved from the available getters
        """
        pass

    @abstractmethod
    def get_artist(self):
        """
            Returns the artist of the current song.
            retrieve_current_metadata must be called first. 
        """
        pass

    @abstractmethod
    def get_title(self):
        """
            Returns the title of the current song.
            retrieve_current_metadata must be called first. 
        """
        pass

    @abstractmethod
    def get_interpreter(self):
        """
            Returns the interpreter of the current song.
            retrieve_current_metadata must be called first. 
        """
        pass
