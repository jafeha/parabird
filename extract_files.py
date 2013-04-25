# encoding: utf-8

from utils import *
import os.path
import tarfile
import zipfile
import subprocess
import sys
import os
import tempfile
import shlex
import shutil
import tarfile
import zipfile
import requests
import plistlib
import glob
from xml.dom import minidom
extractLogger=logging.getLogger('extract')
def extract_tarfile(progname, filename, path):
    mainLogger.info("[INFO] Extracting {}" .format(progname))
    try:
        tar = tarfile.open(filename)
        tar.extractall(path)
        tar.close()
    except:
        mainLogger.error("[ERROR] Could not extract {}. exiting " .format(progname))
        mainLogger.exception("[ERROR] Could not extract {}. exiting " .format(progname))
        sys.exit()


def extract_7z(progname, filename, path):
    extractLogger.info("[INFO] Extracting {}" .format(progname))
    try:
        subprocess.check_call(['7z', 'e', filename, '-o',+path])
    except:
        extractLogger.error("[ERROR] Could not extract {}. exiting" .format(progname))
        extractLogger.exception("[ERROR] Could not extract {}. exiting" .format(progname))
        sys.exit()


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
        sys.exit()

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
        sys.exit()      
