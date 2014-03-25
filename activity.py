#activity.py
"""
The activity module it the mother of all other activities
"""

from sqlalchemy.orm import sessionmaker
from models.model import engine

import logging, time


class Activity(object):
    """
    Inherit from this class to create an activity.
    Activities are what some people call controllers.
    If you expect to receive something from a service, say NFC service, you must implement
    a proper receive method. In this case. receiveNfcMessage(self, message)
    """

    def __init__(self, kernel):
        super(Activity, self).__init__()
        self.kernel = kernel
        self.logger = logging.getLogger('activity')
        self._session = None
    

    def onCreate(self, data=None):
        """
        This method is called when the object is created.
        You should override this method in your own activity.
        The data parameter contains whatever got passed from switchActivity
        """
        pass

    def setLayout(self, layout,sleep=0):
        """
        Change the layout of the screen
        Layout is string that tells which layout file to load.
        If, for instance, you pass "<folder>/<layout>" the file layouts/<folder>/<layout>.qml get loaded. 
        """
        self.kernel.send("display", {"head":"set_layout", "data":layout})
        if sleep > 0:
            time.sleep(sleep)

    def send(self, service, message):
        """ 
        Send message to any service. 
        Message must be a dictionary.
        """
        self.kernel.send(service, message)

    
    def switchActivity(self, activity, data=None):
        """ 
        Switch to the specified activity
        The data param gets sent to the new activity's onCreate method.
        """
        self.kernel.switchActivity(activity, data)


    def emptyQueue(self, name):
        """
        Clears the queue for any inbound message from the specified service. 
        Use this method with care as you risk important messages are deleted. 
        """
        self.kernel.emptyQueue(name)


    @property
    def session(self):
        """ 
        Session property used for sqlalchemy
        """
        if not hasattr(self, "_session") or self._session == None:
            self._session = sessionmaker(bind=engine)()
        return self._session

    def callLayoutFunc(self, func, param):
        """
        Deprecated. Use invokeLayoutFunction
        """
        self.logger.warning("callLayoutFunc is deprecated, use invokeLayoutFunction. Please remove the old when fixed")

    def invokeLayoutFunction(self, function, param):
        """
        Use this method to update anything on the layout. 
        Function is the name of the function to be called in the layout. 
        Param is paremeter for that function. 
        """
        self.send("display", {"head":"call_func", "data":{"func":function, "param":param}})