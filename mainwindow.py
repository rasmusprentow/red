
from PySide import QtCore, QtGui, QtUiTools, QtDeclarative
from red.config import config,get_config
from services.display import Display

class MainWindow(QtGui.QMainWindow):
    _instance = None

    
    @staticmethod
    def instance():
        if MainWindow._instance == None:
            MainWindow._instance = MainWindow()
        return MainWindow._instance

    def __init__(self):
        super(MainWindow, self).__init__(None)
        self.context = None
        self.centralWidget = QtGui.QStackedWidget()
        self.setCentralWidget(self.centralWidget)
        self.setLayout("common/loading")
        
        if get_config(config,"GUI","fullscreen",default='false') == "true":
            self.showFullScreen()
        else:
            self.resize(480,272)
        Display._instance.functionSignal.connect(self.functionCall)
        Display._instance.layoutSignal.connect(self.setLayout)
        
     
    def functionCall(self, functionName, param):
        func = eval("self.view.rootObject()." + functionName)
        func(param)

    def setLayout(self, layout):
        self.view = QtDeclarative.QDeclarativeView()
        self.view.setSource(QtCore.QUrl.fromLocalFile( './layouts/'+ layout +'.qml' ))
        self.view.setResizeMode( QtDeclarative.QDeclarativeView.SizeRootObjectToView )

        if get_config(config,"GUI","cursor",default="false") != "true":
            self.view.setCursor(QtCore.Qt.BlankCursor)

        qcontext = self.view.rootContext() 
        qcontext.setContextProperty("context",Display._instance)
 
        self.centralWidget.addWidget(self.view)
        self.centralWidget.setCurrentWidget(self.view)