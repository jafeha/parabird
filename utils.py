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
import logging
import extract_files
import re
import requests
import plistlib
import glob
from xml.dom import minidom

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
    
def detect_stick():
    '''
    detects if a stick is plugged in, returns a dict with infos about the stick. see 
    mountparse for a description of the dict
    '''    
    #read from mount for the first time
    output_first,error_first = subprocess.Popen("mount",stdout = subprocess.PIPE,
        stderr= subprocess.PIPE).communicate()


    print "Pleaze insert stick, and wait thill is it mountet, then press ENTER"
    raw_input()

    #read from mount for the second time
    output_second,error_second = subprocess.Popen("mount",stdout = subprocess.PIPE,
        stderr= subprocess.PIPE).communicate()

    #convert it to sets
    output_first_set = set(output_first.split("\n"))
    output_second_set = set(output_second.split("\n"))

    #iterate through the items, which are not in both sets (e.g. new lines)

    for i in output_first_set.symmetric_difference(output_second_set):
        mp = mountparse(i)
        if (mp):
            return mp
        else:
            return None




#from http://docs.python.org/2/howto/logging-cookbook.html explainations there

#tempdir = tempfile.mkdtemp()

tempdir = os.path.realpath(tempfile.mkdtemp())
tc_mountpoint = os.path.realpath(tempfile.mkdtemp())

logfile = os.path.realpath(tempdir+"/"+"parabirdy_log.txt")

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename=tempdir+"/"+"parabirdy_log.txt",
                    filemode='w')
                    
console = logging.StreamHandler()
console.setLevel(logging.INFO)
#formatter = logging.Formatter('%(name)-6s: %(levelname)-6s %(message)s')
formatter = logging.Formatter('[%(levelname)s::%(name)s]: %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)
mainLogger = logging.getLogger('main')



mainLogger.info('Logfile: ' + logfile)

# This function tests dependencies. All stdout is send to devnull
def dependency_check(checked_app):
    try:
        FNULL = open(os.devnull, 'w')
        subprocess.check_call(checked_app, stdout=FNULL)

    except OSError:
        mainLogger.error("Missing Depedencies: {} not installed, exiting...".format(checked_app))
        mainLogger.exception("Missing Depedencies: {} not installed, exiting...".format(checked_app))
        sys.exit()

# This function checks if there is any parameter given, 
# If there is a parameter given, it updates the config 
# if not it uses default values from config.ini
def update_config(section, key, value_from_argparser):
    if value_from_argparser:
        mainLogger.info('Parameter given, device or container is: ' + value_from_argparser)
        parser.set(section, key, value_from_argparser)

    if value_from_argparser == None:
        mainLogger.info("Taking {} {} from Config: {}" .format(section, key, parser.get(section, key) ))

# This function tries to downloads all the programs we 
# want to install. 
def download_application(progname, url, filename):
    mainLogger.info("[INFO] Downloading {}" .format(progname))

    try:
        for r in range(3):
            down = requests.get(url)
            with open(tempdir+"/"+filename, "wb") as code:
                code.write(down.content)
            if down.status_code == 200:
                break
        else:
            mainLogger.error("[ERROR] Could not download {}. exiting " .format(progname))
            exit()

    except IOError:
        mainLogger.error("[ERROR] Could not download {}" .format(progname))
        mainLogger.exception("[ERROR] Could not download {}" .format(progname))
        raise
        sys.exit()
        return None


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
parser.add_argument("-s", "--container_size", help="Specify Container Size in Bytes")

args = parser.parse_args()

# Importing Config File: config.ini
from ConfigParser import SafeConfigParser
parser = SafeConfigParser()
with codecs.open('config.ini', 'r', encoding='utf-8') as f:
    parser.readfp(f)


def extract_tarfile(progname, filename, path):
    mainLogger.info("[INFO] Extracting {}" .format(progname))
    try:
        tar = tarfile.open(filename)
        tar.extractall(path)
        tar.close()
    except:
        mainLogger.error("[ERROR] Could not extract {}. exiting " .format(progname))
        mainLogger.exception("[ERROR] Could not extract {}. exiting " .format(progname))
        exit()


def extract_7z(progname, filename, path):
    mainLogger.info("[INFO] Extracting {}" .format(progname))
    try:
        subprocess.check_call(['7z', 'e', filename, '-o',+path])
    except:
        mainLogger.error("[ERROR] Could not extract {}. exiting" .format(progname))
        mainLogger.exception("[ERROR] Could not extract {}. exiting" .format(progname))
        exit()


def extract_zipfile(progname, filename, path):
    mainLogger.info("[INFO] Extracting {}" .format(progname))
    try:
        zip = zipfile.ZipFile(filename)
        zip.extractall(path)
        zip.close()
    except:
        mainLogger.error("Could not extract {}. exiting " .format(progname))
        logging.exception("extract_zipfile did not work:")
        raise
        exit()

def extract_dmg_mac(progname, filename, path):
    '''
    extracts files from a dmg on mac:
    mounts the image via hdiutil, copies the stuff to the specified path

    parameters:
    progname is the name of the program, only used for messages
    filename is the name of the dmg to "extract"
    path is the path, where all files are copied

    returns the path
    '''
    mainLogger.info("Extracting {} with extract_dmg_mac".format(progname))
    try:   
        outplist = subprocess.Popen(['hdiutil', 'attach', '-plist', filename], stdout=subprocess.PIPE).communicate()[0]
        pldict = plistlib.readPlistFromString(outplist)
        for se in pldict['system-entities']:
            if se.get('mount-point'):
                dmg_mountpoint =  se.get('mount-point')+"/"
                mainLogger.info("Mac Extract: DMG Mountpoint is {}".format(dmg_mountpoint))
                break
        else:
            dmg_mountpoint = None
            mainLogger.error('Mac Extract: Mac mountpoint could not be figured out.')
            return False

        for i in glob.glob(dmg_mountpoint+"/*.app"):
            shutil.copytree(i, os.path.join(path, os.path.basename(i)))
            mainLogger.info('Mac Extract: Copying from {} to {}'.format
                (i, os.path.join(path, os.path.basename(i))))
        
        try:
            mainLogger.info('Mac Extract: Copying for {} done'.format(progname))
            return i
        except NameError:
            #aka no i
            return False

    except OSError:
        mainLogger.error("Mac Extract: hdiutil not installed. quitting")
        mainLogger.exception("Mac Extract: hdiutil not installed. quitting")
        raise
        sys.exit()
        







def extract_dmg(progname, dmg, path):
    mainLogger.info("[INFO] Extracting {}" .format(progname))
    try:
        mainLogger.debug("Linux DMG Extract: img2dmg: {} {} {}".format("dmg2img", dmg, dmg+".img"))
        subprocess.check_call(["dmg2img", dmg, dmg+".img"])
        mainLogger.debug(
            "Linux DMG Extract: mounting: {} {} {} {} {} {} {}".format(
            'mount', '-t', 'hfsplus', '-o', 'loop', dmg+".img",
            tempdir+"/dmg/"))
        subprocess.check_call(['mount', '-t', 'hfsplus', '-o', 'loop', dmg+".img", tempdir+"/dmg/"])

        # This line fails for unknown reasons: 
        # shutil.Error: [('/tmp/tmp5grVcT/dmg/ ', u'/tmp/tmpu5_8ts/apps/mac/thunderbird/ ', "[Errno 2] No such file or directory: '/tmp/tmp5grVcT/dmg/ '")]
        # We have to fix this somehow. I'm quite sure this comes from the space in the filename, but i have no idea where that comes from. As long as we can't copy the tree, we can't put tb for mac os on the stick.

        sutil.copytree(tempdir+"/dmg", path)
        shutil.rmtree(tempdir+"/dmg/")

    except:
        mainLogger.error("[ERROR] Could not extract {}. exiting " .format(progname))
        mainLogger.exception("[ERROR] Could not extract {}. exiting " .format(progname))
        exit()      


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
        mainLogger.debug("ID for {} is {}".format(rdffile, extension_id))
        return extension_id
    except IOError:
        mainLogger.error("Could not access file {}".format(rdffile))
        mainLogger.exception("Could not access file {}".format(rdffile))
        return None
    except IndexError:
        mainLogger.error("Not a valid install.rdf File: {}".format(rdffile))
        mainLogger.exception("Not a valid install.rdf File: {}".format(rdffile))
        return None
