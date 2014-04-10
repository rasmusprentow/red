#app.py
import time
import logging, logging.config
import sys
from red.config      import config, initConfig
#logging.config.fileConfig('config/logging.conf')
from PySide           import QtGui
from red.kernel      import Kernel
import signal
import sys

class Red(object):

    def __init__(self, configFile='meta.conf'):
        self.configFile = configFile
        pass

    def start(self):
        global config
        ### Initialize Logger
        initConfig(self.configFile,logging.getLogger("config"))
        
        logger = logging.getLogger("red")
        logger.info("Zebra 14 is booting")
        
        app = QtGui.QApplication(sys.argv)

        
        #logger.info('Reading config; ' + self.configFile) 
        #config.read(self.configFile)



        self.kernel = Kernel()
        self.window = None
        ##### This is QT load UI ######
        services = config.get('Services','Services').split(",")
        if "display" in services:
            logger.info("Zebra GUI is initiating")
            from red.mainwindow import MainWindow
            self.window = MainWindow.instance()
            self.window.show()
            logger.info('Zebra GUI initiated')
        
        ###############################
        self.kernel.start()
        signal.signal(signal.SIGINT, self.signal_handler)
        
        ###### This fellow must be run in the end ######
        if "display" in services:
            sys.exit(app.exec_())

    def signal_handler(self, signal, frame):
        self.kernel.stop()
        if self.window != None:
            self.window.close()
    