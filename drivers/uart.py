
#uart.py

import Adafruit_BBIO.UART as UART
import serial
import os.path
import json
from red.config import get_config, config
import logging 
logger = logging.getLogger("kernel.uart")
from excep.excep import TimedOutException
from threading import Timer
# UARTS on the BBB
# UART    RX  TX  CTS RTS Device
# UART1   P9_26   P9_24   P9_20   P9_19   /dev/ttyO1
# UART2   P9_22   P9_21                   /dev/ttyO2
# UART3   P9_42   P8_36   P8_34           /dev/ttyO3
# UART4   P9_11   P9_13   P8_35   P8_33   /dev/ttyO4
# UART5   P8_38   P8_37   P8_31   P8_32   /dev/ttyO5



class Uart(object):


    def __init__(self):
        pass

    def start(self,uartnum, ser=None, baudrate=9600, mockUart=False, sysprefix="/dev/ttyO"):
        if not mockUart:
            UART.setup('UART' + uartnum)
        print("Baudrate is: " + baudrate)
        self.serial = ser or serial.Serial(sysprefix+uartnum, baudrate, timeout=5)
        return self

    def startFromConfig(self, config):
        uartnum = config.get('Intercom', 'uartnum')
        mockUart =  get_config(config, 'Intercom', 'use_mock_uart', default='false') == 'true'
        sysprefix = get_config(config, 'Intercom', 'sys_prefix', default='/dev/ttyO')
        baudrate = get_config(config, 'Intercom', 'baudrate', default=9600)
       
        self.start(uartnum=uartnum, mockUart=mockUart, sysprefix=sysprefix, baudrate=baudrate )
      

    def sendJson(self, message):
        logger.info ("sending " + str(message))
        self.serial.write(json.dumps(message))

    def setTimedout(self, value):
        self.timedout = value


    def receiveJson(self):
        self.timedout = False 
        timer = Timer(10, lambda x: self.setTimedout(x) , [True]) 
        timer.daemon = True
        timer.start()
        string = ""
        while True:
            string += self.serial.read()
            if self.timedout:
                raise TimedOutException("Uart timed out")
            if string != "":
                timer.cancel()
                timer = Timer(10, lambda x: self.setTimedout(x) , [True]) 
                timer.daemon = True
                timer.start()
            logger.info("Receiving " + string)
            try:
                data = json.loads(string)

                return data
            except ValueError as e: 
                pass
    
