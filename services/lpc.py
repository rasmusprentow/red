#lpc.py

from red.services.base import Service
import zmq
import red.drivers.nfc as nfc
from red.config import config, get_config
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

        if get_config(config,'LPC', 'use_mock_reader', default='false') == 'true': 
            self.nfcReader = nfc.MockNfcReader(port=port)
        else:
            self.nfcReader = nfc.NfcReader(port=port)
        self.nfcReader.start()

    def processMessage(self, message):
        if(message['head'] == "get_tag"):
            self.getTag()
            return True
        elif(message['head'] == "activate_buzzer"):
            self.nfcReader.activateBuzzer()
            return True
        elif(message['head'] == "flush_serial"):
            self.nfcReader.clear()
            return True
        else:
            return False
            

    def getTag(self):
        self.nfcReader.clear()
        
        tagData = self.nfcReader.getTagData()
        while tagData.moreThanOneCard():
            tagData = self.nfcReader.getTagData()

        serial = tagData.getSerialAsHex()
        message = {'head' : 'tag', 'data' : serial}
        self.send(message)