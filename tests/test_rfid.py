#test_nfc.py

#test_basethread.py

import sys

sys.path.append('.')

from red.drivers.nfc import NfcReader, Command,InvalidSerialNumberLpcException
import unittest

import logging, logging.config
logging.config.fileConfig('config/logging.conf')


class FakeSerial:

    toBeRead = []

    def sendMessage(self,msg):
        self.toBeRead = msg
        self.toBeRead.reverse()

    def read(self,length=1):
        return chr(self.toBeRead.pop());

   

class Test_ServiceTestCase(unittest.TestCase):
 
    def setUp(self):
        self.reader = NfcReader(lambda x:x)
        pass
 
    def tearDown(self):
        """Call after every test case."""
        pass
 
    def test_createCommand(self):
        cmd =  Command(0x89,[0x18,0x0A])
        
        """
        asserts
        """
        self.assertEqual([0xAA,0x00,0x03,0x89,0x18,0x0A,0x98,0xBB], cmd.message)

    def test_fakeSerial(self):
        msg = [0xAA,0x00,0x0A,0x00,0x00,0xAA,0xBB,0xAA,0xBB,0xAA,0xBB,0xAA,0xBB,0x0A,0xBB]
        fs = FakeSerial();
        fs.sendMessage(msg)

        """
        asserts
        """
        self.assertEqual(chr(0xAA), fs.read())
        self.assertEqual(chr(0x00), fs.read())
        self.assertEqual(chr(0x0A), fs.read())
          
    def test_receiveMessage(self):
        msg_withExtra = [0xaa,0x0,0x6,0x0,0x0,0x27,0xb,0xde,0xe4,0x10,0xbb,(0xCC),0xBB]
        msg           = [0xaa,0x0,0x6,0x0,0x0,0x27,0xb,0xde,0xe4,0x10,0xbb]
        data          = [0x0,0x27,0xb,0xde,0xe4]
        snr        = [0x27,0xb,0xde,0xe4]
        fs = FakeSerial()
        fs.sendMessage(msg_withExtra)
        self.reader.start(fs)
        result = self.reader._receiveMessage() 

        """
        asserts
        """
        self.assertEqual(result.data, data)
        self.assertEqual(result.status, 0x00)
        self.assertEqual(result.getSerial(), snr)
        self.assertTrue(result.isValidBcc())

    def test_receiveMessageFail(self):
        msg_withExtra = [(0xAA),(0x00),(0x0A),(0x00),(0x00),(0xAA),(0xBB),(0xAA),(0xBB),(0xAA),(0xBB),(0xAA),(0xBB),(0x0A),(0xBB),(0xCC),0xBB]
        msg           = [(0xAA),(0x00),(0x0A),(0x00),(0x00),(0xAA),(0xBB),(0xAA),(0xBB),(0xAA),(0xBB),(0xAA),(0xBB),(0x0A),0xBB]
        data          = [(0x00),(0xAA),(0xBB),(0xAA),(0xBB),(0xAA),(0xBB),(0xAA),(0xBB)]
        snr        = [(0xAA),(0xBB),(0xAA),(0xBB),(0xAA),(0xBB),(0xAA),0xBB]
        fs = FakeSerial()
        fs.sendMessage(msg_withExtra)
        self.reader.start(fs)
        result = self.reader._receiveMessage() 

        """
        asserts
        """
        self.assertEqual(result.data, data)
        self.assertEqual(result.status, 0x00)
        try:
            self.assertFalse(result.getSerial())
        except InvalidSerialNumberLpcException:
            assert True
        assert result.isValidBcc() == True

    def test_receiveMessageInvalid(self):
        msg = [(0xAA),(0x00),(0x0A),(0x00),(0x00),(0xAA),(0xBB),(0xAA),(0xBB),(0xAA),(0xBB),(0xAA),(0xBB),(0x08),(0xBB)]
      
        fs = FakeSerial()
        fs.sendMessage(msg)
        self.reader.start(fs)
        result = self.reader._receiveMessage() 

        """
        asserts
        """
        self.assertFalse(result.isValidBcc())
        try:
            self.assertFalse(result.getSerial())
        except:
            assert True


    #def test_extractSerial(self):
    #    msg = [0xAA,0x00,0x0A,0x00,0x00,0xAA,0xBB,0xAA,0xBB,0xAA,0xBB,0xAA,0xBB,0x0A,0xBB]
    #    snr = [0xAA,0xBB,0xAA,0xBB,0xAA,0xBB,0xAA,0xBB]
    #    result = 
    #    assert result == snr


 
if __name__ == "__main__":
    unittest.main() # run all tests




