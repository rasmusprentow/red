#network.py

from red.services.base import Service
import zmq, logging
from threading import Thread

logger = logging.getLogger(__file__)

class Network (Service, Thread):

    
    

    def processMessage(self,message):
        assert message is dict
        self.sock.send_json({'msg':'Echoing: ' + message['msg']}) 
        return True
