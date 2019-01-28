#!/usr/bin/env python
import time
import serial
import unidecode

class DisplayManager():
    """
        This class is in charge of controlling the lcd screen and 
        all the timers related to things displayed on this screen. 
    """
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
        self._ip_start_time = None
        self._scroll_start_time = None
        self._mode = DisplayManager.HALT
        self._volume_displayed = False
        self._ip_displayed = False
        self.configure_lcd()
        self.display_halt_message()

    def configure_lcd(self):
        """
            Initial configuration of the LCD screen
        """
        self._lcd.write([0xFE, 0x52]) # Disable autoscroll
        time.sleep(0.01)
        self._lcd.write([0xFE, 0xD0, 0, 180, 130]) # Set backlight color
        time.sleep(0.01)
        self._lcd.write([0xFE, 0x99, 250]) # Set brightness
        time.sleep(0.01)
        self._lcd.write([0xFE, 0x50, 180]) # Set contrast
        time.sleep(0.01)
        self._lcd.write([0xFE, 0x58]) # Cleaning LCD screen
        time.sleep(0.01)
        self._lcd.write([0xFE, 0x40]) # Set startup message
        self._lcd.write(self._name.encode()) # Set startup message
        time.sleep(0.01)

    
    def close(self):
        """
            Properly closing the serial connection on program exiting.
        """
        self.display_halt_message()
        self._lcd.close()

    def display_halt_message(self):
        """
            When no radios are playing, this method can be called 
            to display the name of the program instead.
        """
        self._mode = DisplayManager.HALT
        self.set_full_text(self._name)

    def clear_lcd_screen(self):
        """
            To empty the LCD screen content, 
            and set the cursor to the first character (1x1)
        """
        self._lcd.write([0xFE, 0x58])
        time.sleep(0.01)

    def set_full_text(self, text):
        """
            To write a text from the first character. If more than 16 chars, 
            it will also use the second line to display the end of the text.
            It clears the LCD before writing. 
        """
        if isinstance(text, str):
            self.clear_lcd_screen()
            self._lcd.write(text.encode())
            time.sleep(0.01)

    def update_bottom_text(self, text):
        """
            This method displays a text only on the second line. The text cannot 
            be more than 16 chars long. 
        """
        if isinstance(text, str):
            self._lcd.write([0xFE, 0x47, 1, 2])
            time.sleep(0.01)
            self._lcd.write(text.encode())
            time.sleep(0.01)

    def scroll_message(self):
        """
            This methods update the second line from one step of scrolling.
        """
        subtext = self._radio_info[self._radio_info_indice:min(self._radio_info_indice+16,self._radio_info_length)]
        self.update_bottom_text(subtext)
        self._radio_info_indice += 1
                

    def display_volume(self, vol):
        """
            This method displays the volume on the screen, and initialize 
            the volume timer. The update_display method will clear the 
            volume info at the end of the timer and set the radio name instead.
        """
        if isinstance(vol, int) and vol >= 0 and vol <= 100:
            self._volume_start_time = time.time()
            volume_text = str(vol)
            if vol == 0:
                volume_text = "MIN"
            elif vol == 100:
                volume_text = "MAX"
            self.set_full_text(DisplayManager.VOLUME_PREFIX+volume_text)
            self._volume_displayed = True

    def update_display(self):
        """
            This method has two main purposes :
              - If volume is displayed, checking timer and restoring 
                previous display if reached
              - If radio is displayed and radio_info available,
                manage the scrolling of the info (one step at each call)
        """
        if self._ip_displayed: # If the IP is currently displayed
            now = time.time()
            if (now - self._ip_start_time) >= self._volume_timer: # and if the timer is reached (we have to clean the display and restore the previous content)
                self._ip_displayed = False
                if self._mode == DisplayManager.HALT: # If the previous content was the HALT message, let's restore it
                    self.display_halt_message()
                elif self._mode == DisplayManager.RADIO: # If it was the radio content (name + optionnaly info), restore it
                    self._radio_info_indice = 0
                    self.update_radio(self._radio_short_name, self._radio_long_name)
        elif self._volume_displayed: # If the volume is currently displayed
            now = time.time()
            if (now - self._volume_start_time) >= self._volume_timer: # and if the timer is reached (we have to clean the display and restore the previous content)
                self._volume_displayed = False
                if self._mode == DisplayManager.HALT: # If the previous content was the HALT message, let's restore it
                    self.display_halt_message()
                elif self._mode == DisplayManager.RADIO: # If it was the radio content (name + optionnaly info), restore it
                    self._radio_info_indice = 0
                    self.update_radio(self._radio_short_name, self._radio_long_name)
        elif self._mode == DisplayManager.RADIO: # If we are in radio mode
            if self._radio_info != None and self._radio_info_length > 16: # And a radio info is available AND scrolling is needed (because radio info more than 16 chars)
                now = time.time()
                if self._radio_info_indice == 1: # If we are at the beginning of the scrolling, let's wait for a pause before starting scrolling
                    if now - self._scroll_start_time >= self._scroll_pause:
                        self.scroll_message()
                        self._scroll_start_time = time.time()
                elif self._radio_info_indice+16 > self._radio_info_length: # The same at the end, let's make a pause before starting again the scroll from the beginning
                    if now - self._scroll_start_time >= self._scroll_pause:
                        self._radio_info_indice = 0
                        self.scroll_message()
                        self._scroll_start_time = time.time()
                elif now - self._scroll_start_time >= self._scroll_interval: # If in the middle of the scrolling, let's scroll of one step.
                    self.scroll_message()
                    self._scroll_start_time = time.time()

    def update_radio(self, short_name, long_name):
        """
            Update the radio title and eventually the radio info if available.
            Can be called after radio change, or just if the radio info must be 
            updated.
        """
        if isinstance(short_name, str) and isinstance(long_name, str):
            self._mode = DisplayManager.RADIO
            self._radio_short_name = short_name
            self._radio_long_name = long_name
            if self._radio_info == None: # If no info available, let's write the full name of the radio (using the two lines if needed)
                self.set_full_text(self._radio_long_name)
            else: # If radio info is available, we have to write the radio name on the first line only (short name) and use the second line to scroll the radio info
                self.set_full_text(self._radio_short_name)
                if self._radio_info_length <= 16:
                    self.update_bottom_text(self._radio_info)
                else:
                    self.scroll_message()
                    self._scroll_start_time = time.time()

    def update_radio_info(self, message): # Only if in RADIO mode
        """
            This method updates the text content of a radio info. It clears
            the radio info content if no info available, or set the new text.
        """
        if message == None: # If now, no message is available (end of a song for example, or radio without info available)
            self._radio_info_length = 0
            self._radio_info_indice = 0
            self._radio_info = None
        elif self._mode == DisplayManager.RADIO and isinstance(message, str): # If info is available, replacing UNICODE chars by ASCII chars and stripping the string.
            self._radio_info = unidecode.unidecode(message.strip())
            self._radio_info_length = len(self._radio_info)
            self._radio_info_indice = 0
        self.update_radio(self._radio_short_name, self._radio_long_name) # Finally calls the update_radio method to really update the display (this current method only updates the text var)
    
    def display_ip_address(self, ip_address):
        """
            This method displays the IP address of the RPI
            on the screen, and initialize the ip_address_timer. 
            The update_display method will clear the 
            ip_address at the end of the timer and set the radio name instead.
        """
        if isinstance(ip_address, str) and len(ip_address) <= 16:
            text = "Adresse IP      "+ip_address
            self.set_full_text(text)
            self._ip_displayed = True
            self._ip_start_time = time.time()
