#config.py

import configparser

global config

### Load config
config = configparser.ConfigParser()
config.read("config/init.conf")