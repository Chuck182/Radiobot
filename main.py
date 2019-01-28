# External imports
import sys
import json
import serial
import RPi.GPIO as GPIO
import time
import signal

# Internal modules
from displayManager import DisplayManager
from configLoader import ConfigLoader
from configLoader import ConfigurationFileException
from radioManager import RadioManager
from playerManager import PlayerManager
from radio import Radio

##############################
### GLOBAL VARS
##############################

# Modules
displayManager = None
configLoader = None
radioManager = None
playerManager = None

##############################
### STARTUP FUNCTIONS
##############################

# Raspberry pi GPIO initialization
def configure_GPIO():
    """
        Initialize the used GPIO pins and set listeners for these pins.
        Those GPIO pins are used to connect buttons 
        (volume up/down and radio previous/next)
    """
    GPIO.setmode(GPIO.BCM) # we are using gpio BCM notation
    GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set this gpio pin as input, with a pull-down resistor
    GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(22, GPIO.FALLING, callback=volume_up_callback, bouncetime=200) # Adding listener on PIN state change, triggered by falling signal  and 200 ms of pause to prevent bouncing effects)
    GPIO.add_event_detect(23, GPIO.FALLING, callback=volume_down_callback, bouncetime=200)
    GPIO.add_event_detect(24, GPIO.FALLING, callback=next_radio_callback, bouncetime=200)
    GPIO.add_event_detect(25, GPIO.FALLING, callback=previous_radio_callback, bouncetime=200)

# Global initialisation method
def init_radiobot(config_file):
    """
        Initialize the different radiobot components :
        - Configuration loader, which will parse the json conf file and check
          attributes conformity
        - Display Manager, which is in charge of controling the LCD screen 
          and all the display behaviors (timers and so on)
        - Player manager, which is in charge of controlling VLC and Alsa 
          (starting and stoping network streams, applying volume modifications)
        - Radio manager, which is the overall manager, in charge of radio 
          selection and communication between the display and the player. 
    """
    global displayManager,configLoader,radioManager,playerManager
    try: # Trying to load configuration file
        configLoader = ConfigLoader(config_file)
        configLoader.parse_config_file()
        print ("Configuration file loaded successfully")
    except Exception as e:
        print ("Invalid configuration : " + str(e))
        print ("Exciting.")
        sys.exit(2)

    # Loading display manager
    displayManager = DisplayManager(serial.Serial(configLoader.serial_device,configLoader.serial_baud_rate,timeout=1), configLoader.name, configLoader.volume_timer, configLoader.scroll_time_interval, configLoader.scroll_time_pause)

    # Loading player
    playerManager = PlayerManager(configLoader.volume)

    # Loading the radio manager
    radioManager = RadioManager(configLoader.radios, configLoader.volume, configLoader.volume_step, configLoader.radio_info_check_interval, configLoader.full_radio_name_pause, configLoader.radio_indice, playerManager, displayManager)
    
    # Loading GPIO configuration
    configure_GPIO()

    # Starting first radio
    radioManager.play_radio()

##############################
### CALLBACK FUNCTIONS
##############################

def volume_up_callback(channel):
    """"
        Callback function, called when the volume UP button is pressed
    """
    radioManager.volume_up()

def volume_down_callback(channel):
    """"
        Callback function, called when the volume DOWN button is pressed
    """
    radioManager.volume_down()

def next_radio_callback(channel):
    """"
        Callback function, called when the radio NEXT button is pressed
    """
    radioManager.next()

def previous_radio_callback(channel):
    """"
        Callback function, called when the radio PREVIOUS button is pressed
    """
    radioManager.previous()


##############################
### MAIN FUNCTION
##############################

def clean_exit():
    """
        This function closes the program in a proper way.
        It stop GPIO and LCD and saves volume and radio settings.
    """
    print()
    print("Cleaning GPIO")
    GPIO.cleanup()
    print("Cleaning LCD")
    displayManager.close()
    # Saving settings
    print("Saving current settings to cache")
    configLoader.save_settings(radioManager.get_current_volume(), radioManager.get_current_radio_indice())
    print("Exiting.")
    sys.exit(0)

def sigterm_callback(signal, frame):
    """
        Callback function, called when SIGTERM is triggered
    """
    clean_exit()


def main(config_file):
    """
        Main method called on program startup. 
        Takes the config file path (program arguement)
        This method run the init function and then 
        loop on refresh methods until program termination.
    """
    print("Radiobot (v1.0)")
    print("Written by Chuck182")
    print()

    # Setting signal listener (SIGTERM)
    signal.signal(signal.SIGTERM, sigterm_callback)

    # Initializing radiobot 
    init_radiobot(config_file)

    # While there are no process interruptions, loop on display update functions 
    try:
        while True:
            displayManager.update_display() # To update display (i.e. scroll radio info or end of volume level display)
            radioManager.check_radio_info() # Check if new radio info is available, and notify display if needed
            time.sleep(0.05)
    except KeyboardInterrupt:
        clean_exit()

if __name__== "__main__":
    if len(sys.argv) <= 1:
        print ("Missing configuration file path")
        print ("Exiting.")
        sys.exit(2)
    main(sys.argv[1])
