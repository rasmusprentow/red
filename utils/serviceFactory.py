#factory.py

import zmq
import os


from red.config import config
from services import *
from red.services import *

#from services.keyinput import Keyinput

import logging, configparser

logger = logging.getLogger("kernel.ServiceFactory")

class ServiceMeta (): pass
       
  
      
class ServiceFactory (object):
    
    def __init__(self,module):
        self.module = module

    def createActiveServicesFromConfig(self):

        servicesToCreate = config.get('Services','Services').split(",")
        try:
            servicesToCreate += config.get('Services','slaves').split(",")
        except configparser.NoOptionError:
            logger.warning("The 'slaves' directory was missing in config")

        try: 
            servicesToCreate += config.get('Services','masters').split(",")
        except configparser.NoOptionError:
            logger.warning("The 'slaves' directory was missing in config")

        logger.info("Creating the following services: " + str(servicesToCreate))
  
        
        serviceList = dict()
      
        for service in servicesToCreate:
            logger.info("Creating service: " + service)
            if service == '' or service == None: 
                continue
            serviceList[service] =self.createService(service)

        return serviceList


    
    def createService(self, serviceName ):

        meta = ServiceMeta()
        
        meta.socketName = config.get('Sockets', serviceName)
        
        meta.serviceName = serviceName
      
       
        meta.socket = self.module.context.socket(zmq.PAIR)
       
        

        """ Determine if this is a slave service """
        meta.isSlaveService = False
        try:
            meta.isSlaveService = meta.serviceName in config.get('Services','slaves')
        except configparser.NoOptionError:
            logger.warning("The 'slaves' directory was missing in config")

        """ Determine if this is a master service """
        meta.isMasterService = False
        try:
            meta.isMasterService = meta.serviceName in config.get('Services','masters')
        except configparser.NoOptionError:
            logger.warning("The 'masters' directory was missing in config")

        """ It cannot be both slave and master """
        assert not (meta.isSlaveService and meta.isMasterService)

        if  meta.isMasterService:
            """ You must connect to the master """
            logger.info("Connecting on socket: " + meta.socketName)
            meta.socket.connect(meta.socketName)
        else:
            """ We bind to normal and slave services """
            logger.info("Binding on socket: " + (meta.socketName))
            meta.socket.bind(meta.socketName)
            logger.info("Bound on socket: " + meta.socketName)
          
        if not (meta.isSlaveService or meta.isMasterService):
            """ Slaves and masters should never be started by us """
            logger.info("Starting service: " + str(serviceName))
            serviceClass = eval( serviceName + "." +serviceName.capitalize())
            meta.service = serviceClass(name=meta.socketName, context=self.module.context)
            meta.service.start();


        self.module.poller.register(meta.socket, zmq.POLLIN)
        
        if not (meta.isSlaveService):
            """ 
            We have really no idea whether the slave is active or not.
            The slave will tell os when it connects. 
            To connect the slave, someone must actually turn on a device
            Physically turn on a device. 
            """
           
            meta.socket.send_json({"head":"echo"})


        return meta