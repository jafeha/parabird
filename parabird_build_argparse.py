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


def dependency_check(checked_app):

	try:
		FNULL = open(os.devnull, 'w')
		subprocess.check_call(checked_app, stdout=FNULL)

	except OSError:
		print "[ERROR] Missing Depedencies:", checked_app, "not installed, exiting..."
		from sys import exit
		exit()

def update_config(section, key, value_from_argparser):
        
	if value_from_argparser:
		print "[INFO] Parameter given, device or container is:", value_from_argparser
		parser.set(section, key, value_from_argparser)

	if value_from_argparser == None:
		print "[INFO] Setting", section, key, "to Parameter from Config File:", parser.get(section, key)


def download_application(progname, url):
	print "[INFO] Downloading", progname
	
	try:
		returnobject = urllib.urlretrieve(url, filename="/tmp/"+progname)
		print tempdir
		returnobject = urllib.urlretrieve(url, filename="/tmp/"+progname)
	except:
		print "[ERROR] Could not download", progname
		return None

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

from ConfigParser import SafeConfigParser

parser = SafeConfigParser()
with codecs.open('config.ini', 'r', encoding='utf-8') as f:
    parser.readfp(f)

# Removed, because there is no verbosity support, could be reimplemented later.
#if args.verbose:
#   print "verbosity turned on"

print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
print "Checking Dependencies and Configure"
print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"

print "[INFO] Checking all Dependencies..."

try:
	dependency_check(["truecrypt", "--text", "--version"])
	dependency_check("7z")
except: 
	print "[ERROR] Dependency Checks failed large scale, exiting..."
	from sys import exit
	exit()

print "[INFO] Configuring..."

# Setting Parameters given from argparse

try:
	update_config("DEFAULT", "device", args.device)
#	update_config("thunderbird", "version", args.thunder)
#	update_config("torbirdy", "version", args.torbirdy)
#	update_config("enigmail", "version", args.enigmail)
#	update_config("vidalia", "version", args.vidalia)
	update_config("DEFAULT", "container_name", args.container_name)

except NameError: 
	print "[ERROR] Hier ist was ganz arg schiefgelaufen"

# Setting Path Parameters given by tempfile

mountpoint = tempfile.mkdtemp()
tempdir = tempfile.mkdtemp()
tc_mountpoint = tempfile.mkdtemp()

parser.set('truecrypting', 'container_path', mountpoint+"/"+parser.get('DEFAULT', 'container_name'))
parser.set('truecrypting', 'tc_mountpoint', tc_mountpoint)

print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
print "Mounting and Truecrypting"
print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"

print "[INFO] Mounting USB Stick to", mountpoint

try:
	subprocess.check_call(["mount", parser.get('DEFAULT', 'device'), mountpoint])
except:
	print "[ERROR] Mounting", parser.get('DEFAULT', 'device'), "to", mountpoint, "failed"

print "[INFO] Creating Truecrypt Container on USB-Stick"

print "[INFO] Creating", parser.get('truecrypting', 'container_path')

subprocess.check_call(shlex.split(parser.get('truecrypting', 'create')))

print "[INFO] Mounting Truecrypt Container"

subprocess.check_call(shlex.split(parser.get('truecrypting', 'mount')))


#print "[INFO] Creating Folders in Truecrypt Container"

#print "[INFO] Starting to download Applications to:", tempdir

#download_application("Thunderbird [Linux]", parser.get('thunderbird', 'linux_url'))
#download_application("Thunderbird [Windows]", parser.get('thunderbird', 'windows_url'))
#download_application("Thunderbird [Mac OS]", parser.get('thunderbird', 'mac_url'))
#download_application("Torbirdy", parser.get('torbirdy', 'url'))
#download_application("Enigmail", parser.get('enigmail', 'url'))
#download_application("Vidalia [Linux]", parser.get('vidalia', 'linux_url'))
#download_application("Vidalia [Windows]", parser.get('vidalia', 'windows_url'))
#download_application("Vidalia [Mac OS]", parser.get('vidalia', 'mac_url'))

#print "[INFO] Extracting Thunderbird [Linux]"
#print "[INFO] Extracting Thunderbird [Windows]"
#print "[INFO] Extracting Thunderbird [Mac OS]"
#print "[INFO] Configure Extensions and Profile Folder"

print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
print "Unmounting Truecrypt and Stick"
print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"

print "[INFO] Unmounting Truecrypt Container"

subprocess.check_call(shlex.split(parser.get('truecrypting', 'unmount')))

print "[INFO] Unmounting USB-Stick"

try:
        subprocess.check_call(["umount", mountpoint])
except:
        print "[Error] Unmounting", mountpoint, "failed"


#print "[INFO] Cleaning up Temporary Directories"

# Removed for debugging purposes, should be reenabled in release:
#os.removedirs(mountpoint)
#os.removedirs(tempdir)
#os.removedirs(tc_mountpoint)
