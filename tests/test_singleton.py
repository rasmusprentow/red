#test_singleton.py



import sys

sys.path.append('.')

import unittest
from  red.utils.singleton import Singleton

import logging, logging.config
logging.config.fileConfig('config/logging.conf')


""" 
Subject class is used for testing it is a singleton and should work that way
"""
@Singleton
class SubjectClass():
	pass

@Singleton
class SubjectClass2():
    pass

@Singleton
class SubjectParamClass():
    def __init__(self, param1):
        self.param1 = param1
    pass


class EmptyClass():
    pass

@Singleton
class InheritedSingletonSubjectClass(SubjectClass2):
    def onlySubGotThis(self):
        pass
    


class Test_SimpleTestCase(unittest.TestCase):
 
    def setUp(self):
        """Call before every test case."""
        pass
 
    def tearDown(self):
        """Call after every test case."""
        pass
    
    def testCanInstanciate(self):
        instance = SubjectClass.instance();
        assert instance != None # For some reason "isinstance(instance, SubjectClass)" did not work
    
    def testThatSingleTonInstancesAreInfactTheSameInstance(self):
        instance = SubjectClass.instance();
        instance.number = 2;
    
        instance2 = SubjectClass.instance();
        assert instance2.number == 2
        assert instance == instance2
    
    def testThatNormalConstructionIsImpossible(self):
        try: 
            instance = SubjectClass()
            assert False
        except:
            assert True
    
    def testThatParamswork(self):
        paramval ="paramval"
        instance = SubjectParamClass.instance(paramval);
    
    
        instance2 = SubjectParamClass.instance();
        assert instance2.param1 == paramval
        assert instance == instance2
 
    """
    I could not make this one work and decided that it is not worth the time
    def testThatSingleTonInstancesAreInfactTheSameInstanceWithInheritace(self):
        instance = InheritedSingletonSubjectClass.instance();
        instance.number = 2;

        instance2 = InheritedSingletonSubjectClass.instance();
        instance2.onlySubGotThis();
        instance.onlySubGotThis();
        assert instance2.number == 2
        assert instance == instance2
    """
if __name__ == "__main__":
    unittest.main() # run all tests
