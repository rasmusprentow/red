#activity.py
"""
The activity module it the mother of all other activities
"""



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
        self.logger = logging.getLogger('activity.' + str(self.__class__.__name__))
        self._session = None
        self.defaultSleepTime = 5
    

    def onCreate(self, data=None):
        """
        This method is called when the object is created.
        You should override this method in your own activity.
        The data parameter contains whatever got passed from switchActivity
        """
        pass

    def setLayout(self, layout, sleep=0):
        """
        Change the layout of the screen
        Layout is string that tells which layout file to load.
        If, for instance, you pass "<folder>/<layout>" the file layouts/<folder>/<layout>.qml get loaded. 
        """
        self.kernel.send("display", {"head":"set_layout", "data":layout})
        if sleep > 0:
            time.sleep(sleep)

    def send(self, service, message=None, head=None, data=None):
        """ 
        Send message to any service. 
        Message must be a dictionary.
        If the head parameter is set message can be ignored.
        """
        if head != None:
            self.kernel.send(service, {"head" : head, "data" : data})
        else:
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
        return self.kernel.session

    def invokeLayoutFunction(self, function, param):
        """
        Use this method to update anything on the layout. 
        Function is the name of the function to be called in the layout. 
        Param is parameter for that function. 
        """
        self.send("display", {"head":"call_func", "data":{"func":function, "param":param}})
    
    
    def clearLpc(self):
        """ Resets the lpc service if it exists """
        self.kernel.clearLpc()


    def setErrorLayout(self, message=None, sleep=0):
        """ 
        Changes layout to the error layout.
        Message is the message to be displayed and sleep is the amount of time which the system sould sleep
        """
        self.setLayout("error")
        if message != None:
            errorMsg = message
        else:
            errorMsg = "An Error Occurred"
        self.invokeLayoutFunction("updateErrorText", errorMsg )
        time.sleep(sleep)


    def setLoadingScreen(self, message=""):
        self.setLayout("loading")
        self.invokeLayoutFunction("updateInfoText", message)


