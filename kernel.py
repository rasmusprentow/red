""" The kernel package contains the Kernel 
 Pylint: pylint2  kernel.py --disable=trailing-whitespace --disable=line-too-long --disable=no-member --disable=invalid-name
"""
import logging, logging.config
import zmq
import threading
import traceback

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
        self.activity = None
        self.running = True
        self._session = None
      

    def receive(self, name, message):
        """ 
        Reveive method for any messages reeived from any service 
        The activity will get the message in its 'receive<service>Message' method

        """
        if message["head"] == "system_message":
            if "data" not in message:
                self.logger.critical("Erroneous system_message. Msg: " + str(message))
            if message["data"] == "stop":
                self.stop() 
            if message["data"] == "echo":
                self.logger.info("Received echo from " + name)  
            return         
        
        methodName = "receive" + name.capitalize() + "Message"
       
        if hasattr(self.activity, methodName):
            method = getattr(self.activity, methodName)
        else:        
            self.logger.warning("The method 'receive" + name.capitalize() + "Message' is not implemented in " + str(self.activity))
            return 

        if callable(method):
            try: 
                method(message)
            except Exception: 
                ## We restart everything 
                self.logger.critical("An unknown exception occured. Exception: " + traceback.format_exc())
                self.restartAllServices()
                self.startActivities()

        else: 
            self.logger.critical("The so-called method named: '" + str(method) + "' is not callable")

    def restartAllServices(self):
        """ Restarts all services """
        for key in self.services:
            service = self.services[key]
            if not service.isMasterService: 
                # We do not inform our master of a restart
                self.emptyQueue(service.serviceName)
                service.socket.send_json({"head" : "system_message", "data" : "restart"})

    def stop(self):
        """ Stops all running services and itself """
        self.running = False

        for key in self.services:
            service = self.services[key]
            if not config.has_option("Sockets", "keyinput") or service.socketName != config.get("Sockets", "keyinput"):
                self.logger.info("Terminating socket: " + service.socketName)
                service.socket.send_json({"head" : "system_message" , "data" : "stop"})

    def startActivities(self):
        """Starting activity based on config"""
        startActivityName = config.get("Activities", "start")
        self.logger.info("Starting activity: " + startActivityName)
        self.switchActivity(startActivityName, clearLpc=False)

       
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

        self.logger.info("Stopping kernel.")


    def send(self, service, message):
        """ 
        Sends a message to the specified service 
        """
        assert service in self.services, ("The Specified service: " + str(service) + " was not in services: " + str(self.services))
        self.services[service].socket.send_json(message)


    @property
    def session(self):
        """ 
        Session property used for sqlalchemy
        """
        if not hasattr(self, "_session") or self._session == None:
            from models.model import engine
            from sqlalchemy.orm import sessionmaker
            self._session = sessionmaker(bind=engine)()
        return self._session

    

    def switchActivity(self, activity, data=None, clearLpc=True):
        """ Switches activity to the specified activity. Data is sent to the activity """
        Activity = activity.capitalize()
        self.logger.debug("Switching activity to " + activity)
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
        if clearLpc:
            self.clearLpc() # ensure activities start in clean state
        

        self.activity = activityClass(self)
        self.activity.onCreate(data) 
        

    def emptyQueue(self, name):
        """ Empties the ZMQ queue """
        meta = self.services[name]
       
        while meta.socket.poll(2) != 0:
            meta.socket.recv_json()

    def clearLpc(self):
        """ Resets the lpc service if it exists """
        if "lpc" in self.services:
            if self.activity != None:
                self.activity.send("lpc",{"head":"stop_operations"})
            self.emptyQueue("lpc")