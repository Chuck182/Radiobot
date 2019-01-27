#!/usr/bin/env python
from radio import Radio
import time

class RadioManager():
    def __init__(self, radio_list, volume, volume_step, radio_info_check_interval, full_radio_name_pause, player, display):
        self._radios = radio_list
        self._indice = 0
        self._volume = volume
        self._volume_step = volume_step
        self._player = player
        self._display = display
        self._radio_info_check_interval = radio_info_check_interval
        self._last_check = time.time()
        self._previous_info = ""
        self._full_radio_name_pause = full_radio_name_pause

    # Public functions

    def next(self):
        if self._indice >= len(self._radios)-1 :
            self._indice = 0
        else:
            self._indice += 1
        self.play_radio()

    def previous(self):
        if self._indice <= 0 :
            self._indice = len(self._radios)-1
        else:
            self._indice -= 1
        self.play_radio()

    def play_radio(self):
        self._player.change_radio(self.__get_stream_url())
        self._display.update_radio_info(None)
        self._display.update_radio(self.__get_short_name(), self.__get_long_name())
        self._last_check = time.time()-self._radio_info_check_interval+self._full_radio_name_pause # To display the full radio name for few seconds

    def volume_up(self): 
        if self._volume <= (100-self._volume_step):
            self._volume += self._volume_step
        self._player.change_volume(self._volume)
        self._display.display_volume(self._volume)

    def volume_down(self): 
        if self._volume >= (0+self._volume_step):
            self._volume -= self._volume_step
        self._player.change_volume(self._volume)
        self._display.display_volume(self._volume)

    def check_radio_info(self):
        if time.time() - self._last_check > self._radio_info_check_interval:
            self._last_check = time.time()
            infos = ""
            module = self._radios[self._indice].get_module()
            if module is not None:
                if self._radios[self._indice].get_module().retrieveCurrentMetadata():
                    artist = module.getArtist()
                    title = module.getTitle()
                    interpreter = module.getInterpreter()
        
                    if not isinstance(artist, str):
                        artist = ""
        
                    if not isinstance(title, str):
                        title = ""
        
                    if not isinstance(interpreter, str):
                        interpreter = ""
        
                    infos = artist
                    if len(artist) > 0 and len(title) > 0 and len(interpreter) > 0:
                        infos += " - "
        
                    infos += title
                    if len(title) > 0 and len(interpreter) > 0:
                        infos += " - "
        
                    infos += interpreter
            if len(infos) > 0:
                if infos != self._previous_info:
                    print ("Infos : "+infos)
                    self._display.update_radio_info(infos)
                    self._previous_info = infos
            else:
                self._display.update_radio_info(None)


    # Private functions
   
    def __get_long_name(self):
        return self._radios[self._indice].long_name

    def __get_short_name(self):
        return self._radios[self._indice].short_name

    def __get_stream_url(self):
        return self._radios[self._indice].stream_url

