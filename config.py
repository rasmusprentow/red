#config.py

import configparser
import sys, getopt, logging

global config

# Read command line args
#myopts, args = getopt.getopt(sys.argv[1:],"c:")
 

#for o, a in myopts:
#    if o == '-c':
#        conffile=a
logger = logging.getLogger('kernel')

### Load config
config = configparser.ConfigParser()


def get_config(config, section, option, ctype=str, default=None): 
    """ Auxilliary method"""
    if default is None: 
        ret = config.get(section, option) 
    else: 
        confdict = config.__dict__.get('_sections') 
        ret = confdict.get(section).get(option, default) 
    return ctype(ret) 