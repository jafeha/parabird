#!/usr/bin/env python
# encoding: utf-8 
import argparse
import ConfigParser
import codecs
import urllib
import subprocess
import sys
import os
import tempfile
import shlex
import shutil
import tarfile
import zipfile
from utils import detect_stick
import logging
import extract_files
from extract_files import extract_tarfile
from extract_files import extract_zipfile

#from http://docs.python.org/2/howto/logging-cookbook.html explainations there

tempdir = tempfile.mkdtemp()
logfile = os.path.realpath(tempdir+"parabirdy_log.txt")

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename=tempdir+"parabirdy_log.txt",
                    filemode='w')
                    
console = logging.StreamHandler()
console.setLevel(logging.INFO)
#formatter = logging.Formatter('%(name)-6s: %(levelname)-6s %(message)s')
formatter = logging.Formatter('[%(levelname)s::%(name)s]: %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)
mainLogger = logging.getLogger('main')



mainLogger.info('Logfile: ' + logfile)

def dependency_check(checked_app):
# This function tests dependencies. All stdout is send to devnull
    try:
        FNULL = open(os.devnull, 'w')
        subprocess.check_call(checked_app, stdout=FNULL)

    except OSError:
        mainLogger.error("[ERROR] Missing Depedencies:", checked_app,+"not installed, exiting...")
        from sys import exit
        exit()

def update_config(section, key, value_from_argparser):
# This function checks if there is any parameter given, 
# If there is a parameter given, it updates the config 
# if not it uses default values from config.ini
    if value_from_argparser:
        mainLogger.info('Parameter given, device or container is: ' + value_from_argparser)
        parser.set(section, key, value_from_argparser)

    if value_from_argparser == None:
        mainLogger.info("Taking %s %s from Config: %s" % (section, key, parser.get(section, key) ))

def download_application(progname, url, filename):
# This function tries to downloads all the programs we 
# want to install. 
    mainLogger.info('[INFO] Downloading: ' + progname)
    
    try:
        returnobject = urllib.urlretrieve(url, filename=tempdir+"/"+filename)
    except:
        mainLogger.error("[ERROR] Could not download", progname)
        return None

#def extract_files(path, destination):
# This function obviously extracts the file in path to destination
#	tar = tarfile.open(path)
#	tar.extractall(destination)
#	tar.close()


# Parsing Arguments given as Parameter from Shell
parser = argparse.ArgumentParser()
parser = argparse.ArgumentParser(description='')
parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
parser.add_argument("-d", "--device", help="Device Flag to specify USB Stick")
parser.add_argument("-t", "--thunder", help="Specify Thunderbird version to download")
parser.add_argument("-b", "--torbirdy", help="Specify Torbirdy Version")
parser.add_argument("-e", "--enigmail", help="Specify Enigmail Version") 
parser.add_argument("-a", "--vidalia", help="Specify Vidalia Version")
parser.add_argument("-n", "--container_name", help="Specify Container Name")

args = parser.parse_args()

# Importing Config File: config.ini
from ConfigParser import SafeConfigParser
parser = SafeConfigParser()
with codecs.open('config.ini', 'r', encoding='utf-8') as f:
    parser.readfp(f)

# PLATFORM SPECIFIC SHIT
# http://docs.python.org/2/library/sys.html#sys.platform
# There exists another path to the truecrypt binary, also tc 
# is NOT in the path. We don't support Win32.
if (sys.platform=="darwin"):
    parser.set('truecrypting','tc_binary',parser.get('truecrypting','tc_mac_binary'))
elif (sys.platform=="win32"):
    mainLogger.error("parabirdy does'nt run on windows. by us a windows license (and some gifts) or reboot in linux. virtualisation might also work")
    exit()

# Removed, because there is no verbosity support, could be reimplemented later.
# see the logging module for built in verbosity support
#if args.verbose:
#   mainLogger.info("verbosity turned on")

print "%" * 30, "\nChecking Dependencies and Configure\n", "%" * 30

mainLogger.info("[INFO] Checking all Dependencies...")

try:
    dependency_check([parser.get('truecrypting', 'tc_binary'), "--text", "--version"])
    dependency_check("7z")
    dependency_check("dmg2img")
except: 
    mainLogger.error("[ERROR] Dependency Checks failed large scale, exiting...")
    from sys import exit
    exit()



mainLogger.info("[INFO] Configuring...")

# Setting Parameters given from argparse

try:
    update_config("DEFAULT", "device", args.device)
    #update_config("thunderbird", "version", args.thunder)
    #update_config("torbirdy", "version", args.torbirdy)
    #update_config("enigmail", "version", args.enigmail)
    #update_config("vidalia", "version", args.vidalia)
    update_config("DEFAULT", "container_name", args.container_name)

except NameError: 
    mainLogger.error("[ERROR] Hier ist was ganz arg schiefgelaufen")


# Setting Path Parameters given by tempfile
tempdir = os.path.realpath(tempfile.mkdtemp())
tc_mountpoint = os.path.realpath(tempfile.mkdtemp())

print "%" * 30, "\nMounting and Truecrypting\n", "%" * 30

# Use an USB-Stick given by a Parameter or a detected one:
if args.device:
    try:
        mountpoint = os.path.realpath(tempfile.mkdtemp())
        update_config("DEFAULT", "device", args.device)
	
    except NameError:
        mainLogger.error("[ERROR] Hier ist was ganz arg schiefgelaufen")
else: 
    stick = detect_stick()
    #print stick

    #if we can write to the mountpoint of the stick, no need to re-mount it
    if (not(os.access(str(stick['mountpoint']), os.W_OK))): 
        #aka we cant write or stick detection did not work
        #question is: does it make sense to continue at this point?
        #which scenarios are possible (except detection not working)
        mountpoint = os.path.realpath(tempfile.mkdtemp())
        mainLogger.error("Stick detection did not work, try to run with what you specified")
        mainLogger.info('[INFO] Mounting USB Stick to' + mountpoint)

        try:
            subprocess.check_call(["mount", parser.get('DEFAULT', 'device'), mountpoint])
        except:
            mainLogger.error("[ERROR] Mounting", + parser.get('DEFAULT', 'device'), + "to", mountpoint, + "failed")
    else:
        parser.set('DEFAULT', "device", stick['device'])
        mountpoint = stick['mountpoint']

# Setting the Path for Truecrypt
parser.set('DEFAULT', 'container_path', mountpoint+"/"+parser.get('DEFAULT', 'container_name'))
parser.set('DEFAULT', 'tc_mountpoint', tc_mountpoint)

#Multiple Variables like this, because the logger only takes 1 argument:
mainLogger.info("[INFO] Creating Container " + parser.get('DEFAULT', 'container_name') + " on USB-Stick: " + parser.get('DEFAULT', 'device'))

# Exit if the container already exists
if os.path.exists(parser.get('DEFAULT', 'container_path')):
    mainLogger.info("The Container given ("+ parser.get('DEFAULT', 'container_path')+") already exists. Exiting...")
    exit()

# Create Container
mainLogger.info('Truecrypting create: '+ parser.get('truecrypting', 'create'))
subprocess.check_call(shlex.split(parser.get('truecrypting', 'create')))

# Mount Container
mainLogger.info("[INFO] Mounting Truecrypt Container")
subprocess.check_call(shlex.split(parser.get('truecrypting', 'mount')))

# Create Folders
mainLogger.info("[INFO] Creating Folders in Truecrypt Container:")

try:
    os.makedirs(parser.get('thunderbird_linux', 'path'))
    os.makedirs(parser.get('vidalia_linux', 'path'))

    os.makedirs(parser.get('thunderbird_windows', 'path'))
    os.makedirs(parser.get('vidalia_windows', 'path'))

    os.makedirs(parser.get('thunderbird_mac', 'path'))
    os.makedirs(parser.get('vidalia_mac', 'path'))

    os.makedirs(parser.get('enigmail', 'path'))
    os.makedirs(parser.get('torbirdy', 'path'))	

    # for extracting tb for mac os, we need to mount a dmg
    # i create an subfolder in tempdir for doing this
    os.makedirs(tempdir+"/dmg")

except OSError:
    mainLogger.error("[ERROR] Folder already exists")


# Download Applications	
mainLogger.info('[INFO] Starting to download Applications to: ' + tempdir)

download_application("Thunderbird [Linux]", parser.get('thunderbird_linux', 'url'), parser.get('thunderbird_linux', 'file'))
download_application("Thunderbird [Windows]", parser.get('thunderbird_windows', 'url'), parser.get('thunderbird_windows', 'file'))
download_application("Thunderbird [Mac OS]", parser.get('thunderbird_mac', 'url'), parser.get('thunderbird_mac', 'file'))
download_application("Torbirdy", parser.get('torbirdy', 'url'), parser.get('torbirdy', 'file'))
download_application("Enigmail", parser.get('enigmail', 'url'), parser.get('enigmail', 'file'))
download_application("Vidalia [Linux]", parser.get('vidalia_linux', 'url'), parser.get('vidalia_linux', 'file'))
download_application("Vidalia [Windows]", parser.get('vidalia_windows', 'url'), parser.get('vidalia_windows', 'file'))
download_application("Vidalia [Mac OS]", parser.get('vidalia_mac', 'url'), parser.get('vidalia_mac', 'file'))

mainLogger.info("[INFO] Extracting Thunderbird [Linux]")
try:
#    extract_files(tempdir+"/"+parser.get('thunderbird_linux', 'file'), parser.get('thunderbird_linux', 'path'))
    extract_tarfile(tempdir+"/"+parser.get('thunderbird_linux', 'file'), parser.get('thunderbird_linux', 'path'))
except:
    mainLogger.error("[ERROR] Could not extract Thunderbird [Linux]")

#mainLogger.info("[INFO] Extracting Thunderbird [Windows]")

mainLogger.info("[INFO] Extracting Thunderbird [Mac OS]")

#try:
#subprocess.check_call(["dmg2img", tempdir+"/"+parser.get('thunderbird_mac', 'file')])
#subprocess.check_call(["mount -t hfsplus -o loop", tempdir+"/"+parser.get('thunderbird_mac', 'uncompressedfile'), tempdir+"/dmg/"])
#shutil.copytree(tempdir+"/dmg/", parser.get('thunderbird_mac', 'path'))
#except:
    # mainLogger.error("[ERROR] Could not Extract Thunderbird [Mac OS]")

mainLogger.info("[INFO] Extracting Vidalia [Linux]")
try:
    extract_tarfile(tempdir+"/"+parser.get('vidalia_linux', 'file'), parser.get('vidalia_linux', 'path'))
except:
    mainLogger.error("[ERROR] Could not extract Vidalia [Linux]")

#mainLogger.info("[INFO] Extracting Vidalia [Windows"]
mainLogger.info("[INFO] Extracting Vidalia [Mac OS]")
try: 
    extract_zipfile(tempdir+"/"+parser.get('vidalia_mac', 'file'), parser.get('vidalia_mac', 'path'))
except:
    mainLogger.error("[ERROR] Could not extract Vidalia [Mac OS]")

mainLogger.info("[INFO] Extracting Torbirdy to Profile Folder")
try:
    extract_zipfile(tempdir+"/"+parser.get('torbirdy', 'file'), parser.get('torbirdy', 'path'))
except:
    mainLogger.error("[ERROR] Could not extract Torbirdy")

mainLogger.info("[INFO] Extracting Enigmail to Profile Folder")
try:
    extract_zipfile(tempdir+"/"+parser.get('enigmail', 'file'), parser.get('enigmail', 'path'))
except:
    mainLogger.error("[ERROR] Could not extract Enigmail")

# Unmounting Truecrypt
mainLogger.info("[INFO] Unmounting Truecrypt Container")
mainLogger.debug('UNMOUNT COMMAND: ' + parser.get('truecrypting', 'unmount'))
subprocess.check_call(shlex.split(parser.get('truecrypting', 'unmount')))

# Unmounting USB-Stick
mainLogger.info("[INFO] Unmounting USB-Stick")

try:
    subprocess.check_call(["umount", mountpoint])

except:
    
    if (sys.platform=="darwin"):
       mainLogger.info("[INFO] please unmount your stick via the finder.")
    else:
        mainLogger.error("[Error] Unmounting", + mountpoint, + "failed")
        

# Removing Temporary folders
mainLogger.info("[INFO] Cleaning up Temporary Directories")

try:
    if args.device:
        os.removedirs(mountpoint)
    os.removedirs(tempdir)
    os.removedirs(tc_mountpoint)
except OSError:
    mainLogger.error("Some temporary Directories could not be removed")
