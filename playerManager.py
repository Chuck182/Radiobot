#!/usr/bin/env python
import vlc
from subprocess import call

class PlayerManager():
    def __init__(self, volume):
        self._volume = volume
        self._player = None
        self._instance = None
        self.init_vlc()
        self.init_alsa()

    def init_vlc(self):
        self._instance = vlc.Instance("--no-video --aout=alsa --metadata-network-access")
        self._player = self._instance.media_player_new()
        self._player.audio_set_volume(self._volume)

    def init_alsa(self):
        call(["amixer", "-M", "-q", "set", "Digital", str(self._volume)+"%"])

    def change_radio(self, url):
        if self._player is None:
            self.init_vlc()
        else:    
            self._player.stop()
        media = self._instance.media_new(url)
        self._player.set_media(media)
        self._player.play()
    
    def change_volume(self, volume):
        self._volume = volume
        if self._player is None:
            self.init_vlc()
        self._player.audio_set_volume(self._volume)
        call(["amixer", "-M", "-q", "set", "Digital", str(self._volume)+"%"])
