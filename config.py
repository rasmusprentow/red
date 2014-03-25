#config.py

import configparser
import sys, getopt, logging

global config

logger = logging.getLogger('kernel')

### Load config
config = configparser.ConfigParser()


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
