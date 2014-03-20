#lpc.py

from red.services.base import Service
import zmq
import red.drivers.nfc as nfc
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
        if 'lpc' in config.get('Services', 'mock'):
            self.nfcReader = nfc.MockNfcReader(port=port)
        else:
            self.nfcReader = nfc.NfcReader(port=port)
        self.nfcReader.start()

    def processMessage(self, message):
        if(message['head'] == "get_pocket"):
            serial = self.getPocket()
            
            message = {'head' : 'pocket', 'data' : serial}
            self.send(message)
            return True

        elif(message['head'] == "activate_buzzer"):
            self.nfcReader.activateBuzzer()
            return True
        elif(message['head'] == "flush_serial"):
            self.nfcReader.clear()
            return True
        else:
            return False
            

    def getPocket(self):
        message = self.nfcReader.getPocketData()
        return message.getSerialAsHex()