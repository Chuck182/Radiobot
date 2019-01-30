#!/usr/bin/env python
from radio import Radio
import json
import numbers

class ConfigurationFileException(Exception):
    """
        This exception class is raised from a ConfigLoader object when
        one setting does not follow the prerequisites for this setting.  
    """
    pass

class ConfigLoader():
    """
        This class is in charge of parsing the json configuration file, 
        checking all the parameters. It provides some getters to access
        parameters if all the parameters are following the requirements. 
    """
    def __init__(self, filename):
        self._filename = filename
        self._radios = []
        self._name = None
        self._halt_message = None
        self._volume_timer = None
        self._scroll_time_interval = None
        self._scroll_time_pause = None
        self._serial_device = None
        self._serial_baud_rate = None
        self._default_volume = None
        self._volume_step = None
        self._radio_info_check_interval = None
        self._full_radio_name_pause = None
        self._save_file_path = None
        self._saved_volume = None
        self._saved_radio = 0

    def parse_config_file(self):
        """
            This method parses the configuration file and 
            check that all parameters follow the prerequisites. 
        """
        with open(self._filename) as f: # Opening configuration file
            tree = json.load(f) # Parsing json content
            
            # Closing file
            f.close()
            
        # First, let's load the list of radios
        for radio in tree['radios']:
            # Load attributes
            long_name = radio['long_name'] 
            short_name = radio['short_name'] 
            stream_url = radio['stream_url'] 
            media_type = radio['type'] 
            module_name = None
            if 'module_name' in radio:
                module_name = radio['module_name']

            # Check radio attributes type
            if not isinstance(long_name, str):
                raise ConfigurationFileException("radios.radio.long_name must be a string")
            
            if not isinstance(short_name, str):
                raise ConfigurationFileException("radios.radio.short_name must be a string")
            
            if not isinstance(stream_url, str):
                raise ConfigurationFileException("radios.radio.stream_url must be a string")
            
            if not isinstance(media_type, str):
                raise ConfigurationFileException("radios.radio.type must be a string")
            
            if module_name is not None and not isinstance(module_name, str):
                raise ConfigurationFileException("radios.radio.module_name must be a string")

            # Check attribute value and size
            if len(long_name) > 32:
                raise ConfigurationFileException("radios.radio.long_name must not exceed 32 characters")
            
            if len(short_name) > 16:
                raise ConfigurationFileException("radios.radio.short_name must not exceed 16 characters")
           
            if media_type != "stream" and media_type != "folder":
                raise ConfigurationFileException("radios.radio.type must be either 'stream' or 'folder'")

            # Register new radio
            r = Radio(long_name, short_name, stream_url, media_type, module_name)
            self._radios.append(r)

        if len(self._radios) <= 0:
            raise ConfigurationFileException("No radio available.")

        # Then, load other mandatory properties
        self._name = tree['general']['name']
        self._halt_message = tree['general']['halt_message']
        self._default_volume = tree['general']['default_volume']
        self._volume_step = tree['general']['volume_step']
        self._volume_timer = tree['display']['volume_timer']
        self._scroll_time_interval = tree['display']['scroll_time_interval']
        self._scroll_time_pause = tree['display']['scroll_time_pause']
        self._serial_device = tree['display']['serial_device']
        self._serial_baud_rate = tree['display']['serial_baud_rate']
        self._radio_info_check_interval = tree['general']['radio_info_check_interval']
        self._full_radio_name_pause = tree['general']['full_radio_name_pause']
        self._save_file_path = tree['general']['save_file_path']

        # Check var type
        if not isinstance(self._name, str):
            raise ConfigurationFileException("general.name parameter must be a string")

        if not isinstance(self._halt_message, str):
            raise ConfigurationFileException("general.halt_message parameter must be a string")

        if not isinstance(self._default_volume, numbers.Number):
            raise ConfigurationFileException("general.default_volume parameter must be a number")
        
        if not isinstance(self._volume_step, numbers.Number):
            raise ConfigurationFileException("general.volume_step parameter must be a number")
        
        if not isinstance(self._volume_timer, numbers.Number):
            raise ConfigurationFileException("display.volume_timer parameter must be a number")
        
        if not isinstance(self._scroll_time_interval, numbers.Number):
            raise ConfigurationFileException("display.scroll_time_interval parameter must be a number")
        
        if not isinstance(self._scroll_time_pause, numbers.Number):
            raise ConfigurationFileException("display.scroll_time_pause parameter must be a number")
        
        if not isinstance(self._serial_device, str):
            raise ConfigurationFileException("display.serial_device parameter must be a string")
        
        if not isinstance(self._serial_baud_rate, numbers.Number):
            raise ConfigurationFileException("display.serial_baud_rate parameter must be a number")
        
        if not isinstance(self._radio_info_check_interval, numbers.Number):
            raise ConfigurationFileException("general.radio_info_check_interval parameter must be a number")
        
        if not isinstance(self._full_radio_name_pause, numbers.Number):
            raise ConfigurationFileException("general.full_radio_name_pause parameter must be a number")
        
        if not isinstance(self._save_file_path, str):
            raise ConfigurationFileException("general.save_file_path parameter must be a string")
        
        # Check var value and size
        if len(self._name) > 32:
            raise ConfigurationFileException("general.name must not exceed 32 characters")
        
        if len(self._halt_message) > 32:
            raise ConfigurationFileException("general.halt_message must not exceed 32 characters")
        
        if self._default_volume > 100 or self._default_volume < 0:
            raise ConfigurationFileException("general.default_volume must be between 0 and 100")
   
        if self._volume_step > 40 or self._volume_step <= 0: 
            raise ConfigurationFileException("general.volume_step must be between 1 and 40")
        
        if self._volume_timer < 0:
            raise ConfigurationFileException("display.volume_timer must be a positive value (in seconds)")

        if self._scroll_time_interval <= 0:
            raise ConfigurationFileException("display.scroll_time_interval must be a non-null positive value (in seconds)")

        if self._scroll_time_pause < 0:
            raise ConfigurationFileException("display.scroll_time_pause must be a positive value (in seconds)")
        
        if self._serial_baud_rate <= 0:
            raise ConfigurationFileException("display.serial_baud_rate must be a non-null positive value")
        
        if self._radio_info_check_interval <= 0:
            raise ConfigurationFileException("general.radio_info_check_interval must be a non-null positive value (in seconds)")

        if self._full_radio_name_pause < 0:
            raise ConfigurationFileException("general.full_radio_name_pause must be a positive value (in seconds)")

        # Now, let's try to load cached settings if exist
        self.load_cached_settings(self._save_file_path)

    def save_settings(self, volume, radio):
        """
            This method is called during program exit. 
            It saves volume level and radio selection to a cache file. 
            This allows restoring the program as it was before exit. 
        """
        try:
            f = open(self._save_file_path, "w+")
            f.write(str(volume)+'\n') # First line is volume
            f.write(str(radio)+'\n') # Second line is radio indice
            f.close()
        except:
            pass # To not crash the program if cannot save settings

    def load_cached_settings(self, file_path):
        """
            This method load the eventually previous cached settings.
            If exists, it loads volume level and radio indice from cached file.
        """
        try:
            f = open(file_path, "r")
            fl = f.readlines()
            if len(fl) >= 2:
                volume = int(fl[0])
                radio = int(fl[1])
                if volume >= 0 and volume <= 100:
                    self._saved_volume = volume
                if radio >= 0 and radio < len(self._radios):
                    self._saved_radio = radio
        except:
            self._saved_volume = None
            self._saved_radio = 0

    # Getters for all parameters
    @property
    def radios(self):
        """
            Getter for the list of radios
        """
        return self._radios

    @property
    def name(self):
        """
            Getter for the name property of the program. 
            This name is also displayed when no radios are launched.
        """
        return self._name

    @property
    def halt_message(self):
        """
            Getter for the halt_message property of the program. 
            This message is displayed during exit.
        """
        return self._halt_message

    @property
    def volume(self):
        """
            Getter for the volume parameter
            Returns default_volume or saved_volume if it exists
        """
        volume = self._default_volume
        if self._saved_volume is not None:
            volume = self._saved_volume
        return volume
    
    @property
    def radio_info_check_interval(self):
        """
            Getter for the radio_info_check_interval parameter
        """
        return self._radio_info_check_interval
    
    @property
    def full_radio_name_pause(self):
        """
            Getter for the full_radio_name_pause parameter
        """
        return self._full_radio_name_pause
    
    @property
    def volume_step(self):
        """
            Getter for the volume_step parameter
        """
        return self._volume_step
    
    @property
    def volume_timer(self):
        """
            Getter for the volume_timer parameter
        """
        return self._volume_timer

    @property
    def scroll_time_interval(self):
        """
            Getter for the scroll_time_interval parameter
        """
        return self._scroll_time_interval

    @property
    def scroll_time_pause(self):
        """
            Getter for the scroll_time_pause parameter
        """
        return self._scroll_time_pause

    @property
    def serial_device(self):
        """
            Getter for the serial_device parameter
        """
        return self._serial_device

    @property
    def serial_baud_rate(self):
        """
            Getter for the serial_baud_rate parameter
        """
        return self._serial_baud_rate
    
    @property
    def radio_indice(self):
        """
            Returns the radio indice of the first radio to launch (0 or saved settings value)
        """
        return self._saved_radio
