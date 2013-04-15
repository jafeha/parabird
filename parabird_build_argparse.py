#!/usr/bin/env python
# encoding: utf-8 
import argparse
import ConfigParser
import codecs
import urllib
import subprocess
import sys
import os

parser = argparse.ArgumentParser()
parser = argparse.ArgumentParser(description='')
parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
parser.add_argument("-d", "--device", help="Device Flag to specify USB Stick")
parser.add_argument("-t", "--thunder", help="Specify Thunderbird version to download")
parser.add_argument("-b", "--torbirdy", help="Specify Torbirdy Version")
parser.add_argument("-e", "--enigmail", help="Specify Enigmail Version") 
parser.add_argument("-a", "--vidalia", help="Specify Vidalia Version")

args = parser.parse_args()

if args.verbose:
   print "verbosity turned on"

if args.device:
   print "Device is:", args.device

from ConfigParser import SafeConfigParser

parser = SafeConfigParser()
with codecs.open('config.ini', 'r', encoding='utf-8') as f:
    parser.readfp(f)


print "[INFO] Checking all Dependencies..."
FNULL = open(os.devnull, 'w')

try:
	subprocess.check_call(["truecrypt", "--version"], stdout=FNULL)

except OSError: 
	print "[ERROR] Missing Depedencies: Truecrypt not installed"

try:
	subprocess.check_call(["7z"], stdout=FNULL)

except OSError:
	print "[ERROR] Missing Depedencies: 7zip not installed"

print "[INFO] Configuring..."

def update_config(section, key, value_from_argparser):
        
	if value_from_argparser:
		print "[INFO] Parameter given, device is:", value_from_argparser
		parser.set(section, key, value_from_argparser)

	if value_from_argparser == None:
		print "[INFO] Setting", section, key, "to Parameter from Config File:", parser.get(section, key)

try:
	update_config("DEFAULT", "device", args.device)
	update_config("thunderbird", "version", args.thunder)
	update_config("torbirdy", "version", args.torbirdy)
	update_config("enigmail", "version", args.enigmail)
	update_config("vidalia", "version", args.vidalia)

except NameError: 
	print "Hier ist was ganz arg schiefgelaufen"


print "[INFO] Creating Mountpoint"
print "[INFO] Mounting USB Stick"
print "[INFO] Creating Truecrypt Container on USB-Stick"
print "[INFO] Mounting Truecrypt Container"
print "[INFO] Creating Folders in Truecrypt Container"
print "[INFO] Downloading Thunderbird [Linux]"
	
try: 
	urllib.urlretrieve(parser.get('thunderbird', 'linux_url'), filename="/tmp/thunderbird_linux.tgz")
except:
	print "Could not Download Thunderbird for Linux"	


print "[INFO] Downloading Thunderbird [Windows]"

try:
	urllib.urlretreive(parser.get('thunderbird', 'windows_url'), filename="/tmp/thunderbird_windows.exe")
except:
	print "Could not Download Thunderbird for Windows"

print "[INFO] Downloading Thunderbird [Mac OS]"
	
try: 
	urllib.urlretreive(parser.get('thunderbird',  'mac_url'), filename="/tmp/thunderbird_mac.dmg")
except: 
	print "Could not Download Thunderbird for Mac OS"
	
print "[INFO] Extracting Thunderbird [Linux]"
print "[INFO] Extracting Thunderbird [Windows]"
print "[INFO] Extracting Thunderbird [Mac OS]"
print "[INFO] Downloading Torbirdy"

try:
	urllib.urlretreive(parser.get('torbirdy', 'url'), filename="/tmp/thunderbird_mac.zip")
except:
	print "Could not Download Torbirdy"


print "[INFO] Downloading Enigmail"

try:
	urllib.urlretreive(parser.get('enigmail',  'url'), filename="/tmp/thunderbird_mac.zip")
except:
	print "Could not Download Thunderbird for Mac OS"


print "[INFO] Configure Extensions and Profile Folder"

print "[INFO] Downloading Vidalia [Linux]"

try:
        urllib.urlretreive(parser.get('vidalia',  'linux_url'), filename="/tmp/thunderbird_mac.zip")
except:
	print "Could not Download Vidalia for Linux"


print "[INFO] Downloading Vidalia [Windows]"

try:
        urllib.urlretreive(parser.get('vidalia',  'windows_url'), filename="/tmp/thunderbird_mac.zip")
except:
        print "Could not Download Vidalia for Windows"


print "[INFO] Downloading Vidalia [Mac OS]"

try:
        urllib.urlretreive(parser.get('vidalia',  'mac_url'), filename="/tmp/thunderbird_mac.zip")
except:
        print "Could not Download Vidalia for Mac OS"


print "[INFO] Unmounting Truecrypt Container"
print "[INFO] Unmounting USB-Stick"

