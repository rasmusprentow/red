RED
===

Rapid Embedded Development

Getting started
---------------
1. Use the folders specified below in "Filestructure"
2. Copy the `red/init-sample.conf` into `config/init.conf`


Dependencies
------------

 - configparser
 - pyzmq
 - pyside*
 - sqlalchemy*
 - pyserial*

The star marked can be avoided, but are used by some standard services. 

Filestructure
-------------
To use RED in your project you need the following file structure: 

     <projectfolder>/
     ............... layouts/
     ............... config/
     ............... helpers/
     ............... activities/

Activities
----------
The core of any RED project is the actitivies.
Inherit from the `red.activity.Activity` to create your own activities. 
To get documentation use: 

     pydoc red/activities.py

Config
------

To use the init.conf you need the following line:

    from red.config import config

Usage:

    config.get('Section','Option')
    
    
Services
--------
Besides activities services are essential. 
Services run in their own thread, and are used to connect to drivers (See drivers)
To create your own service inherit from `red.services.base.Service` and `Thread`. 
The reason we must explicitly inherit from `Thread` and not just make the base service do so is that the standard sarvice named `display` must use `QThread` to work. (If you forget the `Thread` you will have a deadlock`)
Here is an example:


    from red.services.base import Service
    from threading import Thread
    import zmq
    class Keyinput(Service,Thread):

        def processMessage(self,message):
            #Do somthing here
            pass

Drivers
-------
Drivers are the used to connect to physical devices. 
Currently only one standard drivers is included, namely the `NfcReader` which wraps the api of an NFC reader.
