# External imports
import sys
from configLoader import ConfigLoader

def main(config_file):
    print("Radiobot (v1.0)")
    print("Written by Chuck182")
    
    try:
        cl = ConfigLoader(config_file)
        cl.parse_config_file()   
    except Exception as e:
        print ("Invalid configuration : "+ str(e))

if __name__== "__main__":
    if len(sys.argv) <= 1:
        print ("ERROR")
        sys.exit(2)
    main(sys.argv[1])
