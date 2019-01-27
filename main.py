import sys
import json
import serial
import RPi.GPIO as GPIO
import time
from displayManager import DisplayManager
from configLoader import ConfigLoader
from configLoader import ConfigurationFileException
from radioManager import RadioManager
from playerManager import PlayerManager
from radio import Radio


##############################
### GLOBAL VARS
##############################

configfile = '/home/pi/venvs/radiobot/config.json'
asked_for_exit = -1

# Modules
displayManager = None
configLoader = None
radioManager = None
playerManager = None

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

def init_radiobot():
    global displayManager,configLoader,radioManager,playerManager
    # Loading configuration file
    try:
        configLoader = ConfigLoader(configfile)
        configLoader.parse_config_file()
    except ConfigurationFileException as e:
        print ("Invalid configuration : " + str(e))
        print ("Exciting.")
        sys.exit(2)
    except Exception:
        print ("Cannot load configuration file. Check file path or syntax.")
        print ("Exciting.")
        sys.exit(2)

    # Loading display manager
    displayManager = DisplayManager(serial.Serial(configLoader.serial_device,configLoader.serial_baud_rate,timeout=1), configLoader.name, configLoader.volume_timer, configLoader.scroll_time_interval, configLoader.scroll_time_pause)

    # Loading player
    playerManager = PlayerManager(configLoader.default_volume)

    # Loading the radio manager
    radioManager = RadioManager(configLoader.radios, configLoader.default_volume, configLoader.volume_step, playerManager, displayManager)
    
    # Loading GPIO configuration
    configure_GPIO()

    # Starting first radio
    radioManager.play_radio()


##############################
### CALLBACK FUNCTIONS
##############################

def volume_up_callback(channel):
    radioManager.volume_up()

def volume_down_callback(channel):
    radioManager.volume_down()

def next_radio_callback(channel):
    radioManager.next()

def previous_radio_callback(channel):
    radioManager.previous()


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
    print("Radiobot (v0.1)")
    print("Written by Sylvain Benech")
    print("(sylvain.benech@gmail.com)")
    print()

    # Init radiobot 
    init_radiobot()

    # Start first radio
    try:
        while asked_for_exit != 0:
            displayManager.update_display()
            time.sleep(0.1)
    except KeyboardInterrupt:
        clean_exit()

if __name__== "__main__":
    main()

