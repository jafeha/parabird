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


def download_application(progname, url):
# This function tries to downloads all the programs we 
# want to install. 
    print "[INFO] Downloading", progname
    
    try:
        # This Line works. if we need to deal more with the filename, i consider 
        # using  >>> os.path.basename('http://sub.domain.com/filename.zip') 'filename.zip'
        
        # why dont we save to /tmpdir/progname ??? this seems saver to me! procname can be
        # thunderbird_linux or smthng. sure we loose the ending, but that's not important imo
        
        returnobject = urllib.urlretrieve(url, filename=tempdir+"/"+url.split('/')[-1].split('#')[0].split('?')[0])
    except:
        mainLogger.error("[ERROR] Could not download", progname)
        return None

def extract_file(filename, destination):
# This function is used to extract the downloaded achives. 
# http://code.activestate.com/recipes/576714-extract-a-compressed-file/
    if filename.endswith('.zip'):
        opener, mode = zipfile.ZipFile, 'r'
    elif filename.endswith('.tar.gz') or filename.endswith('.tgz'):
        opener, mode = tarfile.open, 'r:gz'
    elif filename.endswith('.tar.bz2') or filename.endswith('.tbz'):
        opener, mode = tarfile.open, 'r:bz2'
    else: 
        raise ValueError, "Could not extract `%s` as no appropriate extractor is found for" % filename

    cwd = os.getcwd()
    os.chdir(destination)
    
    try:
        file = opener(filename, mode)
        try: file.extractall()
        finally: file.close()
    finally:
        os.chdir(cwd)



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
    print """parabirdy does'nt run on windows. by us a windows license (and some gifts)
or reboot in linux. virtualisation might also work"""
    exit()

# Removed, because there is no verbosity support, could be reimplemented later.
# see the logging module for built in verbosity support
#if args.verbose:
#   print "verbosity turned on"

print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
print "Checking Dependencies and Configure"
print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"

mainLogger.info("[INFO] Checking all Dependencies...")

try:
    dependency_check([parser.get('truecrypting', 'tc_binary'), "--text", "--version"])
    dependency_check("7z")
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
        print "Stick detection did not work, try to run with what you specified"
        print "[INFO] Mounting USB Stick to", mountpoint

        try:
            subprocess.check_call(["mount", parser.get('DEFAULT', 'device'), mountpoint])
        except:
            mainLogger.error("[ERROR] Mounting", + parser.get('DEFAULT', 'device'), + "to", mountpoint, + "failed")
    else:
        parser.set('DEFAULT', "device", stick['device'])
        mountpoint = stick['mountpoint']

# Setting the Path for Truecrypt
parser.set('truecrypting', 'container_path', mountpoint+"/"+parser.get('DEFAULT', 'container_name'))
parser.set('truecrypting', 'tc_mountpoint', tc_mountpoint)

#Multiple Variables like this, because the logger only takes 1 argument:
mainLogger.info("[INFO] Creating Container" + parser.get('truecrypting', 'container_name') + "on USB-Stick: " + parser.get('DEFAULT', 'device'))

# Exit if the container already exists
if os.path.exists(parser.get('truecrypting', 'container_path')):
    print "The Container given ("+ parser.get('truecrypting', 'container_path')+") already exists. Exiting..."
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
    os.makedirs(parser.get('truecrypting', 'tc_mountpoint')+"/apps/linux/thunderbird/")
    os.makedirs(parser.get('truecrypting', 'tc_mountpoint')+"/apps/linux/vidalia/")

    os.makedirs(parser.get('truecrypting', 'tc_mountpoint')+"/apps/win/thunderbird/")
    os.makedirs(parser.get('truecrypting', 'tc_mountpoint')+"/apps/win/vidalia/")

    os.makedirs(parser.get('truecrypting', 'tc_mountpoint')+"/apps/mac/thunderbird/")
    os.makedirs(parser.get('truecrypting', 'tc_mountpoint')+"/apps/mac/vidalia/")
	
except OSError:
    mainLogger.error("[ERROR] Folder already exists")


# Download Applications	
print "[INFO] Starting to download Applications to:", tempdir

download_application("Thunderbird [Linux]", parser.get('thunderbird', 'linux_url'))
#download_application("Thunderbird [Windows]", parser.get('thunderbird', 'windows_url'))
#download_application("Thunderbird [Mac OS]", parser.get('thunderbird', 'mac_url'))
#download_application("Torbirdy", parser.get('torbirdy', 'url'))
#download_application("Enigmail", parser.get('enigmail', 'url'))
#download_application("Vidalia [Linux]", parser.get('vidalia', 'linux_url'))
#download_application("Vidalia [Windows]", parser.get('vidalia', 'windows_url'))
#download_application("Vidalia [Mac OS]", parser.get('vidalia', 'mac_url'))

print "[INFO] Extracting Thunderbird [Linux]"
#try:
#extract_file(tempdir+"/"+"thunderbird-17.0.5.tar.bz2", "/tmp/lala")

# This works for me for simple extracting within the current directory (./)
tar = tarfile.open(tempdir+"/"+"thunderbird-17.0.5.tar.bz2")
tar.extractall()
tar.close()
#except:
#	print "FEEEEHLER!!!!"
#print "[INFO] Extracting Thunderbird [Windows]"
#print "[INFO] Extracting Thunderbird [Mac OS]"
#print "[INFO] Configure Extensions and Profile Folder"


# Unmounting Truecrypt
mainLogger.info("[INFO] Unmounting Truecrypt Container")
mainLogger.debug('UNMOUNT COMMAND: ' + parser.get('truecrypting', 'unmount'))

subprocess.check_call(shlex.split(parser.get('truecrypting', 'unmount')))

# Unmounting USB-Stick
#mainLogger.info("[INFO] Unmounting USB-Stick")

#try:
#    subprocess.check_call(["umount", mountpoint])
#except:
    
#    if (sys.platform=="darwin"):
 #       mainLogger.info("[INFO] please unmount your stick via the finder.")
 #   else:
 #       print "[Error] Unmounting", mountpoint, "failed"
        

# Removing Temporary folders
print "[INFO] Cleaning up Temporary Directories"

try:
    if args.device:
        os.removedirs(mountpoint)
    os.removedirs(tempdir)
    os.removedirs(tc_mountpoint)
except OSError:
    print "Some temporary Directories could not be removed"
