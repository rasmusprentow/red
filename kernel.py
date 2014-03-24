
import logging, logging.config
import zmq
import time, sys
import threading
import types
import re

from red.utils.serviceFactory import ServiceFactory
from red.config import config

logger = logging.getLogger("kernel")

from models.model import engine
from sqlalchemy.orm import sessionmaker



class Kernel (threading.Thread):

    def __init__(self):
        super(Kernel, self).__init__()
        ### Initialize Logger
        self.logger = logger

        self.context = zmq.Context()
        self.poller = zmq.Poller()
        self.running = True
        self.services = ServiceFactory(self).createActiveServicesFromConfig()
        self._session = None

    def getSession(self):
        if self._session == None:
            self._session = sessionmaker(bind=engine)()
        return self._session

    @property
    def session(self):
        return self.getSession()

    def __getattr__(self, name):
        """ This little piece of magic delegates methods that
        start with 'receive' to the activity """
        if name.startswith('receive'):
            if self.activity != None:
                assert re.match('^[\w-]+$', name) is not None
                return eval("self.activity." + name)
       
    def receive(self,name, message): 
        if message["head"] == "echo":
            self.logger.info("Received echo from " + name)               
        assert re.match('^[\w-]+$', name) is not None
        try: 
            method = eval("self.activity.receive" + name.capitalize() + "Message")        
            method(message)
        except AttributeError:
            self.logger.fatal("The method 'receive" + name.capitalize() + "Message' is not implemented in " + str(self.activity))

    def stop(self):
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
                self.logger.info ("ContextTerminated " + __file__ + " is shutting down");
                self.running = False
                break


    def send(self, service, message):
        assert service in self.services, ("The Specified service: " + str(service) + " was not in services: " + str(self.services))
        self.services[service].socket.send_json(message)


    def switchActivity(self, activity, data = None):
        Activity = activity.capitalize()

        try:
            package = config.get('Activities','package')
            importPackage = "from activities." + package + "." + activity + " import " + Activity
        except: 
            importPackage = "from activities." + activity + " import " + Activity

        logger.info("Importing config defined package: " + importPackage)
        exec importPackage

        self.activity = eval(Activity)(self)
        self.activity.onCreate(data)

    def emptyQueue(self,name):
      
        meta = self.services[name]
       
        while meta.socket.poll(2) != 0:
            meta.socket.recv_json()