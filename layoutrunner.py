""" 
The layoutrunner can be used to run a layout and see it without running the kernel 
"""




from red.mainwindow import MainWindow

from red.services.display import Display
from PySide           import QtGui
import zmq , threading, sys
from red.config import config


app = QtGui.QApplication(sys.argv)
socketName = "inproc://display"


class InThreasd(threading.Thread):

    def __init__(self):
        super(InThreasd,self).__init__()
        context = zmq.Context()
        real_context = zmq.Context.instance();
        self.socket = real_context.socket(zmq.PAIR)
        self.socket.bind(socketName)
        self.last = ""

    def run (self):
        print "Type name of layout (Enter refreshes)"
        while True:
            try:
                inp = raw_input()
            
            except:     
                break
            if inp == "":
                inp = self.last
            self.socket.send_json({"head":"set_layout","data":inp})
            self.last = inp
           



listener = InThreasd()


display = Display(name=socketName)


window = MainWindow.instance()
window.show()

display.start()
listener.start()



sys.exit(app.exec_())
        


