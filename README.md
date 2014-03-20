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
To create your own service inherit from `red.services.base.Service`




Drivers
-------
Drivers are the used to connect to physical devices. 
Currently only one standard drivers is included, namely the `NfcReader` which wraps the api of an NFC reader.
