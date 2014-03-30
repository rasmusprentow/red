import sys

sys.path.append('.')

import unittest
import zmq

from threading import Thread

from activities.cashier.main import Main 
import logging, logging.config
from models.testdata import createTestData, clearTestData
from helpers.transactor import Transactor, InsufficientCoinException, SerialNotFoundException
from helpers.authenticator import Authenticator

logging.config.fileConfig('config/logging.conf')

from red.config import config
from red.kernel import Kernel



class MockSocket():

    def __init__(self):
        self.received = None

    def send_json(self,value,_2=None,_3=None):
        self.received = value

class MockSerivce():

    def __init__(self):
        
        self.socket = MockSocket()

    def getReceived(self):
        return self.socket.received


class MockKernel(Kernel):
    def __init__(self):
        super(MockKernel, self).__init__()
        pass


class BaseActivityTest(unittest.TestCase):

    def setup(self):
        """ Call super(TESTNAME, self).setup() """
        self.kernel = MockKernel()
        self.kernel.services = {}

    def getActivity(self, activity):
        """ Takes an activity as instance and instanciates it correctly """
        return activity(self.kernel)

    def setServices(self, services):
        "Call this during the test setUp to add required Services"
        for service in services:
            self.kernel.services[service] = MockSerivce()

    def assertReceived(self, service, arg):
        """ Asserts that the required service received the argument """
        received = self.kernel.services[service].getReceived()
        self.assertEqual(arg, received)

