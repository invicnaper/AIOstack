.. role:: bash(code)
   :language: bash
Arguments
==========================================
There many arguments for using AIOstack, here's the full-list :

- --method
- --version
- --no-vm
- --no-hardware
- --interface
- --force


--method
---------
Telling AIOstack which method you want to use for installing OpenStack

:bash:`./AIOstack.py --method <name>`


--version
----------
Telling AIOstack which version of OpenStack you want to install

:bash:`./AIOstack.py --version <name>`

--novm
--------
Disabling the check of the virtual machine

--nohardware
-----------------
Disabling the check of hardware perf

--interface
-----------------
set the interface name, ex : eth0

This is required when using devstack


--force
-----------------
to force devstack to install OpenStack
