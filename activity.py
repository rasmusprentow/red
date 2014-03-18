#activity.py


class Activity(object):
    """docstring for Activity"""

    def __init__(self, kernel):
        super(Activity, self).__init__()
        self.kernel = kernel
    
    def onCreate(self, data=None):
        pass



    def setLayout(self,layout):
        self.kernel.send("display", {"head":"set_layout", "data":layout})

    def send(self,service,message):
        self.kernel.send(service, message)

    
    def switchActivity(self,activity,data=None):
        self.kernel.switchActivity(activity,data)


    def emptyQueue(self,name):
        self.kernel.emptyQueue(name)


    @property
    def session(self):
        return self.kernel.getSession()
   

    def callLayoutFunc(self, func, param):
        self.send("display", {"head":"call_func", "data":{"func":func, "param":param}})