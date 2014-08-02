

from red.drivers.uart import Uart
import unittest
import logging
import json
logging.config.fileConfig('config/logging.conf') 

class Test_UARTTestCase(unittest.TestCase):
 
    def setUp(self):
        """Call before every test case."""
        pass
 
    def tearDown(self):
        """Call after every test case."""
        pass
 
    def testReceiveJsonPass(self):

        string1 = "{}"
        string2 = "{\"asdsdf\":\"ddd\"}"
        string3 = '{"sdfsdf":"dadasdad"}'
        string4 = '{"test" : [ "ddd", "dsd"]}'
        string5 = '{"test" : [ "ddd", "dsd", {"sdsds" : "dsdsd"}]}'

        uart = Uart()
        uart.serial = MockSerial(string1)
        self.assertEqual(json.loads(string1), uart.receiveJson())
        uart.serial = MockSerial(string2)
        self.assertEqual(json.loads(string2), uart.receiveJson())
        uart.serial = MockSerial(string3)
        self.assertEqual(json.loads(string3), uart.receiveJson())
        uart.serial = MockSerial(string4)
        self.assertEqual(json.loads(string4), uart.receiveJson())
        uart.serial = MockSerial(string5)
        self.assertEqual(json.loads(string5), uart.receiveJson())


class MockSerial(object):
    def __init__(self, message):
        self.message = message
    
    def read(self):
        head = self.message[0]
        self.message = self.message[1:]
        return head
 
if __name__ == "__main__":
    unittest.main() # run all tests
