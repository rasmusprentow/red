RED
===

Rapid Embedded Development

Getting started
---------------
1. Use the folders specified below in "Filestructure"
2. Copy the `red/init-sample.conf` into `config/init.conf`


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
To get documentation use 

     pydoc red/activities.py


