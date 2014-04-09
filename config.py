#config.py

import configparser
import sys, getopt, logging
from red.utils.run_once import run_once
import string
import os.path

global config
global logger

@run_once
def init ():
    global config
    global logger
    logger = logging.getLogger('kernel')

    ### Load config
    config = configparser.ConfigParser()
    config.read('config/init.conf')

    if config.has_option("Configs","mandatories"):
        for f in string.split(config.get("Configs","mandatories")):
            config.read(f)

    if config.has_option("Configs","optionals"):
        for f in string.split(config.get("Configs","optionals")):
            if os.path.isfile(f):
                config.read(f)


def get_config(config, section, option, ctype=str, default=None): 
    """ Auxilliary method"""
    try:
        if default is None: 
            ret = config.get(section, option) 
        else: 
            confdict = config.__dict__.get('_sections') 
            ret = confdict.get(section).get(option, default) 
        return ctype(ret) 
    except:
        return ctype(default)

init()
