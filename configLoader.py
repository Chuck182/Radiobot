#!/usr/bin/env python
from radio import Radio
import json
import numbers

class ConfigurationFileException(Exception):
    pass

class ConfigLoader():
    def __init__(self, filename):
        self._filename = filename
        self._radios = []
        self._name = None
        self._volume_timer = None
        self._scroll_time_interval = None
        self._scroll_time_pause = None
        self._serial_device = None
        self._serial_baud_rate = None
        self._default_volume = None
        self._volume_step = None
        self._radio_info_check_interval = None
        self._full_radio_name_pause = None

    def parse_config_file(self):
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
            
            if module_name is not None and not isinstance(module_name, str):
                raise ConfigurationFileException("radios.radio.module_name must be a string")

            # Check attribute value and size
            if len(long_name) > 32:
                   raise ConfigurationFileException("radios.radio.long_name must not exceed 32 characters")
            
            if len(short_name) > 16:
                   raise ConfigurationFileException("radios.radio.short_name must not exceed 16 characters")
            
            # Register new radio
            r = Radio(long_name, short_name, stream_url, module_name)
            self._radios.append(r)

        if len(self._radios) <= 0:
            raise ConfigurationFileException("No radio available.")

        # Then, load other mandatory properties
        self._name = tree['general']['name']
        self._default_volume = tree['general']['default_volume']
        self._volume_step = tree['general']['volume_step']
        self._volume_timer = tree['display']['volume_timer']
        self._scroll_time_interval = tree['display']['scroll_time_interval']
        self._scroll_time_pause = tree['display']['scroll_time_pause']
        self._serial_device = tree['display']['serial_device']
        self._serial_baud_rate = tree['display']['serial_baud_rate']
        self._radio_info_check_interval = tree['general']['radio_info_check_interval']
        self._full_radio_name_pause = tree['general']['full_radio_name_pause']

        # Check var type
        if not isinstance(self._name, str):
            raise ConfigurationFileException("general.name parameter must be a string")

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
        
        # Check var value and size
        if len(self._name) > 32:
            raise ConfigurationFileException("general.name must not exceed 32 characters")
        
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


    # Getters for all parameters
    @property
    def radios(self):
        return self._radios

    @property
    def name(self):
        return self._name

    @property
    def default_volume(self):
        return self._default_volume
    
    @property
    def radio_info_check_interval(self):
        return self._radio_info_check_interval
    
    @property
    def full_radio_name_pause(self):
        return self._full_radio_name_pause
    
    @property
    def volume_step(self):
        return self._volume_step
    
    @property
    def volume_timer(self):
        return self._volume_timer

    @property
    def scroll_time_interval(self):
        return self._scroll_time_interval

    @property
    def scroll_time_pause(self):
        return self._scroll_time_pause

    @property
    def serial_device(self):
        return self._serial_device

    @property
    def serial_baud_rate(self):
        return self._serial_baud_rate
