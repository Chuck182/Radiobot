#!/usr/bin/env python
from radio import Radio

class RadioManager():
    def __init__(self, radio_list, volume, volume_step, player, display):
        self._radios = radio_list
        self._indice = 0
        self._radio_info_available = False
        self._volume = volume
        self._volume_step = volume_step
        self._player = player
        self._display = display

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
        self._display.update_radio(self.__get_short_name(), self.__get_long_name())
    
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

    # Private functions

    def __is_radio_available(self):
        available = False
        if len(self._radios) > 0:
            available = True
        return available

    def __get_long_name(self):
        return self._radios[self._indice].long_name
    
    def __get_short_name(self):
        return self._radios[self._indice].short_name
    
    def __get_stream_url(self):
        return self._radios[self._indice].stream_url
    
    def __update_radio_info(self):
        if self._radios[self._indice].get_module() is not None:
            self._radio_info_available = self._radios[self._indice].get_module().retrieveCurrentMetadata()
        else:
            self._radio_info_available = False
        return self._radio_info_available

    def __get_radio_info(self):
        if self._radio_info_available:
            module = self._radio_info_available = self._radios[self._indice].get_module() 
            infos = module.getArtist() + " - " + module.getTitle() + " - " + module.getInterpreter()
