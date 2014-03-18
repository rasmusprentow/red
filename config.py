#config.py

import configparser

### Load config
config = configparser.ConfigParser()
config.read("config/init.conf")

global config