#app.py
import time
import logging, logging.config
import sys
from red.config      import config

logging.config.fileConfig('config/logging.conf')

from PySide           import QtGui
from red.kernel      import Kernel
import signal
import sys

class Red(object):

    def __init__(self, configFile='config/init.conf'):
        self.configFile = configFile

    def start(self):
        ### Initialize Logger
        
        logger = logging.getLogger("red")
        logger.info("Zebra 14 is booting")
        
        app = QtGui.QApplication(sys.argv)
        
        logger.info('Reading config; ' + self.configFile) 
        config.read(self.configFile)



        self.kernel = Kernel(app)
        signal.signal(signal.SIGINT, self.signal_handler)
        
        ##### This is QT load UI ######
        services = config.get('Services','Services').split(",")
        if "display" in services:
            logger.info("Zebra GUI is initiating")
            from red.mainwindow import MainWindow
            window = MainWindow.instance()
            window.show()
            logger.info('Zebra GUI initiated')
        
        ###############################
        self.kernel.start()
        
        ###### This fellow must be run in the end ######
        if "display" in services:
            sys.exit(app.exec_())

    def signal_handler(self, signal, frame):
        print('You pressed Ctrl+C!')
        self.kernel.stop()
    