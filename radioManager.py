#!/usr/bin/env python
from radio import Radio
import time
import threading
from queue import Queue

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
        self._queue = Queue()
        self._threads = []
        self._lock = threading.Lock()

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
        self._display.on_thread(self._display.update_radio_info, None)
        self._display.on_thread(self._display.update_radio, self.__get_short_name(), self.__get_long_name())
        self._last_check = time.time()-self._radio_info_check_interval+self._full_radio_name_pause # To display the full radio name for few seconds
        self._player.change_radio(self.__get_stream_url(), self.__get_media_type())

    def volume_up(self): 
        """
            Called by the UI volume UP callback. 
            Update the volume target value and call the player, alsa
            and the display for update.
        """
        if self._volume <= (100-self._volume_step):
            self._volume += self._volume_step
        self._player.change_volume(self._volume)
        self._display.on_thread(self._display.display_volume, self._volume)

    def volume_down(self): 
        """
            Called by the UI volume DOWN callback. 
            Update the volume target value and call the player, alsa
            and the display for update.
        """
        if self._volume >= (0+self._volume_step):
            self._volume -= self._volume_step
        self._player.change_volume(self._volume)
        self._display.on_thread(self._display.display_volume, self._volume)

    def check_radio_info(self):
        """
            If the radio_info_check_interval is reached, 
            if a module is available for this radio, 
            and if metadata can be downloaded, then it retrieves 
            this new info and notify the display for update. 
        """
        # Check if info available
        if not self._queue.empty():
            infos = self._queue.get()
            if len(infos) > 0: # If some infos have been collected
                if infos != self._previous_info: # And if this info is different from the current one (currently displayed)
                    print ("New info available : "+infos)
                    self._display.on_thread(self._display.update_radio_info, infos)
                    self._previous_info = infos # Save this info as the current info for next check
            else:
                self._display.on_thread(self._display.update_radio_info, None)
        elif time.time() - self._last_check > self._radio_info_check_interval: # Run only if it is time to check (defined by the radio_info_check_interval param)
            self._last_check = time.time()
            #self._threads.append(threading.Thread(target=self.__get_info_async))
            threading.Thread(target=self.__get_info_async).start()

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

    def __get_media_type(self):
        return self._radios[self._indice].media_type

    def __get_info_async(self):
        try:
            infos = ""
            if self._radios[self._indice].extractor_module_name.lower() == "vlc":
                infos = self._player.get_infos()
            else:
                module = self._radios[self._indice].get_module() # Get the module related to this radio
                if module is not None: # If a module is available
                    self._lock.acquire()
                    if module.retrieve_current_metadata(): # If metadata are available at this time
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
                        if len(artist) > 0 and (len(title) > 0 or len(interpreter) > 0):
                            infos += " - "
            
                        infos += title
                        if len(title) > 0 and len(interpreter) > 0:
                            infos += " - "
            
                        infos += interpreter
                    self._lock.release() 
            if len(infos) > 0:
                self._queue.put(infos)
        except Exception as e:
            print (str(e))
