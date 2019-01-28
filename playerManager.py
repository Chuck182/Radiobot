#!/usr/bin/env python
import vlc
from subprocess import call

class PlayerManager():
    """
        This module is managing the VLC program the alsaaudio mixer for
        volume control. 
    """
    def __init__(self, volume):
        self._volume = volume
        self._player = None
        self._instance = None
        self.init_vlc()
        self.init_alsa()

    def init_vlc(self):
        """
            Creates a vlc instance, ready to listen for an audio stream.
        """
        self._instance = vlc.Instance("--no-video --aout=alsa --metadata-network-access")
        self._player = self._instance.media_player_new()
        self._player.audio_set_volume(self._volume)

    def init_alsa(self):
        """
            Alsa calls are direct system calls. 
            The init_alsa method purpose is to set the 
            pre-defined volume on the alsa mixer
        """
        call(["amixer", "-M", "-q", "set", "Digital", str(self._volume)+"%"])

    def change_radio(self, url):
        """
            Takes a stream URL in input and asks the vlc instance to 
            listen for this stream and play its content. 
            Run the init_vlc method if no vlc instance available. 
        """
        if self._player is None:
            self.init_vlc()
        else:    
            self._player.stop()
        media = self._instance.media_new(url)
        self._player.set_media(media)
        self._player.play()
    
    def change_volume(self, volume):
        """
            Takes the new volume in parameter and set this volume (percent)
            at two levels :
              - VLC volume setting
              - General ALSA mixer for RCA output
        """
        self._volume = volume
        if self._player is None:
            self.init_vlc()
        self._player.audio_set_volume(self._volume)
        call(["amixer", "-M", "-q", "set", "Digital", str(self._volume)+"%"])
