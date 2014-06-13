



from red.services.base import Service
from red.drivers import keypad
import zmq, time

import logging
from threading import Thread
logger = logging.getLogger(__file__)

class Keypad(Service,Thread):
    # Overrides run, so doesn't wait for messages
    def run(self):


        try:
            while True:
                key = keypad.getKey()
                if key != None:
                    self.socket.send_json({"head":"key_pressed","data":key})
                time.sleep(0.2) 
                    
        except zmq.error.ContextTerminated:
            return
 