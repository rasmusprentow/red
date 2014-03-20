red
===

Rapid Embedded Development

Getting started
===============
Use create the folders specified in below in "Filestructure"
Copy the `red/init-sample.conf` into `config/init.conf`


Filestructure
=============
To use RED your project must have the following file structure: 

     <projectfolder>/
     ............... layouts/
     ............... config/
     ............... helpers/
     ............... activities/

Activities
==========
The core of any red project is the actitivies.
Inherit from the `red.activity.Activity` to create your own activities. 
To get documentation use 

     pydoc red/activities.py


