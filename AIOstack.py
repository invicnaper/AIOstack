#!/usr/bin/python
#   @ AIOstack helps you to install openstack in your virtualMachine for testing
#   @ Hamza Bourrahim
#   @ Version 0.1
#   @ For Centos / Redhat
#
#                   GNU LESSER GENERAL PUBLIC LICENSE
#                       Version 3, 29 June 2007
#
# Copyright (C) 2007 Free Software Foundation, Inc. <http://fsf.org/>
# Everyone is permitted to copy and distribute verbatim copies
# of this license document, but changing it is not allowed.
#
#
#  This version of the GNU Lesser General Public License incorporates
#the terms and conditions of version 3 of the GNU General Public
#License, supplemented by the additional permissions listed below.
#
#  0. Additional Definitions.
#
#  As used herein, "this License" refers to version 3 of the GNU Lesser
#General Public License, and the "GNU GPL" refers to version 3 of the GNU
#General Public License.
#
#  "The Library" refers to a covered work governed by this License,
#other than an Application or a Combined Work as defined below.
#
#  An "Application" is any work that makes use of an interface provided
#by the Library, but which is not otherwise based on the Library.
#Defining a subclass of a class defined by the Library is deemed a mode
#of using an interface provided by the Library.
#
#  A "Combined Work" is a work produced by combining or linking an
#Application with the Library.  The particular version of the Library
#with which the Combined Work was made is also called the "Linked
#Version".
#

#===================================
#            modules to install
# psutil
#===================================

import os
import sys
import argparse
import platform
import subprocess
import traceback
import time
from threading import Thread
from psutil import virtual_memory

RED     = "\033[31m"
GREEN   = "\033[32m"
BLUE    = "\033[34m"
YELLOW  = "\033[36m"
COL     = "\033[33m"
DEFAULT = "\033[0m"

VERSION = "0.2"
AUTHOR  = "Hamza Bourrahim"

ACTION  = BLUE + "[+] " + DEFAULT
ERROR   = RED + "[!] " + DEFAULT
OK      = GREEN + "[o] " + DEFAULT
OKLINE  = GREEN + "[Ok] " + DEFAULT
ERLINE  = RED +   "[Error] " + DEFAULT
NOTICE  = YELLOW + "[@] " + DEFAULT
WARN    = COL + "[%]" + DEFAULT

#glob var
distrib = ""
hypervizor =""
flag_rdo_installed = 0
flag_installed = 0
flag_rdo_cleanup = 0
openstack_version = ""

GB_4 = 4 *1024 * 1024 * 1024
GB_6 = 6 *1024 * 1024 * 1024

#===================================
#            Functions
#===================================

def header():
    """ showing header informations """
    print "-----------------------------------------------------------------------------"
    print RED + "\tAIOstack" + DEFAULT
    print "@ AIOstack helps you to install Openstack in your virtualMachine for testing"
    print "@ Author : " + BLUE + AUTHOR + DEFAULT
    print "@ Version : " + GREEN + VERSION + DEFAULT
    print "-----------------------------------------------------------------------------"
    print ""

def printAction(message):
    """ printing action is running """
    sys.stdout.write(ACTION + message +' ..')
    #handle len of message
    words = len(message.split())
    if words == 3:
        sys.stdout.write("\t\t\t\t\t")
    if words == 4:
        sys.stdout.write("\t\t\t\t")
    if words == 5:
        sys.stdout.write("\t\t\t")
    if words == 6:
        sys.stdout.write("\t\t")
    sys.stdout.flush()

def checkOs():
    """ OS name and OS release """
    printAction("checking if running on Linux")
    if platform.system() == "Linux":
        print OKLINE
        #check if using centos
        printAction("checking if using CentOs")
        if platform.linux_distribution()[0].find("centos") or platform.linux_distribution()[0].find("CentOs"):
            print OKLINE
            distrib = platform.linux_distribution()[0]
            return 1
        else:
            print ERLINE
            return -1
    else:
        print ERLINE
        return -1

def checkIfVM():
    """ check if running on VM using virt-what """
    printAction("checking if running on Virtual Machine")
    try:
        output = subprocess.check_output(["virt-what"], stderr=subprocess.STDOUT, shell=True)
        if output == "":
            #no vm
            print ERLINE
            return -1
        else :
            #running vm
            print OKLINE
            hypervisor = output
            return 1
    except OSError as e:
        if e.errno == os.errno.ENOENT:
            print ERLINE
            #install Virt-what
            install(["sudo","yum","install","-y","virt-what"],"virt-what")
            #re check if running in VM
            checkifVM()
    except subprocess.CalledProcessError, e:
        print ERLINE
        print ERROR + e.output

def checkRoot():
    """ check if running as root  """
    printAction("checking if running as Root")
    if os.geteuid() != 0:
        print ERLINE
        return -1
    else:
        print OKLINE
        return 1
def checkHardware():
    """ checking ram and processors and network adapters """
    #ram
    printAction("checking vertual memory")
    mem = virtual_memory()
    total = mem.total
    if int(total) < GB_4:
        return -1
    print OKLINE

#===================================
#            install package
#===================================
def threadInstall(cmd):
    """ thread for installing package """
    global flag_installed

    try:
        #install openstack version
        subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        #installed
        flag_installed = 1
    except OSError as e:
        if e.errno == os.errno.ENOENT:
            flag_installed = 1
            print ERLINE
    except subprocess.CalledProcessError, e:
        flag_installed = 1
        print ERLINE
        print ERROR + e.output

def install(cmd, name):
    """ installing package """
    global flag_installed
    printAction("installing " + name)
    background_thread = Thread(target=threadInstall, args=(cmd))
    background_thread.start()
    spinner = spinning_cursor()
    while flag_installed == 0:
        sys.stdout.write(spinner.next())
        sys.stdout.flush()
        time.sleep(0.1)
        sys.stdout.write('\b')
    print OKLINE
#===================================
#            RDO method
#===================================
def checkIfalreadyDone():
    """ check if packstack is installed , so to clean up and reinstall everything """
    printAction("checking if packstack is installed")
    try:
        output = subprocess.check_output(["packstack"], stderr=subprocess.STDOUT)
        #installed
        print OKLINE
        cleanUp()
    except OSError as e:
        if e.errno == os.errno.ENOENT:
            print ERLINE
            installRdo()
    except subprocess.CalledProcessError, e:
        print ERLINE
        print ERROR + e.output

def threadInstallRdo():
    """ thread for installing rdo """
    global flag_rdo_installed

    try:
        #install openstack version
        subprocess.check_output(["yum","install","-y","centos-release-openstack-"+ openstack_version], stderr=subprocess.STDOUT)
        #install packstack
        subprocess.check_output(["yum","install","-y","openstack-packstack"], stderr=subprocess.STDOUT)
        #installed
        flag_rdo_installed = 1
    except OSError as e:
        if e.errno == os.errno.ENOENT:
            flag_rdo_installed = 1
            print ERLINE
    except subprocess.CalledProcessError, e:
        flag_rdo_installed = 1
        print ERLINE
        print ERROR + e.output

def installRdo():
    """ installing rdo """
    global flag_rdo_installed
    printAction("installing rdo packstack")
    background_thread = Thread(target=threadInstallRdo)
    background_thread.start()
    spinner = spinning_cursor()
    while flag_rdo_installed == 0:
        sys.stdout.write(spinner.next())
        sys.stdout.flush()
        time.sleep(0.1)
        sys.stdout.write('\b')
    print OKLINE

def threadcleanUp():
    """ thread for installing rdo """
    global flag_rdo_cleanup

    try:
        subprocess.check_output(["yum","remove","openstack-packstack"], stderr=subprocess.STDOUT)
        subprocess.check_output(["yum","remove","centos-release-openstack-"+ openstack_version], stderr=subprocess.STDOUT)
        #installed
        flag_rdo_cleanup = 1
    except OSError as e:
        if e.errno == os.errno.ENOENT:
            flag_rdo_cleanup = 1
            print ERLINE
    except subprocess.CalledProcessError, e:
        flag_rdo_cleanup = 1
        print ERLINE
        print ERROR + e.output

def cleanUp():
    """ clean a previous installation """
    global flag_rdo_installed
    printAction("cleaning the previous installation")
    background_thread = Thread(target=threadcleanUp)
    background_thread.start()
    spinner = spinning_cursor()
    while flag_rdo_cleanup == 0:
        sys.stdout.write(spinner.next())
        sys.stdout.flush()
        time.sleep(0.1)
        sys.stdout.write('\b')
    #reinstall
    print OKLINE
    installRdo()

def spinning_cursor():
    while True:
        for cursor in '|/-\\':
            yield cursor

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='AIOstack helps you to install openstack in your virtualMachine for testing')
  parser.add_argument('--verbose',
    action='store_true',
    help='verbose flag' )
  parser.add_argument('--method', nargs=1, help="set the install methode")
  parser.add_argument('--version', nargs=1, help="set the openstack version, ex: ocata")
  parser.add_argument('--novm',action='store_true', help="skip vm check")
  args = parser.parse_args()

  try:
      header()
      #geting install method
      if args.method:
          print NOTICE + "# Env Check #"
          if args.method[0] == "rdo":
              #must be run as root for thi method"
              if args.version :
                  openstack_version = args.version[0]
              else:
                  print ERROR + "no version, please use --help"
                  sys.exit(0)
              if checkRoot() == -1:
                  print ERROR + "aborting installation"
                  sys.exit(0)
              print NOTICE + "@ using rdo as method @"
              #check if running on Linux and using Centos
              if checkOs() == -1:
                  print ERROR + "aborting installation"
                  sys.exit(0)
              #checking if running on virtual machine and using CentOS
              if args.novm:
                  print WARN + "skiping vm check"
              else:
                  if checkIfVM() == -1:
                      print ERROR + "aborting installation"
                      sys.exit(0)
              #Hardware Check
              print NOTICE + "# Hardware Check #"
              checkHardware()
              #check packstack
              print NOTICE + "# Software Check #"
              checkIfalreadyDone()
              #os config
      else :
          print ERROR + "no method, please use --help"

  except KeyboardInterrupt:
      print ""
      print ERROR + "Shutdown requested"
      print ERROR + "aborting installation"
  except Exception:
      traceback.print_exc(file=sys.stdout)
      print ERROR + "An Error occured"
      print ERROR + "aborting installation"
