# encoding: utf-8


import urllib
import subprocess
import sys
import os
import tempfile
import shlex
import shutil
import tarfile
import zipfile
import logging
import re
import requests
import plistlib
import glob
import time
from xml.dom import minidom
from ConfigParser import SafeConfigParser
import codecs
import weakref

#
# Config
#

# Importing Config File: config.ini
parser = SafeConfigParser()
with codecs.open('config.ini', 'r', encoding='utf-8') as f:
    parser.readfp(f)


#
# smuggling the config in other programms
#

def configtransport():
    return weakref.proxy(parser)


class ParaLogger(object):
    #the stuff at this level only gets executed once
    logging.basicConfig(level=logging.DEBUG,
        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        datefmt='%m-%d %H:%M',
        filename="/tmp/parabirdy_log.txt",
        filemode='w')
                    
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(levelname)s::%(name)s]: %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
    def __init__(self):
        #since we use __new__, init isn't used
        pass
    def __new__(cls, loggername):
        #here is the new logger born
        #do it like this: fooLogger = ParaLogger('foo')
        return  logging.getLogger(loggername)   

utilsLogger = ParaLogger('utils')

utilsLogger.info('Logfile: ' + "/tmp/parabirdy_log.txt" )
#utilsLogger.info('TEMPDIR: '+ tempdir)



def mountparse(line_from_mount):
    '''
    give it a line from mount(not /etc/fstab!) as a string and it return a dict
    with the following keys:
        
    device(eg /dev/sdc), mountpoint /media/foo, os (linux or darwin),
    type (fstype), opts (mountoptions)
    
    from jojoo, gplv3
    '''
    ret={}

 
    device_point = r'''
    ^       # beginning of the line
    (.+)    #   some chars until there is a whitespace and a on - DEVICE
    \s      #   whitespace
    on      #   on - valid at linux and osx
    \s      #   whitespace
    (.+)\s  #   some chars until there is a whitespace and a "type" or ( - MPOINT            
    (\(.*\s| #( with a whitespace after some time (mac) OR              )
    type\s) #type with a whitespace short after(linux)
    (.*)\)           
    '''
    d_p = re.compile(device_point, re.VERBOSE)
    try:
        dm_listet = d_p.search(line_from_mount).groups()
    except AttributeError:
        #print "mountparse could not parse the line from mount"
        return None
    try:
        ret["device"], ret["mountpoint"] = dm_listet[0], dm_listet[1]
    except ValueError:
        print "could'nt decifer your mounts. is it a linux or a mac with /dev/foobar on /mountpoint ?"
    if (dm_listet[2].find("type")>=0):
        ret['os'] = 'linux'
        try:
            ret["type"], ret["opts"] = dm_listet[3].split(" (")
        except ValueError:
            print "not a linux? dont know what to do, splitting of", dm_listet[3], "failed"
    else:
        ret['os'] = 'darwin'
        temp = dm_listet[2].split(', ')
        ret['type'] = temp[0].replace('(', '')
        ret['opts'] = ", ".join(temp[1:]) + dm_listet[3]

    return ret
    
def detect_stick(user_interface='console'):
    '''
    detects if a stick is plugged in, returns a dict with infos about the stick. see 
    mountparse for a description of the dict
    '''    
    #read from mount for the first time
    output_first,error_first = subprocess.Popen("mount",stdout = subprocess.PIPE,
        stderr= subprocess.PIPE).communicate()


    utilsLogger.debug("trying to guess usb stick")
    utilsLogger.warning("Pleaze insert stick, and wait till is it mountet")
    sys.stdout.flush()
    for i in range(400):
        if user_interface == 'console':
            time.sleep(0.5)
            sys.stdout.write(".")
            sys.stdout.flush()
        else:
            pass
        #read from mount for the second time
        output_second,error_second = subprocess.Popen("mount",stdout = subprocess.PIPE,
            stderr= subprocess.PIPE).communicate()
        #convert it to sets
        output_first_set = set(output_first.split("\n"))
        output_second_set = set(output_second.split("\n"))
        if output_second_set.difference(output_first_set):
            #iterate through the items, which are not in both sets (e.g. new lines)
            for i in output_first_set.symmetric_difference(output_second_set):
                mp = mountparse(i)
                if (mp):
                    if mp['type'] != ('msdos' or 'fat' or 'vfat'):
                        utilsLogger.warning(
                        "is {} mounted on {} really a usb stick where you want to write?"
                        .format(mp['device'], mp['mountpoint']))
                    else:
                        utilsLogger.info("found new Device: {}".format(mp['mountpoint']))
                    return mp
                    break
                else:
                    return None
            break
    else:
        #else from the for loop
        utilsLogger.error("No USB stick in 200 seconds")
        return None


# This function tests dependencies. All stdout is send to devnull
def dependency_check(checked_app):
    '''
    Checks if a command is available by simply running it and looking it
    is available in the path
    '''
    try:
        FNULL = open(os.devnull, 'w')
        subprocess.check_call(checked_app, stdout=FNULL)

    except OSError:
        utilsLogger.error("Missing Depedencies: {} not installed, exiting...".format(checked_app))
        utilsLogger.exception("Missing Depedencies: {} not installed, exiting...".format(checked_app))
        sys.exit()


# This function tries to downloads all the programs we 
# want to install. 
def download_application(progname, url, filename):
    tempdir = parser.get('DEFAULT', 'tempdir')
    utilsLogger.info("[INFO] Downloading {}" .format(progname))

    try:
        for r in range(3):
            down = requests.get(url)
            utilsLogger.debug("Writing {} ".format(tempdir+"/"+filename))
            with codecs.open(tempdir+"/"+filename, "wb") as code:
                code.write(down.content)
            if down.status_code == 200:
                break
        else:
            utilsLogger.error("[ERROR] Could not download {}. exiting " .format(progname))
            exit()

    except IOError:
        utilsLogger.error("[ERROR] Could not download {}" .format(progname))
        utilsLogger.exception("[ERROR] Could not download {}" .format(progname))
        raise
        sys.exit()
        return None


def get_extension_id(rdffile):
    '''
    gets the extension id.

    parameters:
    rdffile: path to a rdffile

    returns the 
    '''
    try:
        from xml.dom import minidom
        xmldoc = minidom.parse(rdffile)
        extension_id = xmldoc.getElementsByTagName('em:id')[0].firstChild.nodeValue
        utilsLogger.debug("ID for {} is {}".format(rdffile, extension_id))
        return extension_id
    except IOError:
        utilsLogger.error("Could not access file {}".format(rdffile))
        utilsLogger.exception("Could not access file {}".format(rdffile))
        return None
    except IndexError:
        utilsLogger.error("Not a valid install.rdf File: {}".format(rdffile))
        utilsLogger.exception("Not a valid install.rdf File: {}"
                              .format(rdffile))
        return None


def suite(suitename):
    '''
    downloads all files from the specified suitename (see config)
    suite can be all, linux, mac, win
    returns True if all worked
    '''

    #we need to remove duplicates!
    suitename = list(set(parser.get('suite', suitename).split(" ")))
    for progname in suitename:
        yield progname


def copy_from_cache(progname, url, archived_file):
    '''
    copy files from ~/.parabirdy/cache/ to tempdir
    returns True on success
    TODO stub von jonas:
    expand user
    test
    '''
    #yeah, ~/.parabirdy/cache/ is hardcoded and tmpdir is from the parser...
    #yeah, you got the files 3 times: in ~/.pbdy/cache/,
    #in the tmpdir and then extracted....
    tempdir = parser.get('DEFAULT', 'tempdir')
    src = os.path.join(os.path.expanduser('~'), ".parabirdy/cache",
                       os.path.basename(archived_file))
    dst = os.path.join(tempdir, os.path.basename(archived_file))
    shutil.copy2(src, dst)
