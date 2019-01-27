#!/usr/bin/env python
import time
import serial


class DisplayManager():
    VOLUME_PREFIX = "Volume "
    HALT = 1
    RADIO = 2

    def __init__(self, lcd, name, vol_timer, scroll_interval, scroll_pause):
        self._lcd = lcd
        self._name = name
        self._volume_timer = vol_timer
        self._scroll_interval = scroll_interval
        self._scroll_pause = scroll_pause
        self._radio_short_name = None
        self._radio_long_name = None
        self._volume = None
        self._radio_info = None
        self._radio_info_length = 0
        self._radio_info_indice = 0
        self._volume_start_time = None
        self._scroll_start_time = None
        self._mode = DisplayManager.HALT
        self._volume_displayed = False
        self.configure_lcd()
        self.display_halt_message()

    def configure_lcd(self):
        self._lcd.write([0xFE, 0x52]) #Disable autoscroll
    
    def close(self):
        self.display_halt_message()
        self._lcd.close()

    def display_halt_message(self):
        self._mode = DisplayManager.HALT
        self.set_full_text(self._name)

    def clear_lcd_screen(self):
        self._lcd.write([0xFE, 0x58])
        time.sleep(0.01)

    def set_full_text(self, text):
        if isinstance(text, str):
            self.clear_lcd_screen()
            self._lcd.write(text.encode())
            time.sleep(0.01)

    def update_bottom_text(self, text):
        if isinstance(text, str):
            self._lcd.write([0xFE, 0x47, 1, 2])
            time.sleep(0.01)
            self._lcd.write(text.encode())
            time.sleep(0.01)

    def scroll_message(self):
        subtext = self._radio_info[self._radio_info_indice:min(self._radio_info_indice+16,self._radio_info_length)]
        self.update_bottom_text(subtext)
        self._radio_info_indice += 1
                

    def display_volume(self, vol):
        if isinstance(vol, int) and vol >= 0 and vol <= 100:
            volume_text = str(vol)
            if vol == 0:
                volume_text = "MIN"
            elif vol == 100:
                volume_text = "MAX"
            self.set_full_text(DisplayManager.VOLUME_PREFIX+volume_text)
            self._volume_displayed = True
            self._volume_start_time = time.time()

    def update_display(self):
        if self._volume_displayed:
            now = time.time()
            if (now - self._volume_start_time) >= self._volume_timer:
                self._volume_displayed = False
                if self._mode == DisplayManager.HALT:
                    self.display_halt_message()
                elif self._mode == DisplayManager.RADIO:
                    self._radio_info_indice = 0
                    self.update_radio(self._radio_short_name, self._radio_long_name)
        elif self._mode == DisplayManager.RADIO:
            if self._radio_info != None and self._radio_info_length > 16:
                now = time.time()
                if self._radio_info_indice == 1:
                    if now - self._scroll_start_time >= self._scroll_pause:
                        self.scroll_message()
                        self._scroll_start_time = time.time()
                elif self._radio_info_indice+16 > self._radio_info_length:
                    if now - self._scroll_start_time >= self._scroll_pause:
                        self._radio_info_indice = 0
                        self.scroll_message()
                        self._scroll_start_time = time.time()
                elif now - self._scroll_start_time >= self._scroll_interval:
                    self.scroll_message()
                    self._scroll_start_time = time.time()

    def update_radio(self, short_name, long_name):
        if isinstance(short_name, str) and isinstance(long_name, str):
            self._mode = DisplayManager.RADIO
            self._radio_short_name = short_name
            self._radio_long_name = long_name
            if self._radio_info == None:
                self.set_full_text(self._radio_long_name)
            else:
                self.set_full_text(self._radio_short_name)
                if self._radio_info_length <= 16:
                    self.update_bottom_text(self._radio_info)
                else:
                    self.scroll_message()
                    self._scroll_start_time = time.time()

    def update_radio_info(self, message): # Only if in RADIO mode
        if message == None:
            self._radio_info_length = 0
            self._radio_info_indice = 0
            self._radio_info = None
        elif self._mode == DisplayManager.RADIO and isinstance(message, str):
            self._radio_info = message.strip()
            self._radio_info_length = len(self._radio_info)
            self._radio_info_indice = 0
        self.update_radio(self._radio_short_name, self._radio_long_name)
