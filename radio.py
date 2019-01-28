#!/usr/bin/env python
import importlib

class Radio():

    def __init__(self, long_name, short_name, stream_url, extractor_module):
        self._long_name = long_name
        self._short_name = short_name
        self._stream_url = stream_url
        self._extractor_module_name = extractor_module
        self._extractor_module = None

    @property
    def long_name(self):
        return self._long_name

    @property
    def short_name(self):
        return self._short_name

    @property
    def stream_url(self):
        return self._stream_url

    @property
    def extractor_module_name(self):
        return self._extractor_module_name

    def get_module(self):
        if self._extractor_module is None and self._extractor_module_name is not None:
            try:
                lib = importlib.import_module(self.extractor_module_name)
                self._extractor_module = lib.RadioMetadataExtractor()
            except Exception as e:
                print (e)
                self._extractor_module = None
        return self._extractor_module
