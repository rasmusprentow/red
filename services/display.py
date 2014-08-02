#display.py

import sys, time
from red.services.base import Service
from PySide.QtCore import QThread, Signal, Slot, QObject



class Display(Service, QThread, QObject):

    layoutSignal = Signal(object)
    functionSignal = Signal(str,str)
    fourIntsSignal = Signal(str,int,int)
    _instance = None

    def __init__(self, name, context=None):
        super(Display, self).__init__(name=name, context=context)
        Display._instance = self
        
    def processMessage(self, message):
        if message["head"] == "set_layout":
            self.layoutSignal.emit(message["data"])
            return True
        elif message["head"] == "call_func": 
            param = message["data"]["param"] 
            if (not isinstance(param, tuple)) and (not isinstance(param, list)) :
                self.functionSignal.emit(message["data"]["func"],str(message["data"]["param"]))        
            else:
                self.fourIntsSignal.emit(message["data"]["func"],message["data"]["param"][0],message["data"]["param"][1])      
            return True     
        else:
            return False

    @Slot(str)
    def onClicked(self, btn):
      
        message = {"head":"button_clicked","data":btn}
        self.send(message)
        
        

