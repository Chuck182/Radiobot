#!/usr/bin/env python
import vlc
from subprocess import call
import glob
import random

class PlayerManager():
    """
        This module is managing the VLC program the alsaaudio mixer for
        volume control. 
    """
    def __init__(self, volume):
        self._volume = volume
        self._player = None
        self._instance = None
        self._media = None
        self._media_list = None
        self._list_player = None
        self.init_vlc()
        self.init_alsa()

    def init_vlc(self):
        """
            Creates a vlc instance, ready to listen for an audio stream.
        """
        self._instance = vlc.Instance("--no-video --aout=alsa --no-metadata-network-access")
        self._player = self._instance.media_player_new()
        self._player.audio_set_volume(self._volume)
        self._list_player = self._instance.media_list_player_new()
        self._list_player.set_media_player(self._player)
        self._list_player.set_playback_mode(vlc.PlaybackMode.loop)

    def init_alsa(self):
        """
            Alsa calls are direct system calls. 
            The init_alsa method purpose is to set the 
            pre-defined volume on the alsa mixer
        """
        call(["amixer", "-M", "-q", "set", "Digital", str(self._volume)+"%"])

    def change_radio(self, url, media_type):
        """
            Takes a stream URL in input and asks the vlc instance to 
            listen for this stream and play its content. 
            Run the init_vlc method if no vlc instance available. 
        """
        if self._player is None or self._list_player is None:
            self.init_vlc()
        else:    
            self._player.stop()
            self._list_player.stop()

        if media_type == "stream":
            self._media = self._instance.media_new(url)
            self._player.set_media(self._media)
            self._player.play()
        elif media_type == "folder":
            files = glob.glob(url)        
            random.shuffle(files)
            media_list = vlc.MediaList(files)
            self._list_player.set_media_list(media_list)
            self._list_player.play()

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

    def get_infos(self):
        info = ""
        try:
            media = self._player.get_media()
            title = str(media.get_meta(vlc.Meta.Title))
            artist = str(media.get_meta(vlc.Meta.Artist))
            info = artist+" - "+title
        except Exception as e:
            print (str(e))
            info = ""
        return info
