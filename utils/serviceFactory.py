#factory.py

import zmq
import os


from red.config import config
from services import *
from red.services import *

#from services.keyinput import Keyinput

import logging

logger = logging.getLogger("kernel.ServiceFactory")

class ServiceMeta ():
    def __init__(self,socketName,serviceName, callback,context, poller):
        self.serviceName = serviceName;
        self.callback = callback
        self.socketName = socketName

        self.socket = context.socket(zmq.PAIR)
        logger.info("Binding on socket: " + socketName)
        self.socket.bind(socketName)
        
        self.service = serviceName(name=socketName, context=context)
        self.service.start();

        poller.register(self.socket, zmq.POLLIN)
        
        self.socket.send_json({"head":"echo"})
  
      
class ServiceFactory ():
    
    def __init__(self,module):
        self.module = module

    def createActiveServicesFromConfig(self):
        servicesToCreate = config.get('Services','Services').split(",")
        serviceList = dict()
      
        for service in servicesToCreate:
            logger.info("Creating service: " + service)
            socketName = config.get('Sockets', service)
            className = eval( service + "." +service.title())
            callback = eval("self.module.receive" + service.title() + "Message")
            serviceList[service] =(self.createService(socketName,className,callback))

        return serviceList

    
    def createService(self,socketName, servicename, callback ):
        return ServiceMeta(socketName, servicename, callback,self.module.context,self.module.poller)