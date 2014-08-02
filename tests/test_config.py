#test_kernel.py
import unittest
from red.config import config, initConfig



class Test_Config(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Call on construction"""
        pass

    def setUp(self):
        """Call before every test case."""
        pass

    def tearDown(self):
        """Call after every test case."""
        pass

    def testConfigRecursion(self):
        initConfig("red/tests/config/recursion_meta.conf")
        self.assertEqual(config.get('Test','rec'),'2')

    def testConfigNoRecursion(self):
        initConfig("red/tests/config/recursion_meta.conf",None,0)
        self.assertEqual(config.get('Test','rec'),'1')

    @unittest.skip("Only implemented for 'config' and 'logging.config', not the general case yet")
    def testConfigAlternativeVariable(self):
        initConfig("red/tests/config/alternative_var_meta.conf")
        self.assertEqual(red.tests.config.alternative.get('Test','option'),'value')

    def testMissingMandatoryFile(self):
        self.assertRaises(Exception,initConfig,("red/tests/config/missing_mandatory_file_meta.conf"))

    def testMissingMandatoryOption(self):
        '''testMissingMandatoryOption'''
        self.assertRaises(Exception,initConfig,("red/tests/config/missing_mandatory_option_meta.conf"))

    def testMissingOptionalFile(self):
        #Just check that it can be called without raising an error
        initConfig("red/tests/config/missing_optional_file_meta.conf")

if __name__ == "__main__":
    unittest.main() # run all tests
