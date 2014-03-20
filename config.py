#config.py

import configparser
import sys, getopt, logging

global config


conffile='config/init.conf'
 
# Read command line args
myopts, args = getopt.getopt(sys.argv[1:],"c:")
 

for o, a in myopts:
    if o == '-c':
        conffile=a

logger = logging.getLogger('kernel')
logger.info('Reading config; ' + conffile)
### Load config
config = configparser.ConfigParser()
config.read(conffile)