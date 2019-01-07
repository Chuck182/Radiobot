import sys
import vlc
import json
from pprint import pprint
import RPi.GPIO as GPIO
import time
from subprocess import call
import serial

##############################
### GLOBAL VARS
##############################

configfile = '/home/pi/venvs/radiobot/radiobot-config.json'
configuration = {}
radios = []
selected_radio = 0
number_of_radios = 0
player = None
instance = None
lcd = None
no_radio_display_text = "Pas de radio"
asked_for_exit = -1
current_volume = 60
volume_step = 5
volume_display_timer = 3
volume_display_remaining = -1

##############################
### iCUSTOM CLASSES
##############################

class Radio:
    def __init__(self, d, u):
        self._display_name = d
        self._url = u

    @property
    def display_name(self):
        return self._display_name

    @property
    def url(self):
        return self._url

##############################
### STARTUP FUNCTIONS
##############################

def configure_GPIO():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(22, GPIO.FALLING, callback=volume_up_callback, bouncetime=200)
    GPIO.add_event_detect(23, GPIO.FALLING, callback=volume_down_callback, bouncetime=200)
    GPIO.add_event_detect(24, GPIO.FALLING, callback=next_radio_callback, bouncetime=200)
    GPIO.add_event_detect(25, GPIO.FALLING, callback=previous_radio_callback, bouncetime=200)

def configure_vlc_player():
    global player, instance
    instance = vlc.Instance("--no-video --aout=alsa")
    player = instance.media_player_new()
    player.audio_set_volume(current_volume)

def configure_alsamixer():
    call(["amixer", "-M", "-q", "set", "PCM", str(current_volume)+"%"])

def set_listener():
    with Listener(on_press=on_key_pressed) as listener:
        listener.join()

def load_configuration_file():
    global configuration,radios,number_of_radios
    try:
        with open(configfile) as f:
            configuration = json.load(f)
#            pprint(configuration)
            for radio in configuration['radios']:
                radios.append(Radio(radio['display_name'], radio['url']))
    except:
        print("Fatal error. Cannot load configuration file. Exiting.")
        sys.exit(2)

    number_of_radios = len(radios)
    print (str(len(radios))+" radios have been loaded.")

def configure_lcd():
    global lcd
    lcd = serial.Serial('/dev/ttyACM0',9600, timeout=1)

##############################
### CALLBACK FUNCTIONS
##############################

def volume_up_callback(channel):
    global current_volume
    if current_volume <= (100-volume_step):
        current_volume += volume_step
    update_current_volume()

def volume_down_callback(channel):
    global current_volume
    if current_volume >= (0+volume_step):
        current_volume -= volume_step
    update_current_volume()

def next_radio_callback(channel):
    global selected_radio
    selected_radio += 1
    if (selected_radio >= len(radios)):
        selected_radio = 0
    update_current_radio()

def previous_radio_callback(channel):
    global selected_radio
    selected_radio -= 1
    if (selected_radio < 0):
        selected_radio = len(radios)-1
    update_current_radio()

##############################
### FUNCTIONAL FUNCTIONS
##############################

def update_current_radio():
    global player, instance
    if player is None:
        configure_vlc_player()
    else:
        player.stop()
    display_radio_name()
    if (number_of_radios > 0):
#        player = vlc.MediaPlayer(radios[selected_radio].url)
#        player.play()
        media = instance.media_new(radios[selected_radio].url)
        player.set_media(media)
        player.play()

def update_current_volume():
    global volume_display_remaining
    player.audio_set_volume(current_volume)
    call(["amixer", "-M", "-q", "set", "Digital", str(current_volume)+"%"])
    volume = "Volume "+str(current_volume)
    print(volume)
    display_text_on_lcd(volume)
    volume_display_remaining = volume_display_timer

def display_radio_name():
    if (number_of_radios > 0):
        print(radios[selected_radio].display_name)
        display_text_on_lcd(radios[selected_radio].display_name)
    else:
        print (no_radio_display_text)
        display_text_on_lcd(no_radio_display_text)

def clear_lcd_screen():
    ## Clear screen
    lcd.write([0xFE, 0x58])
    time.sleep(0.01)

def display_text_on_lcd(text):
    clear_lcd_screen()
    lcd.write(text.encode())
    time.sleep(0.01)

##############################
### MAIN FUNCTION
##############################

def clean_exit():
    print()
    print("Cleaning GPIO")
    GPIO.cleanup()
    print("Cleaning LCD")
    clear_lcd_screen()
    print("Exiting.")
    sys.exit(0)

def main():
    global volume_display_remaining
    print("Radiobot (v0.1)")
    print("Written by Sylvain Benech")
    print("(sylvain.benech@gmail.com)")
    print()

    # Start modules
    load_configuration_file()
    configure_GPIO()
    configure_lcd()
    configure_vlc_player()
    configure_alsamixer() 

    # Start first radio
    update_current_radio()
    try:
        while asked_for_exit != 0:
            time.sleep(1)
            if volume_display_remaining>0:
                volume_display_remaining -= 1
            elif volume_display_remaining == 0:
                volume_display_remaining -= 1
                display_radio_name()
    except KeyboardInterrupt:
        clean_exit()

if __name__== "__main__":
    main()

