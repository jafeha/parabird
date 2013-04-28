#!/usr/bin/env python
# encoding: utf-8

import subprocess
import sys
import os
import tempfile
import shlex
import shutil
import argparse




from utils import ParaLogger, detect_stick, dependency_check, download_application, get_extension_id, copy_from_cache, configtransport, suite
from extract_files import extract_tarfile, extract_7z, extract_zipfile, extract_dmg_mac, extract_dmg


#
#getting the config
#

parser = configtransport()

#
# Creation of tempdirs.
#

tempdir = os.path.realpath(tempfile.mkdtemp())
parser.set('DEFAULT', 'tempdir', tempdir)

tc_mountpoint = os.path.realpath(tempfile.mkdtemp())
logfile = os.path.realpath(tempdir+"/"+"parabirdy_log.txt")


mainLogger = ParaLogger('main')


#
# Configuring Commandline Arguments and Config
#


#
# Commandline Arguments
#

# Parsing Arguments given as Parameter from Shell
clparser = argparse.ArgumentParser()
clparser = argparse.ArgumentParser(description='')
clparser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
clparser.add_argument("-c", "--cache", help="use a cache in ~/.parabirdy/cache", action="store_true")
clparser.add_argument("-d", "--device", help="Device Flag to specify USB Stick")
clparser.add_argument("-t", "--thunder", help="Specify Thunderbird version to download")
clparser.add_argument("-b", "--torbirdy", help="Specify Torbirdy Version")
clparser.add_argument("-e", "--enigmail", help="Specify Enigmail Version") 
clparser.add_argument("-a", "--vidalia", help="Specify Vidalia Version")
clparser.add_argument("-n", "--container_name", help="Specify Container Name")
clparser.add_argument("-s", "--container_size", help="Specify Container Size in Bytes")

args = clparser.parse_args()


#
# Upgrading the Config
#

if (sys.platform == "darwin"):
    parser.set('truecrypting','tc_binary',parser.get('truecrypting','tc_mac_binary'))
    extract_dmg = extract_dmg_mac
elif (sys.platform == "win32"):
    mainLogger.error("parabirdy does'nt run on windows. by us a windows license (and some gifts) or reboot in linux. virtualisation might also work")
    sys.exit()

# Removed, because there is no verbosity support, could be reimplemented later.
# see the logging module for built in verbosity support
#if args.verbose:
#   mainLogger.info("verbosity turned on")




print "%" * 30, "\nChecking Dependencies and Configure\n", "%" * 30

print "Tempdir is:", tempdir

mainLogger.info("Checking all Dependencies...")

try:
    mainLogger.debug("truerypt binary is {}".format(parser.get('truecrypting', 'tc_binary')))
    dependency_check([parser.get('truecrypting', 'tc_binary'), "--text", "--version"])
    dependency_check("7z")
    if (sys.platform=="darwin"):
        dependency_check(["hdiutil", "info"])
    else:
        dependency_check("dmg2img")
except: 
    mainLogger.error("Dependency Checks failed large scale, exiting...")
    mainLogger.exception("Dependency Checks failed large scale, exiting...")
    sys.exit()



mainLogger.info("[INFO] Configuring...")



def update_config(section, key, value_from_argparser):
    '''
    This function checks if there is any parameter given, 
    If there is a parameter given, it updates the config 
    if not it uses default values from config.ini
    '''
    
    if value_from_argparser:
        mainLogger.info('Parameter given, device or container is: ' + value_from_argparser)
        parser.set(section, key, value_from_argparser)

    if value_from_argparser is None:
        mainLogger.info("Taking {} {} from Config: {}"
                        .format(section, key, parser.get(section, key)))


#
# Setting Parameters given from argparse
#

try:
    update_config("DEFAULT", "device", args.device)
    #update_config("thunderbird", "version", args.thunder)
    #update_config("torbirdy", "version", args.torbirdy)
    #update_config("enigmail", "version", args.enigmail)
    #update_config("vidalia", "version", args.vidalia)
    update_config("DEFAULT", "container_name", args.container_name)
    update_config("truecrypting", "size", args.container_size)

except NameError:
    mainLogger.error("[ERROR] Hier ist was ganz arg schiefgelaufen")
    mainLogger.exception("[ERROR] Hier ist was ganz arg schiefgelaufen")

print "%" * 30, "\nMounting and Truecrypting\n", "%" * 30

#
# Use an USB-Stick given by a Parameter or a detected one:
#

if args.device:
    try:
        mountpoint = os.path.realpath(tempfile.mkdtemp())
        update_config("DEFAULT", "device", args.device)

    except NameError:
        mainLogger.error("[ERROR] Hier ist was ganz arg schiefgelaufen")
        mainLogger.exception("[ERROR] Hier ist was ganz arg schiefgelaufen")
else:
    stick = detect_stick()

    #did autodetection work? and can we write?
    #if we can write to the mountpoint of the stick, no need to re-mount it
    if stick['mountpoint'] and (not(os.access(str(stick['mountpoint']), os.W_OK))):
        #aka we cant write or stick detection did not work
        #question is: does it make sense to continue at this point?
        #which scenarios are possible (except detection not working)
        mountpoint = os.path.realpath(tempfile.mkdtemp())
        mainLogger.error("Stick detection did not work, try to run with what you specified")
        mainLogger.info('[INFO] Mounting USB Stick to' + mountpoint)

        try:
            subprocess.check_call(["mount", parser.get('DEFAULT', 'device'), mountpoint])
        except:
            mainLogger.error("Mounting {} to {} failed".format(parser.get('DEFAULT', 'device', mountpoint)))
            mainLogger.exception("Mounting {} to {} failed".format(parser.get('DEFAULT', 'device', mountpoint)))
            raise

    #ok, we can write to the stick        
    else:
        parser.set('DEFAULT', "device", stick['device'])
        mountpoint = stick['mountpoint']

#
# Setting the Path for Truecrypt
#

parser.set('DEFAULT', 'container_path', mountpoint+"/"+parser.get('DEFAULT', 'container_name'))
mainLogger.debug("Container Path is: {}".format(parser.get('DEFAULT', 'container_path')))

parser.set('DEFAULT', 'tc_mountpoint', tc_mountpoint)
mainLogger.debug("TC Mountpoint is: {}".format(parser.get('DEFAULT', 'tc_mountpoint')))


#Multiple Variables like this, because the logger only takes 1 argument:
mainLogger.info("[INFO] Creating Container " + parser.get('DEFAULT', 'container_name') + " on USB-Stick: " + parser.get('DEFAULT', 'device'))

#
# Exit if the container already exists
#

if os.path.exists(parser.get('DEFAULT', 'container_path')):
    mainLogger.info("The Container given ("+ parser.get('DEFAULT', 'container_path')+") already exists. Exiting...")
    exit()

#
# Create Container
#
mainLogger.debug('Truecrypting create: ' + parser.get('truecrypting', 'create'))
subprocess.check_call(shlex.split(parser.get('truecrypting', 'create')))

#
# Mount Container
#

mainLogger.info("[INFO] Mounting Truecrypt Container")
subprocess.check_call(shlex.split(parser.get('truecrypting', 'mount')))

#
# Create Folders
#

mainLogger.info("[INFO] Creating Folders in Truecrypt Container:")

try:
    for prog in suite("all"):
        os.makedirs(parser.get(prog, 'path'))

    # for extracting tb for mac os, we need to mount a dmg
    # i create an subfolder in tempdir for doing this
    os.makedirs(tempdir+"/dmg")

except OSError:
    mainLogger.error("[ERROR] Folder already exists")
    mainLogger.exception("[ERROR] Folder already exists")

#
# Download Applications
#


mainLogger.info('[INFO] Starting to download Applications to: ' + tempdir)

if (args.cache):
    download_application = copy_from_cache
for progname in suite("all"):
    mainLogger.info("Getting {}".format(progname))
    download_application(progname, parser.get(progname, 'url'),
                         parser.get(progname, 'file'))


#
# Extracting Applications
#
# 1. Linux
# 2. Mac
# 3. Windows
#


# Extracting Linux Applications

extract_tarfile("Thunderbird [Linux]", tempdir+"/"+parser.get('thunderbird_linux', 'file'), parser.get('thunderbird_linux', 'path'))
parser.set('torbirdy', 'path', os.path.join(parser.get('thunderbird_linux', 'path'), 'thunderbird/distribution/extensions/torbirdy'))
extract_zipfile("Torbirdy", tempdir+"/"+parser.get('torbirdy', 'file'), parser.get('torbirdy', 'path'))
print 'Extension ID is:', get_extension_id(os.path.join(parser.get('torbirdy', 'path'), 'install.rdf'))
os.rename(parser.get('torbirdy', 'path'), os.path.join(parser.get('thunderbird_linux', 'path'), 'thunderbird/distribution/extensions/', get_extension_id(os.path.join(parser.get('torbirdy', 'path'), 'install.rdf'))))


parser.set('enigmail', 'path', os.path.join(parser.get('thunderbird_linux', 'path'), 'thunderbird/distribution/extensions/enigmail'))
extract_zipfile("Enigmail", tempdir+"/"+parser.get('enigmail', 'file'), parser.get('enigmail', 'path'))
print 'Extension ID is:', get_extension_id(os.path.join(parser.get('enigmail', 'path'), 'install.rdf'))
os.rename(parser.get('enigmail', 'path'), os.path.join(parser.get('thunderbird_linux', 'path'), 'thunderbird/distribution/extensions/', get_extension_id(os.path.join(parser.get('enigmail', 'path'), 'install.rdf'))))

extract_zipfile("GPG 4 USB [Linux]", tempdir+"/"+parser.get('gpg4usb', 'file'), parser.get('gpg4usb', 'path'))
extract_tarfile("Vidalia [Linux]", tempdir+"/"+parser.get('vidalia_linux', 'file'), parser.get('vidalia_linux', 'path'))

# Extract Mac Applications

extract_dmg("Thunderbird [Mac OS]", os.path.join(tempdir, parser.get('thunderbird_mac', 'file')), parser.get('thunderbird_mac', 'path') )

parser.set('torbirdy', 'path', os.path.join(parser.get('thunderbird_mac', 'path'), 'Contents/MacOS/distribution/extensions/torbirdy'))
extract_zipfile("Torbirdy", tempdir+"/"+parser.get('torbirdy', 'file'), parser.get('torbirdy', 'path'))
print 'Extension ID is:', get_extension_id(os.path.join(parser.get('torbirdy', 'path'), 'install.rdf'))
os.rename(parser.get('torbirdy', 'path'), os.path.join(parser.get('thunderbird_mac', 'path'), 'Contents/MacOS/distribution/extensions/', get_extension_id(os.path.join(parser.get('torbirdy', 'path'), 'install.rdf'))))


parser.set('enigmail', 'path', os.path.join(parser.get('thunderbird_mac', 'path'), 'Contents/MacOS/distribution/extensions/enigmail'))
extract_zipfile("Enigmail", tempdir+"/"+parser.get('enigmail', 'file'), parser.get('enigmail', 'path'))
print 'Extension ID is:', get_extension_id(os.path.join(parser.get('enigmail', 'path'), 'install.rdf'))
os.rename(parser.get('enigmail', 'path'), os.path.join(parser.get('thunderbird_mac', 'path'), 'Contents/MacOS/distribution/extensions/', get_extension_id(os.path.join(parser.get('enigmail', 'path'), 'install.rdf'))))

#extract_dmg("GPG Tools [Mac OS]", os.path.join(tempdir, parser.get('gpg4mac', 'file')), parser.get('gpg4mac', 'path'))
extract_zipfile("Vidalia [Mac OS]", tempdir+"/"+parser.get('vidalia_mac', 'file'), parser.get('vidalia_mac', 'path'))

# Extract Windows Applications

extract_7z("Thunderbird [Windows]", tempdir+"/"+parser.get('thunderbird_windows', 'file'), parser.get('thunderbird_windows','path'))

parser.set('torbirdy', 'path', os.path.join(parser.get('thunderbird_windows', 'path'), 'core/distribution/extensions/torbirdy'))
extract_zipfile("Torbirdy", tempdir+"/"+parser.get('torbirdy', 'file'), parser.get('torbirdy', 'path'))
print 'Extension ID is:', get_extension_id(os.path.join(parser.get('torbirdy', 'path'), 'install.rdf'))
os.rename(parser.get('torbirdy', 'path'), os.path.join(parser.get('thunderbird_windows', 'path'), 'core/distribution/extensions/', get_extension_id(os.path.join(parser.get('torbirdy', 'path'), 'install.rdf'))))


parser.set('enigmail', 'path', os.path.join(parser.get('thunderbird_windows', 'path'), 'core/distribution/extensions/enigmail'))
extract_zipfile("Enigmail", tempdir+"/"+parser.get('enigmail', 'file'), parser.get('enigmail', 'path'))
print 'Extension ID is:', get_extension_id(os.path.join(parser.get('enigmail', 'path'), 'install.rdf'))
os.rename(parser.get('enigmail', 'path'), os.path.join(parser.get('thunderbird_windows', 'path'), 'core/distribution/extensions/', get_extension_id(os.path.join(parser.get('enigmail', 'path'), 'install.rdf'))))


extract_zipfile("GPG 4 USB [Windows]", tempdir+"/"+parser.get('gpg4usb', 'file'), parser.get('gpg4usb', 'path')) 
extract_7z("Vidalia [Windows]", tempdir+"/"+parser.get('vidalia_windows', 'file'), parser.get('vidalia_windows', 'path'))

#
# Unmounting Truecrypt
#

#mainLogger.info("[INFO] Unmounting Truecrypt Container")
#mainLogger.debug('UNMOUNT COMMAND: ' + parser.get('truecrypting', 'unmount'))
#subprocess.check_call(shlex.split(parser.get('truecrypting', 'unmount')))

#
# Unmounting USB-Stick
#

#mainLogger.info("[INFO] Unmounting USB-Stick")

#try:
#    if args.device:
#        subprocess.check_call(["umount", mountpoint])

#except:
    
#    if (sys.platform=="darwin"):
#       mainLogger.info("[INFO] please unmount your stick via the finder.")
#    else:
#        mainLogger.error("[Error] Unmounting", + mountpoint, + "failed")
        
#
# Removing Temporary folders
#

#mainLogger.info("[INFO] Cleaning up Temporary Directories")

#try:
#    if args.device:
#        os.removedirs(mountpoint)
#    os.removedirs(tempdir)
#    os.removedirs(tc_mountpoint)
#except OSError:
#    mainLogger.error("Some temporary Directories could not be removed")
#    mainLogger.exception("Some temporary Directories could not be removed")
