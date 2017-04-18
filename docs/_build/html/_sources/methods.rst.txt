.. role:: bash(code)
   :language: bash
Methods for installing Openstack
==========================================

There are many methods to deploy Openstack, here is a list of the supported methods

- rdo packstack
- devstack
- openstack-ansible
- TripleO
- Fuel


RDO Packstack
---------------
Using rdo packages to installOpenstack

:bash:`./AIOstack.py --method rdo --version <version>`

DevStack
---------------
Using the ./stack.sh

:bash:`./AIOstack.py --method devstack --version <version> --interface <name>`

**--interface** is required if you're using devstack

OpenStack-Ansible
------------------
Using Ansible

:bash:`./AIOstack.py --method ansible --version <version>`


TripleO
----------
TripleO is short for “OpenStack on OpenStack”

Not implemented yet

Fuel
-----
Fuel is an open-source tool that simplifies and accelerates the initial deployment of OpenStack

Not implemented yet
