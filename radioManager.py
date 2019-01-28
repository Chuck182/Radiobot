#!/usr/bin/env python
from radio import Radio
import time

class RadioManager():
    """
       This is the orchestrator of the radiobot program. 
       It receives actions from UI (volume, radio) and 
       update the player and the display. 

    """
    def __init__(self, radio_list, volume, volume_step, radio_info_check_interval, full_radio_name_pause, radio_indice, player, display):
        self._radios = radio_list
        self._indice = radio_indice
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
        """
            Called by the UI radio next callback. 
            Update the indice of the radios[] list and call the 
            play_radio method, which will update the player and 
            the display. 
        """
        if self._indice >= len(self._radios)-1 :
            self._indice = 0
        else:
            self._indice += 1
        self.play_radio()

    def previous(self):
        """
            Called by the UI radio previous callback. 
            Update the indice of the radios[] list and call the 
            play_radio method, which will update the player and 
            the display. 
        """
        if self._indice <= 0 :
            self._indice = len(self._radios)-1
        else:
            self._indice -= 1
        self.play_radio()

    def play_radio(self):
        """
            Asks the player to play the selected radio and the 
            display to display the name of this selected radio.
        """
        self._player.change_radio(self.__get_stream_url())
        self._display.update_radio_info(None)
        self._display.update_radio(self.__get_short_name(), self.__get_long_name())
        self._last_check = time.time()-self._radio_info_check_interval+self._full_radio_name_pause # To display the full radio name for few seconds

    def volume_up(self): 
        """
            Called by the UI volume UP callback. 
            Update the volume target value and call the player, alsa
            and the display for update.
        """
        if self._volume <= (100-self._volume_step):
            self._volume += self._volume_step
        self._player.change_volume(self._volume)
        self._display.display_volume(self._volume)

    def volume_down(self): 
        """
            Called by the UI volume DOWN callback. 
            Update the volume target value and call the player, alsa
            and the display for update.
        """
        if self._volume >= (0+self._volume_step):
            self._volume -= self._volume_step
        self._player.change_volume(self._volume)
        self._display.display_volume(self._volume)

    def check_radio_info(self):
        """
            If the radio_info_check_interval is reached, 
            if a module is available for this radio, 
            and if metadata can be downloaded, then it retrieves 
            this new info and notify the display for update. 
        """
        if time.time() - self._last_check > self._radio_info_check_interval: # Run only if it is time to check (defined by the radio_info_check_interval param)
            self._last_check = time.time()
            infos = ""
            module = self._radios[self._indice].get_module() # Get the module related to this radio
            if module is not None: # If a module is available
                if self._radios[self._indice].get_module().retrieve_current_metadata(): # If metadata are available at this time
                    artist = module.get_artist()
                    title = module.get_title()
                    interpreter = module.get_interpreter()
        
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
            if len(infos) > 0: # If some infos have been collected
                if infos != self._previous_info: # And if this info is different from the current one (currently displayed)
                    print ("New info available : "+infos)
                    self._display.update_radio_info(infos) # Notify the display for this new available information
                    self._previous_info = infos # Save this info as the current info for next check
            else:
                self._display.update_radio_info(None) # If no info available at this time, notify the display to cleanup the info currently displayed.

    def get_current_volume(self):
        """
            Returns the current volume level (int)
        """
        return self._volume

    def get_current_radio_indice(self):
        """
            Returns the current radio indice
        """
        return self._indice

    # Private getters
   
    def __get_long_name(self):
        return self._radios[self._indice].long_name

    def __get_short_name(self):
        return self._radios[self._indice].short_name

    def __get_stream_url(self):
        return self._radios[self._indice].stream_url

