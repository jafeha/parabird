#!/usr/bin/env python
# encoding: utf-8 
# das wird jetzt eine version, die tc nicht herunter läd, sondern davon ausgeht, dass tc in der consolenvariante installiert ist.
# der thunderbird wird mal noch nicht heruntergeladen# die subprocess aufrufe bleiben vorerst auskommentiert und werden als  kommando geprintet lasse

import urllib # url handling, downloads
import getopt # optionen/argumente parsen
import sys    # dinge die den interpreter betreffen
import subprocess  # make system calls
import ConfigParser

from ConfigParser import SafeConfigParser
import codecs

parser = SafeConfigParser()
with codecs.open('config.ini', 'r', encoding='utf-8') as f:
    parser.readfp(f)
    
print "Übersicht über alle Configurationsoptionen"
print "#" * 20
for section_name in parser.sections():
    print 'Section:', section_name
    for name, value in parser.items(section_name):
        print " %s\t= %s" % (name, value)
    print "-" * 8

print "\n" * 2
print "url from truecrypt:\t", parser.get('truecrypt', 'url')
print "changing version to 10.0"
parser.set('truecrypt', 'version', '10.0')
print 'this updates the url:\t', parser.get('truecrypt', 'url')



# config goes here
#usb_device = "" # defaultwert
TRUECRYPT_CREATE = "truecrypt --create --volume-type=Hidden --filesystem=None --hash=RIPEMD-160 --encryption=AES" +usb_device 
#TRUECRYPT = "truecrypt --filesystem=none"+ usb_device
#truecrypt_version = "7.0a" # hier koennen wir spaeter nen argument uebergeben
#truecrypt_url = "http://www.truecrypt.org/download/truecrypt-"+ truecrypt_version +  "-linux-console-x86.tar.gz"
#MAKE_FS = "mkfs.ntfs --quick /dev/mapper/truecrypt0" # hier muss noch ein Check eingebaut werden, damit er auch das richtige device bekommt.
#UNMOUNT_USB = "truecrypt -d"+ usb_device
#MOUNTPOINT_CREATE = "mkdir /tmp/mount/" #ueberlegung: das mit dem mounten mit nem eigenen py modul machenexi
#MOUNTPOINT = "/tmp/mount/"
#TRUEMOUNT = "truecrypt "+ usb_device +" "+ MOUNTPOINT 
#thunderbird_url = "http://releases.mozilla.org/pub/mozilla.org/thunderbird/releases/17.0.5/linux-x86_64/de/thunderbird-17.0.5.tar.bz2"
#TB_DOWNFILE = "/tmp/thunderbird.tar.bz2" # da fehlte in deiner version das =


# dont edit below this line

#options, remainder = getopt.getopt(sys.argv[1:], 'o:v', ['output=', 
#						'help',
#						'verbose',
#						'truecrypt=',
#						'device=',
#						])


#for opt, arg in options:
#	if opt in ('-o', '--output'):
#		output_filename = arg
#	elif opt in ('-v', '--verbose'):
#		verbose = True
#	elif opt in ('-h', '--help'):
#		print "usage: lalala"
#	elif opt == '--truecrypt':
#		truecrypt_version = arg
#	elif opt == '--device':
#		usb_device = arg



#urllib.urlretrieve(truecrypt_url, "/tmp/tc.tgz")

#cmds_create =  [TRUECRYPT, MAKE_FS, UNMOUNT_USB] #wenn du was zuweisen willst muss da ein = hin
cmds_create =  [TRUECRYPT_CREATE] #wenn du was zuweisen willst muss da ein = hin
#cmds_mount = [MOUNTPOINT_CREATE, TRUEMOUNT] # ditto
for cmd in cmds_create:
	print "Creating encrypted USB-Stick"
	#subprocess.call(cmd_create, shell=True)
	#hier muss n check hin, ob das device existiert, bzw ob die --device option ueberhaupt gesetzt ist
	print "__COMMAND__", cmd # hier muss es cmd heiszen, nicht cmd_create. cmd_create ist die liste, cmd das element in dem man atm ist
	print "Encrypted USB-Stick created and mounted to:", MOUNTPOINT # siehe shell -> 

#for cmd in cmds_mount:
#	print "Creating Mountpoint and Mounting USB Stick"
#	try:
		#subprocess.check_call(cmd_mount, shell=True)
#		print "__COMMAND__",cmd # s.o.
#	except CalledProcessError:
#	    print cmd_mount, "did not work"
	
	#hier sollte n check mit os.listfiles oder so hin    
#	print "USB-Stick mounted..."

# Truecrypt tut, jetzt kommt Thunderbird

print "Downloading Thunderbird"
#urllib.urlretrieve(thunderbird_url, TB_DOWNFILE) # erstes rgument: url. zweites argument: ziel. + kettet stings aneinander
print "Download complete, unpacking"
#subprocess.call("tar xfj " + TB_DOWNFILE, shell=True) # um tar muessen ", das 2. + ist zu viel, leerzeichen fehlen
print "tar xfj " + TB_DOWNFILE

