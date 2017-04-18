#!/usr/bin/python
#   @ AIOstack helps you to install openstack in your virtualMachine for testing
#   @ Hamza Bourrahim
#   @ Version 0.3
#   @ For Centos / Redhat / Ubuntu
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
import git
import socket
import fcntl
import struct
import getpass
import pwd
import crypt

RED     = "\033[31m"
GREEN   = "\033[32m"
BLUE    = "\033[34m"
YELLOW  = "\033[36m"
COL     = "\033[33m"
DEFAULT = "\033[0m"

VERSION = "0.3"
AUTHOR  = "Hamza Bourrahim"

ACTION  = BLUE + "\t[+] " + DEFAULT
ERROR   = RED + "\t[!] " + DEFAULT
OK      = GREEN + "\t[o] " + DEFAULT
OKLINE  = GREEN + "[Ok] " + DEFAULT
ERLINE  = RED +   "[Error] " + DEFAULT
NOTICE  = YELLOW + "[@] " + DEFAULT
WARN    = COL + "\t[%] " + DEFAULT

#glob vars
distrib = ""
hypervizor =""
flag_rdo_installed = 0
flag_installed = 0
flag_task_done = 0
flag_git_done = 0
git_directory = None
flag_rdo_cleanup = 0
openstack_version = ""
interface = None

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
    if words == 2:
        sys.stdout.write("\t\t\t\t")
    if words == 3:
        sys.stdout.write("\t\t\t\t")
    if words == 4:
        sys.stdout.write("\t\t\t\t")
    if words == 5:
        sys.stdout.write("\t\t\t")
    if words == 6:
        sys.stdout.write("\t\t")
    sys.stdout.flush()

def checkOs(os):
    """ OS name and OS release """
    printAction("checking if running on Linux")
    if platform.system() == "Linux":
        print OKLINE
        #check if using centos
        if os == 1:
            printAction("checking if using CentOs")
            if platform.linux_distribution()[0].find("centos") or platform.linux_distribution()[0].find("CentOs"):
                print OKLINE
                distrib = platform.linux_distribution()[0]
                return 1
            else:
                print ERLINE
                return -1
        if os == 2:
            printAction("checking if using Ubuntu")
            if platform.linux_distribution()[0] == "ubuntu" or platform.linux_distribution()[0] == "Ubuntu":
                print OKLINE
                distrib = platform.linux_distribution()[0]
                return 1
            else:
                print ERLINE
                return -1

    else:
        print ERLINE
        return -1

def checkIfVM(osT):
    """ check if running on VM using virt-what """
    printAction("checking if running on Virtual Machine")
    try:
        output = subprocess.check_output(["virt-what"], stderr=subprocess.STDOUT)
        if output == "":
            #no vm
            print ERLINE
            return -1
        else :
            #running vm
            print OKLINE
            hypervisor = output
            print OK + "Hypervisor :  " + hypervisor
            return 1
    except OSError as e:
        if e.errno == os.errno.ENOENT:
            print ERLINE
            #install Virt-what
            if osT == 1:
                install(["sudo","yum","install","-y","virt-what"],"virt-what")
            if osT == 2:
                install(["sudo","apt-get","install","-y","virt-what"],"virt-what")
            #re check if running in VM
            return checkIfVM(osT)
    except subprocess.CalledProcessError, e:
        print ERLINE
        print ERROR + e.output
        return -1

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
        print ERLINE
        return -1
    print OKLINE

#===================================
#            install package
#===================================
def threadInstall(*cmd):
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

def threadtask(*cmd):
    """ thread for installing package """
    global flag_task_done

    try:
        subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        #installed
        flag_task_done = 1
    except OSError as e:
        if e.errno == os.errno.ENOENT:
            flag_task_done = 1
            print ERLINE
    except subprocess.CalledProcessError, e:
        flag_task_done = 1
        print ERLINE
        print ERROR + e.output

def task(cmd, message):
    """ installing package """
    global flag_task_done
    printAction(message)
    background_thread = Thread(target=threadtask, args=(cmd))
    background_thread.start()
    spinner = spinning_cursor()
    while flag_task_done == 0:
        sys.stdout.write(spinner.next())
        sys.stdout.flush()
        time.sleep(0.1)
        sys.stdout.write('\b')
    print OKLINE
#===================================
#            git method
#===================================
def threadgit(cmd, cmd_opt, gitP):
    """ thread for installing package """
    global flag_git_done

    try:
        #git command
        if cmd == "clone":
            gitP.clone(cmd_opt)
        if cmd == "checkout":
            gitP.checkout(cmd_opt)
        #installed
        flag_git_done = 1
    except OSError as e:
        if e.errno == os.errno.ENOENT:
            fflag_git_done = 1
            print ERLINE
    except subprocess.CalledProcessError, e:
        flag_git_done = 1
        print ERLINE
        print ERROR + e.output
def gitExec(cmd, cmd_opt, message, dirP):
    """ exec git command """
    global flag_git_done
    printAction(message)
    gitP = git.cmd.Git(dirP)
    background_thread = Thread(target=threadgit, args=(cmd, cmd_opt, gitP))
    background_thread.start()
    spinner = spinning_cursor()
    while flag_git_done == 0:
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

#===================================
#            devstack method
#===================================
def getIpaddr(ifname):
    """ get ip address """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

def createLocalConf(ip, password, mysql_password):
    """ creating a localconf """
    printAction("creating local.conf")
    # Open file
    local = open("local.conf", "wb")
    local.write("[[local|localrc]]\n");
    local.write("HOST_IP=" + ip + "\n")
    local.write("SERVICE_HOST=$HOST_IP\n");
    local.write("ADMIN_PASSWORD="  + password + "\n")
    local.write("DATABASE_PASSWORD="  + mysql_password + "\n")
    local.write("RABBIT_PASSWORD="  + password + "\n")
    local.write("SERVICE_PASSWORD=$ADMIN_PASSWORD\n")

    # Close opened file
    local.close()
    print OKLINE

def change_user():
    os.setuid(10033)

def addUser():
    """ creating aiostack user """
    password ="aiostack"
    encPass = crypt.crypt(password,"22")
    task(["useradd","-m","-d","/home/aiostack","-p",encPass,"aiostack"],"creating aiostack user")
    task(["sudo ","usermod","-a","-G","sudo","aiostack"],"adding it to sudo group")
    appendToSudoers()

def appendToSudoers():
    """ add user to sudoers """
    printAction("append to sudoers")
    # Open file
    local = open("/etc/sudoers", "a")
    local.write("aiostack    ALL=(ALL:ALL) ALL\n");

    # Close opened file
    local.close()
    print OKLINE

def installDevstack():
    """ installing devstack """
    #install git
    install(["sudo", "apt-get","install","-y","git"],"git")
    #cd scripts
    #task(["cd","scripts"],"moving to scripts directory")
    #clone repo
    if os.path.exists("scripts/devstack/") == 1:
        print WARN + "devstack exist"
    else:
        gitExec("clone", "https://github.com/openstack-dev/devstack.git", "cloning devstack", "./")
        #task(["git", "clone",""], "cloning devstack")
    #moving devstack
    if os.path.exists("devstack/"):
        task(["mv", "devstack/", "scripts/"],"moving devstack scripts")
    #changing directory
    os.chdir("scripts/devstack")
    #git checkout stable/version
    gitExec("checkout", "stable/" + openstack_version, "checking out " + openstack_version, "./")
    #task(["git","checkout","], "checking out " + openstack_version)
    #get IP address
    ip = getIpaddr(interface)
    print WARN + "IPaddr : " + ip
    #ask for password
    password = getpass.getpass(WARN + "Set OpenStack Password : ")
    mysql_password = getpass.getpass(WARN + "Set Mysql Password : ")
    #edit conf file
    createLocalConf(ip, password, mysql_password)
    #creating user
    try:
        pwd.getpwnam('aiostack')
    except KeyError:
        print ERROR + "User aiostack doesn't exist"
        addUser()
    uid = pwd.getpwnam('aiostack').pw_uid
    print WARN + "aiostack user found, id : ", uid
    #change to aiostack user
    #stacking
    if args.force:
        task(["sudo","-u","aiostack","-p","aiostack","FORCE=yes","./stack.sh"],"Forcing stacking, please wait")
    else:
        task(["sudo","-u","aiostack","-p","aiostack","./stack.sh"],"stacking, please wait")
    #change to root
    #start apache
    #task(["sudo","systemctl","start","apache2"],"starting apache")



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
  parser.add_argument('--no-vm',action='store_true', help="skip vm check")
  parser.add_argument('--no-hardware',action='store_true', help="skip hardware check")
  parser.add_argument('--interface',nargs=1, help="set the interface name")
  parser.add_argument('--force',action='store_true', help="to force devstack")
  args = parser.parse_args()

  try:
      header()
      #geting install method
      if args.method:
          print NOTICE + "# Env Check #"
          if args.method[0] == "rdo":
              #must be run as root for this method"
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
              if checkOs(1) == -1:
                  print ERROR + "aborting installation"
                  sys.exit(0)
              #checking if running on virtual machine and using CentOS
              if args.no_vm:
                  print WARN + "skiping vm check"
              else:
                  stat = checkIfVM(1)
                  if  stat == -1:
                      print ERROR + "aborting installation"
                      sys.exit(0)
              #Hardware Check
              print NOTICE + "# Hardware Check #"
              if args.no_hardware:
                  print WARN + "skiping hardware check"
              else:
                  if checkHardware() == -1:
                      print ERROR + "aborting installation"
                      sys.exit(0)
              #check packstack
              print NOTICE + "# Software Check #"
              checkIfalreadyDone()
              #os config
          if args.method[0] == "devstack":
              if args.version :
                  openstack_version = args.version[0]
              else:
                  print ERROR + "no version, please use --help"
                  sys.exit(0)
              if args.interface :
                  interface = args.interface[0]
              else:
                  print ERROR + "no interface, please use --help"
                  sys.exit(0)
              #check if user is sudoE
              if checkRoot() == -1:
                  print ERROR + "aborting installation"
                  sys.exit(0)
              #check if running on Linux and using ubuntu
              if checkOs(2) == -1:
                  print ERROR + "aborting installation"
                  sys.exit(0)
              #checking if running on virtual machine and using CentOS
              if args.no_vm:
                  print WARN + "skiping vm check"
              else:
                  stat = checkIfVM(2)
                  if  stat == -1:
                      print ERROR + "aborting installation"
                      sys.exit(0)
              #Hardware Check
              print NOTICE + "# Hardware Check #"
              if args.no_hardware:
                  print WARN + "skiping hardware check"
              else:
                  if checkHardware() == -1:
                      print ERROR + "aborting installation"
                      sys.exit(0)
              #install devstack
              installDevstack()
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
