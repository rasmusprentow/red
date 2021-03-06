import serial, time

import logging, threading
from red.config import config, get_config
logger = logging.getLogger(__file__)


""" Start of Text """
STX = 0xAA

""" End of Text """
ETX = 0xBB
class LpcException(Exception):
    """docstring for LpcException"""
   
    def __init__(self, msg):
        super(LpcException, self).__init__(msg)
       
###################################################################################
class InvalidSerialNumberLpcException(LpcException):
    """docstring for LpcException"""
   
    def __init__(self, msg):
        super(LpcException, self).__init__(msg)

###################################################################################
class StatusErrorLpcException(LpcException):
    """docstring for LpcException"""
   
    def __init__(self, msg):
        super(LpcException, self).__init__(msg)

###################################################################################
class BCCLpcException(LpcException):
    """docstring for LpcException"""
   
    def __init__(self, msg):
        super(LpcException, self).__init__(msg)
       
###################################################################################
class Command:
    """
    Represents a command message from the "cmd" and a "data_array"
    A cmd message is: <STX:StationId:msgLenght:cmd:data[0..n]:BCC:ETX>
    """
    def __init__(self,cmd, data=[],stationId=0):
        self.cmd = cmd
        self.data = data
        self.stationId = stationId
    

    @property
    def bcc(self):
        _bcc = self.stationId ^ self.length ^ self.cmd 
        for value in self.data:
            _bcc = _bcc ^ value
        return _bcc
    
    @property
    def message(self):
        _message = [STX, self.stationId,self.length, self.cmd]  
        for value in self.data:
            _message.append(value)
        _message.append(self.bcc)
        _message.append(ETX)   
        return _message   

    @property
    def length(self):
        _length = len(self.data) + 1
        return _length
    
###################################################################################
class RespondMessage(object):
    """ Represents the response from the LpcReader """
    def __init__(self):
        self.stationId = 0
        self.status = 0x00
        self.bbc = 0x00
        self.data = []
        self.length = 0
       
    def getSerial(self):
        if self.status != 0x00:
            raise StatusErrorLpcException("Status Error: %s" % self.status)
        elif self.length != 6:  
            """ A serial is 4 bytes plus status and a sub-status """
            raise InvalidSerialNumberLpcException("The serial number was of insufficient length")
        elif not self.isValidBcc():
            raise BCCLpcException("The BCC was incorrect")
        else:
            data = self.data
            data.remove(0)
            return data
    def moreThanOneCard(self):
        """ The fist byte is a sub-status which must be 0x00 to indicate that only one card was present"""
        return self.data[0] != 0x00

    def getSerialAsHex(self):
        data = "".join("{:02x}".format((c)) for c in self.getSerial())
        return data

    def isValidBcc(self):
        valid = self.stationId ^ self.length ^ self.status 
        for value in self.data:
            valid = valid ^ value
        return valid == self.bcc

    def getRaw(self, sep=""):
        data = hex(self.stationId) + sep + hex(self.status) + sep + hex(self.length)
        data += sep + "".join(hex(c) + sep for c in self.data)
        data += sep + hex(self.bbc) 
        return data


####################################################################################

class MockMessage(object):
    def __init__(self, data):
        self.data = data

    def getSerialAsHex(self):
        return self.data

    def moreThanOneCard(self):
        return False

####################################################################################
class NfcWoker(threading.Thread):

    running = False

    def setReader(self, reader):
        self.reader = reader



    def run(self):
         self.running = True
         while self.running:
            cmd = Command(0x25,[0x26,0x00])  
            self.reader.write(cmd)
            msg = self.reader._receiveMessage()
            #print( msg.getRaw(' '))
            if msg.length == 6:          
                self.running = False
                self.reader.listener(msg)
                return
            time.sleep(0.2)
            

class MockNfcWoker(NfcWoker):

    running = False

    def setNfcListener(self, listener):
        self.listener = listener

    def run(self):
        self.running = True
        self.reader.listener(MockMessage(raw_input()))
        self.running = False
            

###################################################################################
class NfcReader(object):
    """
    Class that wraps the RFID reader. 
    The class will initiate connection once constructed.
    """

    def __init__(self,nfcListener, port="/dev/ttyUSB0", baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.stationId = 00;
        if not callable(nfcListener):
            raise Exception("The nfcListener is not callable")
        
        self.listener = nfcListener
        self.reloadWorker()

    def start(self,ser=None):
        if "/dev/ttyO" in self.port:
            import Adafruit_BBIO.UART as UART
          
            UART.setup('UART' + str(self.port[-1]))
        self.serial = ser or serial.Serial(self.port, self.baudrate)

    def reloadWorker(self):
        self.worker = NfcWoker()
        self.worker.setReader(self)
       


    def getTagData(self):
        """ 
        Puts the reader in read mode and 
        Notifies the listener when a tag is available
        The method is non blocking
        """
        if self.worker.running == True:
            return
        self.reloadWorker()
        self.worker.start()
       
    def _receiveMessage(self):
        """ Internal methodd that receives """
        index = 0
        msg = RespondMessage()
        msg.length = 0
        

        while True:
            byte = (self.serial.read())
            byte = ord(byte)

           
           
            
            if index == 0:
                if byte != 0xaa:
                    print("The first byte was not 0xAA but: " + hex(byte))
                    continue;
            elif index == 1:
                if byte != self.stationId:
                    logger.error("The station is was not zero it was: " + hex(byte))
            elif index == 2:
                msg.length = byte
            elif index == 3:
                msg.status = byte
            elif index > 3 and index <= msg.length + 2:
                msg.data.append(byte)
            elif index > msg.length + 2 and index < msg.length + 4:
                msg.bcc = byte
            elif index == msg.length + 4:
                if byte != 0xBB:
                    raise LpcException("The end of message was not 0xBB, but: " + hex(byte))
                else:
                    return msg
            else:
                raise Exception("Weird error, something really bads happended")
            index += 1;

    def activateBuzzer(self): 
        cmd = Command(0x89,[0x10,0x01])
        self.write(cmd)
        try:
            while self.serial.outWaiting() != 0:
                """ Ensure that the buzz gets transmitted """
                time.sleep(0.01)
        except AttributeError as e:
            logger.error("AttributeError, attribute not found: " + str(e))
            time.sleep(0.4)
        

    def clear(self):
        while self.serial.inWaiting() > 0:
            self.serial.read()
        self.serial.flush()
 
    def stopAllCurrentOperations(self):
        self.worker.running = False
        try: 
            self.worker.join()
        except RuntimeError:
            pass
        self.clear()


    def write(self, cmd):
        msg = ""
        for byte in cmd.message:
            msg += chr(byte)
        self.serial.write(msg)


########################################################################
class MockNfcReader(NfcReader):


    def start(self,ser=None):
        pass
 
    def clear(self):
        pass

    def reloadWorker(self):
        self.worker = MockNfcWoker()
        self.worker.setReader(self)

    def write(self, cmd):
        pass

    def activateBuzzer(self): 
        pass
