""" The kernel package contains the Kernel 
 Pylint: pylint2  red/kernel.py --disable=trailing-whitespace --disable=line-too-long --disable=no-member --disable=invalid-name
"""
import logging, logging.config
import zmq
import threading
import types
import re

from red.utils.serviceFactory import ServiceFactory
from red.config import config

logger = logging.getLogger("kernel")

import importlib


from red.utils.serviceFactory import ServiceFactory
from red.config import config, get_config

class Kernel(threading.Thread):
    """ The Kernel is the core of RED. It is "the controller" of everything """

    def __init__(self):
        super(Kernel, self).__init__()
       

        self.logger = logging.getLogger("kernel")

        self.context = zmq.Context()
        self.poller = zmq.Poller()
        
        self.services = ServiceFactory(self).createActiveServicesFromConfig()
        self._session = None
        self.activity = None
        self.running = True

    def receive(self, name, message):
        """ 
        Reveive method for any messages reeived from any service 
        The activity will get the message in its 'receive<service>Message' method

        """
        if message["head"] == "echo":
            self.logger.info("Received echo from " + name)             
        methodName = "receive" + name.capitalize() + "Message"
       
        if hasattr(self.activity, methodName):
            method = getattr(self.activity, methodName)
        else:        
            self.logger.critical("The method 'receive" + name.capitalize() + "Message' is not implemented in " + str(self.activity))
            return 

        if callable(method):
            method(message)
        else: 
            self.logger.critical("The so-called method named: '" + str(method) + "' is not callable")

    def stop(self):
        """ Stops all running services and itself """
        self.running = False

        for key in self.services:
            service = self.services[key]
            if service.socketName != config.get("Sockets", "keyinput"):
                self.logger.info("Terminating socket: " + service.socketName)
                service.socket.send_json({"head":"stop"})

    def startActivities(self):
        """Starting activity based on config"""
        startActivityName = config.get("Activities", "start")
        self.logger.info("Starting activity: " + startActivityName)
        self.switchActivity(startActivityName)

       
    def run(self):
        self.logger.info("Kernel is booting")

        self.startActivities()
     
        # Process messages from  sockets
        while self.running:
            try:
                poller_socks = dict(self.poller.poll(2))
                
            except KeyboardInterrupt:
                self.logger.info("Received Key interrupt. Exiting")
                break

            try:
                for key in self.services:
                    if self.services[key].socket in poller_socks:
                        self.receive(key, self.services[key].socket.recv_json())   
            except zmq.error.ContextTerminated:
                self.logger.info("ContextTerminated " + __file__ + " is shutting down")
                self.running = False
                break


    def send(self, service, message):
        """ 
        Sends a message to the specified service 
        """
        assert service in self.services, ("The Specified service: " + str(service) + " was not in services: " + str(self.services))
        self.services[service].socket.send_json(message)


    def switchActivity(self, activity, data=None):
        """ Switches activity to the specified activity. Data is sent to the activity """
        Activity = activity.capitalize()

        package = get_config(config, 'Activities', 'package', default='activities')
        moduleName = ''
        if len(package) > 0:
            moduleName += package + "." 
        moduleName += activity

        try: 
            self.logger.debug("Importing " + moduleName)
            module = importlib.import_module(moduleName) #,package=package)     
        except ImportError as e: 
            self.logger.critical("The module '%s' did not exist as an activity in package: %s. Exception: %s" % (activity, package, str(e)))
            return
     
        activityClass = getattr(module, Activity)
        self.activity = activityClass(self)
        self.activity.onCreate(data) 
        

    def emptyQueue(self, name):
        """ Empties the ZMQ queue """
        meta = self.services[name]
       
        while meta.socket.poll(2) != 0:
            meta.socket.recv_json()
