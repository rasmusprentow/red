#display.py

import sys, time
from red.services.base import Service
from PySide.QtCore import QThread, Signal, Slot, QObject



class Display(Service, QThread, QObject):

    layoutSignal = Signal(object)
    functionSignal = Signal(str,str)

    _instance = None

    def __init__(self, name, context=None):
        super(Display, self).__init__(name=name, context=context)
        Display._instance = self
        
    def processMessage(self, message):
        if message["head"] == "set_layout":
            self.layoutSignal.emit(message["data"])
            return True
        elif message["head"] == "call_func":
            self.functionSignal.emit(message["data"]["func"],str(message["data"]["param"])) 
            return True
        else:
            return False

    @Slot(str)
    def onClicked(self, btn):
        print btn
        message = {"head":"button_clicked","data":btn}
        self.send(message)
        

