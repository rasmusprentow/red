#lpc.py

from red.services.base import Service
import zmq
from red.api.rfid import RfidReader
from red.config import config
from threading import Thread
"""
API:

    Receives:
        get_pocket
        
    
    Transmits:
        pocket
            data = <serial>

"""


class Lpc(Service, Thread):

    def __init__(self, name, context=None):
        super(Lpc, self).__init__(name=name, context=context)
        port = config.get('LPC', 'port')
        self.rfidReader = RfidReader(port=port)
        self.rfidReader.start()

    def processMessage(self, message):
        if(message['head'] == "get_pocket"):
            serial = self.getPocket()
            data = "".join("{:02x}".format((c)) for c in serial)
            message = {'head' : 'pocket', 'data' : data}
            self.send(message)
            return True

        elif(message['head'] == "activate_buzzer"):
            self.rfidReader.activateBuzzer()
            return True
        elif(message['head'] == "flush_serial"):
            self.rfidReader.clear()
            return True
        else:
            return False
            

    def getPocket(self):
        message = self.rfidReader.getPocketData()
        return message.getSerial()