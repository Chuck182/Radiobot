#!/usr/bin/env python
from radio import Radio
import json

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

    def parse_config_file(self):
        with open(self._filename) as f:
            tree = json.load(f)
            # Load radios
            for radio in tree['radios']:
                r = Radio(radio['long_name'], radio['short_name'], radio['stream_url'], None)
                if 'module_name' in radio:
                    r.extractor_module_name = radio['module_name']
                self._radios.append(r)

            if len(self._radios) <= 0:
                raise ConfigurationFileException("No radio available.")

            # Load other mandatory properties
            self._name = tree['general']['name']
            self._default_volume = tree['general']['default_volume']
            self._volume_step = tree['general']['volume_step']
            self._volume_timer = tree['display']['volume_timer']
            self._scroll_time_interval = tree['display']['scroll_time_interval']
            self._scroll_time_pause = tree['display']['scroll_time_pause']
            self._serial_device = tree['display']['serial_device']
            self._serial_baud_rate = tree['display']['serial_baud_rate']
           
            if not isinstance(self._name,str):
                raise ConfigurationFileException("general.name parameter must be a string")

            # Closing file
            f.close()

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
