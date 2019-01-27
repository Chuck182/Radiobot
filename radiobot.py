import sys
import vlc
import json
from pprint import pprint
import RPi.GPIO as GPIO
import time
from subprocess import call
import serial
from displayManager import DisplayManager

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
displayManager = None
asked_for_exit = -1
current_volume = 60
volume_step = 5

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
    instance = vlc.Instance("--no-video --aout=alsa --metadata-network-access")
    player = instance.media_player_new()
    player.audio_set_volume(current_volume)

def configure_alsamixer():
    call(["amixer", "-M", "-q", "set", "Digital", str(current_volume)+"%"])

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
#        media.parse_with_options(vlc.MediaParseFlag.network, 0)
#        mediaManager = media.event_manager()
#        mediaManager.event_attach(vlc.EventType.MediaParsedChanged,test_callback,player)
#        print ("Info : "+str(media.get_meta(vlc.Meta.NowPlaying)))


def update_current_volume():
    global volume_display_remaining
    player.audio_set_volume(current_volume)
    call(["amixer", "-M", "-q", "set", "Digital", str(current_volume)+"%"])
    print ("Volume "+str(current_volume))
    displayManager.display_volume(current_volume)

def display_radio_name():
    if (number_of_radios > 0):
        print(radios[selected_radio].display_name)
        displayManager.update_radio(radios[selected_radio].display_name, radios[selected_radio].display_name)
    else:
        displayManager.display_halt_message()

##############################
### MAIN FUNCTION
##############################

def clean_exit():
    print()
    print("Cleaning GPIO")
    GPIO.cleanup()
    print("Cleaning LCD")
    displayManager.close()
    print("Exiting.")
    sys.exit(0)

def main():
    global displayManager
    print("Radiobot (v0.1)")
    print("Written by Sylvain Benech")
    print("(sylvain.benech@gmail.com)")
    print()

    # Start modules
    load_configuration_file()
    configure_GPIO()
    displayManager = DisplayManager(serial.Serial('/dev/ttyACM0',9600,timeout=1), "    Radiobot", 2, 0.5, 2)
    configure_vlc_player()
    configure_alsamixer() 

    # Start first radio
    update_current_radio()
    try:
        while asked_for_exit != 0:
            displayManager.update_display()
            time.sleep(0.1)
    except KeyboardInterrupt:
        clean_exit()

if __name__== "__main__":
    main()

