import threading
import zmq
import logging

class Service(object):

    def __init__(self, name, context=None):
        super(Service, self).__init__() 
        real_context = context or zmq.Context.instance();
        self.socket = real_context.socket(zmq.PAIR)
        self.logger = logging.getLogger("kernel.Service." +  __name__)
        self.logger.info("Connection on socket : " + name)
        self.socket.connect(name)
        self.running = True
    
    def onCreate(self): 
        pass

    def run(self):
        """ 
        Do not override this method
        """
        while self.running:
            try:
                message = self.socket.recv_json()
            except zmq.error.ContextTerminated:
                break;
            if 'head' not in message:
                message = {'head' : 'error', 'data' : 'Malformed data: Head missing'}
                self.send(message)
            elif message['head'] == "system_message":

                if message['head'] == "stop":
                    self.running = False
                    break;
                elif message['data'] == "echo":
                    self.send({'head' : 'system_message', 'data' : 'echo'})
                elif message['data'] == "restart":
                    self.onRestart()
            else:
                if not self.processMessage(message):
                    message = {'head' : 'error', 'data' : self.__class__.__name__ + ': Command not found: ' + message['head']}
                    self.send(message)

        self.logger.info(self.__class__.__name__ + " is now stopped.")

    def send(self, message):
        """ 
        Send message to the current activity.
        """
        self.socket.send_json(message)

    def onRestart(self):
        """ OVerride this method to implement custom restart functionality """
        pass
