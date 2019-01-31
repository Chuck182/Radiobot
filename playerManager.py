#!/usr/bin/env python
import vlc
from subprocess import call
import glob
import random
import time
import threading

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
        self._library = None
        self._library_iterator = None
        self._timer = 0
        self._lock = threading.Lock()
        self.init_vlc()
        self.init_alsa()

    def init_vlc(self):
        """
            Creates a vlc instance, ready to listen for an audio stream.
        """
        self._instance = vlc.Instance("--no-video --aout=alsa --no-metadata-network-access")
        self._player = self._instance.media_player_new()
        self._player.audio_set_volume(self._volume)

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
        if self._player is None:
            self.init_vlc()
        else:
            if self._player.is_playing():
                self._player.stop()
            self._library_iterator = None

        if media_type == "stream":
            self._media = self._instance.media_new(url)
            self._timer = time.time()
        elif media_type == "folder":
            self._library = glob.glob(url)
            random.shuffle(self._library)
            self._library_iterator = iter(self._library)
            self._timer = time.time()

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

    def update_player(self):
        if self._player is not None and not self._player.is_playing() and time.time()-self._timer > 1: # For every cases
            if self._library_iterator is not None: # It is folder media type
                try:
                    # Start next song
                    song = next(self._library_iterator)
                    print ("Song : "+song)
                    self._media = self._instance.media_new(str(song))
                    self._player.set_media(self._media)
                    self._player.play()
                    self._timer = time.time()
                except StopIteration:
                    random.shuffle(self._library)
                    self._library_iterator = iter(self._library)
            else: # It is network stream
                self._player.set_media(self._media)
                self._player.play()
                self._timer = time.time()
                print ("Starting playing")


    def get_infos(self):
        self._lock.acquire()
        info = ""
        try:
            title = str(self._media.get_meta(vlc.Meta.Title))
            artist = str(self._media.get_meta(vlc.Meta.Artist))
            info = artist+" - "+title
            print ("["+threading.currentThread().getName()+"]  Getting info :-)")
        except Exception as e:
            print (str(e))
            info = ""
        self._lock.release()
        return info
