#config.py

import configparser
import logging
from red.utils.run_once import run_once
import os.path
from importlib import import_module

global config

processedConfigs = []

@run_once
def init_once():
    global config
    config = configparser.ConfigParser()
    pass

def initConfig (metaConfigFile, logger=None, recursion=5):
    '''
    Initialize configs based on metaConfigFile and logging to logger
    '''
    ### Load config
    global processedConfigs
    processedConfigs = []
    if logger == None:
        logger = logging.getLogger("dummy")
    if not os.path.isfile(metaConfigFile):
        print ("Meta-config file: " + metaConfigFile + " not found")
        print ("Here is what you might need:")
        print ("echo '[logging.config]\n\
mandatory=config/logging.conf\n\
read=fileConfig\n\
[config]\n\
mandatory=config/init.conf' > " + metaConfigFile)
        exit();
    metaConf = configparser.ConfigParser()
    metaConf.read(metaConfigFile)

    for section in metaConf.sections():
        logger.debug("Processing meta-config section: " + section)
        read = 'read'
        if(metaConf.has_option(section, 'read')):
            read = metaConf.get(section, 'read')
        if section in globals():
            conf = globals()[section]
        else:
            conf = import_module(section)
        if metaConf.has_option(section, 'mandatory'):
            for configFile in metaConf.get(section, "mandatory").split(','):
                if os.path.isfile(configFile):
                    logger.info("Reading mandatory config file: '" + configFile + "' for " + section)
                    readConfigFile(conf,configFile,read,logger,recursion)
                else:
                    logger.critical("Mandatory config file missing: '" + configFile + "' for " + section)
                    raise Exception("Mandatory config file missing: '" + configFile + "' for " + section)
            if(metaConf.has_option(section,'optional')):
                for configFile in metaConf.get(section, "optional").split(','):
                    if os.path.isfile(configFile):
                        logger.info("Reading optional config file: '" + configFile + "' for " + section)
                        readConfigFile(conf,configFile,read,logger,recursion)
                    else:
                        logger.warning("Optional config file missing: '" + configFile + "' for " + section)
        else:
            logger.critical("The 'mandatory' option was missing in meta-config section '" + section + "'")
            raise Exception("The 'mandatory' option was missing in meta-config section '" + section + "'")

    

def readConfigFile(config, f, readMethod, logger, recurse=5):
    '''Read a configuration file into config'''
    global processedConfigs
    processedConfigs.append(f)
    method = getattr(config,readMethod)
    method(f)
    if recurse > 0 and hasattr(config,'has_option') and hasattr(config,'get'):
        if config.has_option("Configs","mandatory"):
            for subConfigFile in config.get("Configs","mandatory").split(','):
                if os.path.isfile(subConfigFile):
                    if subConfigFile not in processedConfigs:
                        logger.info("Reading mandatory config file: '" + subConfigFile + "'")
                        readConfigFile(config,subConfigFile,readMethod,logger,recurse-1)
                else:
                    logger.critical("Mandatory config file missing: '" + subConfigFile + "'")
                    raise Exception("Mandatory config file missing: '" + subConfigFile + "'")
        if config.has_option("Configs","optional"):
            for subConfigFile in config.get("Configs","optional").split(','):
                if os.path.isfile(subConfigFile):
                    if subConfigFile not in processedConfigs:
                        logger.info("Reading optional config file: '" + subConfigFile + "'")
                        readConfigFile(config,subConfigFile,readMethod,logger,recurse-1)
                else:
                    logger.warning("Optional config file missing: '" + subConfigFile + "'")

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

init_once()
