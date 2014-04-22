#factory.py
""" Defines classes for the service factory which creates services """

import zmq


from red.config import config


import logging, configparser, importlib

logger = logging.getLogger("kernel.ServiceFactory")


class ServiceMeta (): 
    """ Used to keep meta information of a service. """

    def __init__(self):
        self.socketName         = None  
        self.serviceName        = None
        self.socket             = None
        self.isSlaveService     = None
        self.isMasterService    = None
        self.service            = None
              
      
class ServiceFactory (object):
    
    def __init__(self,module):
        self.module = module
        try:
            self.masters = config.get('Services','masters').split(",")
        except configparser.NoOptionError:
            self.masters = ['']
            logger.warning("The 'masters' directory was missing in config")
        
        try: 
            self.slaves = config.get('Services','slaves').split(",")
        except configparser.NoOptionError:
            self.slaves = ['']
            logger.warning("The 'slaves' directory was missing in config")

    def createActiveServicesFromConfig(self):

        servicesToCreate = config.get('Services','Services').split(",")
        servicesToCreate += self.slaves
        servicesToCreate += self.masters 

        logger.info("Creating the following services: " + str(servicesToCreate)) 
  
        
        serviceList = dict()
      
        for service in servicesToCreate:
            
            if service == '' or service == None: 
                continue
            logger.info("Creating service: " + service)
            serviceList[service] = self.createService(service)

        return serviceList


    
    def createService(self, serviceName ):
        """ Returns a meta object """
        meta = ServiceMeta()
        
        meta.socketName = config.get('Sockets', serviceName)
        
        meta.serviceName = serviceName

        meta.socket = self.module.context.socket(zmq.PAIR)
        
        ServiceName = serviceName.capitalize()
        
        """ Determine if this is a slave service """
        meta.isSlaveService = meta.serviceName in self.slaves
        meta.isMasterService = meta.serviceName in self.masters
       
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


      
            module = None
            moduleName = "services." + serviceName
            logger.info("Importing " + moduleName)
            try: 
                module = importlib.import_module(moduleName) 
            except Exception as e: 
                try:
                    moduleName = "red.services." + serviceName
                    logger.info("Importing " + moduleName)
                    module = importlib.import_module(moduleName) 
                except Exception as e: 
                    logger.critical("The service '%s' did not exist as an service. Exception: %s" % (serviceName, str(e)))
            
            if module != None:
                serviceClass = getattr(module, ServiceName)
                meta.service = serviceClass(name=meta.socketName, context=self.module.context)
                meta.service.onCreate()
                meta.service.start();


        self.module.poller.register(meta.socket, zmq.POLLIN)
        
        if not (meta.isSlaveService):
            """ 
            We have really no idea whether the slave is active or not.
            The slave will tell os when it connects. 
            To connect the slave, someone must actually turn on a device
            Physically turn on a device. 
            """
           
            meta.socket.send_json({"head":"system_message", "data":"echo"})


        return meta