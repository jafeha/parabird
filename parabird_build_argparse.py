#!/usr/bin/env python
# encoding: utf-8 
import argparse
import ConfigParser
import codecs
import urllib
import subprocess
import sys

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

try:
	if args.device:
		print "[INFO] Parameter given, device is:", args.device
	
	if args.device == None:
		print "[INFO] Setting Device Parameter from Config File:"
		args.device = parser.get('DEFAULT', 'device')
		print "[CONFIG] Parameter is set to", args.device

	if args.thunder == None:
		print "[INFO] Setting Thunderbird Version Parameter from Config File:"
		args.thunder = parser.get('thunderbird', 'version')
		print "[CONFIG] Parameter is set to", args.thunder

	if args.torbirdy == None:
		print "[INFO] Setting Torbirdy Version Parameter from Config File:"
		args.torbirdy = parser.get('torbirdy', 'version')
		print "[CONFIG] Parameter is set to", args.torbirdy

	if args.enigmail == None:
		print "[INFO] Setting Torbirdy Version Parameter from Config File:"
		args.enigmail = parser.get('enigmail', 'version')
		print "[CONFIG] Parameter is set to", args.enigmail

	if args.vidalia == None:
		print "[INFO] Setting Vidalia Version Parameter from Config File:"
		args.vidalia = parser.get('vidalia', 'version')
		print "[CONFIG] Parameter is set to", args.vidalia

except NameError: 
#  args.device = parser.get('device')

  print "Parameter taken from Config file, device is:", parser.get('device')
  print "Hier ist was ganz arg schiefgelaufen"


print "[INFO] Creating Mountpoint"
print "[INFO] Mounting USB Stick"
print "[INFO] Creating Truecrypt Container on USB-Stick"
print "[INFO] Mounting Truecrypt Container"
print "[INFO] Creating Folders in Truecrypt Container"
print "[INFO] Downloading Thunderbird [Linux]"
print "[INFO] Downloading Thunderbird [Windows]"
print "[INFO] Downloading Thunderbird [Mac OS]"
print "[INFO] Extracting Thunderbird [Linux]"
print "[INFO] Extracting Thunderbird [Windows]"
print "[INFO] Extracting Thunderbird [Mac OS]"
print "[INFO] Downloading Torbirdy"
print "[INFO] Downloading Enigmail"
print "[INFO] Configure Extensions and Profile Folder"
print "[INFO] Unmounting Truecrypt Container"
print "[INFO] Unmounting USB-Stick"

