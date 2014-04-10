#test_kernel.py
import unittest
from red.kernel import Kernel
from red.config import config, initConfig
from red.activity import Activity
import math, os

class MockActivity(Activity):

    def receiveTestMessage(self, message):
        self.received = True
 
class Test_kernel(Activity):
    """ 
    This might appear odd, but ass activities must be named
    the same as the module in which they reside, and i needed a
    mock activity which can be loaded, so this class was born 
    """
    received = False
    def receiveTestMessage(self, message):
        print "Got message"
        Test_kernel.received = True


class Test_KernelTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        initConfig("test_meta.conf")

    def setUp(self):
        """Call before every test case."""
       
        
        try:
            config.add_section('Shop')
        except:
            pass

        try: 
            config.add_section('Services')
            config.add_section('Activities')
        except:
            pass

        config.set('Shop', 'voucher_percentage', '33')
        config.set('Shop', 'fee_percentage', '1')
        config.set('Shop', 'name', 'enviclean')
        

        config.set('Services', 'services', '')
        config.set('Activities', 'start', 'test_kernel')
        config.set('Activities', 'package', 'red.tests')

        self.kernel = Kernel()
 
    def tearDown(self):
        """Call after every test case."""
        pass
 
    def testReceive(self):
        """ Tests the receive method """

        """ Should not give an exception, but should log some stuff """
        self.kernel.receive("self.stop()", {"head" : "echo"})

        """ This tests that the message gets delivered to the activity"""
        self.kernel.activity = MockActivity(self.kernel)
        self.kernel.receive("test", {"head" : "echo"})
        self.assertTrue(self.kernel.activity.received)

    def testSwitchActivity(self):
        """ Tests switch activity """

        """ This tests that it does not throw renegade exceptions"""
        self.kernel.switchActivity("something_nonexistant")

        """ This tests that it does not throw renegade exceptions"""
        self.kernel.switchActivity("test_kernel")
        self.kernel.receive("test", {"head" : "echo"})
        self.assertTrue(Test_kernel.received)

    def testSend(self):
        try: 

            self.kernel.send("test", {"head" : "hello"})
            self.assertTrue(False)
        except Exception:
            self.assertTrue(True)

if __name__ == "__main__":
    unittest.main() # run all tests
