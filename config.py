#config.py

import configparser
import sys, getopt, logging
from red.utils.run_once import run_once

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
        return default

init()
