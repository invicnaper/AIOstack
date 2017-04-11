.. role:: bash(code)
   :language: bash
Getting Started
===============

This document will show you how to get up and use AIOstack to quickly install OpenStack


Quick Installation
--------------------

AIOstack default method to install openstack is **rdo packstack**, by default AIOstack will use the **--all-in-one** option.

you have to execute the script with two options, **--method** and **--version**, for installing the ocata version use

:bash:`./AIOstack.py --method rdo --version ocata`

The **rdo packstack** method needs the root privileges , so add sudo to the command line

:bash:`sudo ./AIOstack.py --method rdo --version ocata`

The script will check if you're running it as root or not.
