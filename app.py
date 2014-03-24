#app.py
import time
import logging, logging.config
import sys
from red.config      import config
from PySide           import QtGui
from red.kernel      import Kernel


class Red(object):

    def __init__(configFile='config/init.conf'):
        self.configFile = configFile

    def start(self):
        ### Initialize Logger
        logging.config.fileConfig('config/logging.conf')
        logger = logging.getLogger(__file__)
        logger.info("Zebra 14 is booting")
        
        app = QtGui.QApplication(sys.argv)
        
        logger.info('Reading config; ' + conffile) 
        config.read(self.configFile)



        kernel = Kernel()
        
        ##### This is QT load UI ######
        services = config.get('Services','Services').split(",")
        if "display" in services:
            logger.info("Zebra GUI is initiating")
            from red.mainwindow import MainWindow
            window = MainWindow.instance()
            window.show()
            logger.info('Zebra GUI initiated')
        
        ###############################
        
        
        kernel.start()
        
        
        
        ###### This fellow must be run in the end ######
        if "display" in services:
            sys.exit(app.exec_())
        