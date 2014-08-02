#lpc.py

from red.services.base import Service
import zmq
import red.drivers.nfc as nfc
import traceback

from red.config import config, get_config
from threading import Thread

class Lpc(Service, Thread):

    def __init__(self, name, context=None):
        super(Lpc, self).__init__(name=name, context=context)
        port = config.get('LPC', 'port')

        if get_config(config,'LPC', 'use_mock_reader', default='false') == 'true': 
            self.nfcReader = nfc.MockNfcReader(port=port,nfcListener=self.onNfcMessage)
        else:
            self.nfcReader = nfc.NfcReader(port=port,nfcListener=self.onNfcMessage)
        self.nfcReader.start()

    def processMessage(self, message):
        self.logger.info("Received: " + str(message))
        if(message['head'] == "get_tag"):
            self.nfcReader.getTagData()
            return True
        elif(message['head'] == "activate_buzzer"):
            self.nfcReader.activateBuzzer()
            return True
        elif(message['head'] == "flush_serial"):
            self.nfcReader.clear()
            return True
        elif message['head'] == "stop_operations":
            self.nfcReader.stopAllCurrentOperations()
            return True
        else:
            return False
            
    def onNfcMessage(self,tagData):
        if tagData.moreThanOneCard():
            self.nfcReader.getTagData()
            return
        try: 
            serial = tagData.getSerialAsHex()
        except Exception as e:
            self.logger.fatal("Found exception: " + str(traceback.format_exc()))
            self.nfcReader.getTagData()
            return 
        message = {'head' : 'tag', 'data' : serial}
        self.send(message)
        self.nfcReader.clear()
       