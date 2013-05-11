# encoding: utf-8

import os.path
import tarfile
import zipfile
import subprocess
import sys
import os
import tempfile
import shlex
import shutil
import requests
import plistlib
import glob
from xml.dom import minidom
#from utils import *
from utils import ParaLogger


extractLogger = ParaLogger('extract')


def extract_tarfile(progname, filename, path):
    extractLogger.debug("Extracting {}" .format(progname))
    try:
        tar = tarfile.open(filename)
        tar.extractall(path)
        tar.close()
    except:
        extractLogger.error("[ERROR] Could not extract {}. exiting " .format(progname))
        extractLogger.exception("[ERROR] Could not extract {}. exiting " .format(progname))
        sys.exit()


def extract_7z(progname, filename, path):
    extractLogger.debug("Extracting {}" .format(progname))
    try:
        FNULL = open(os.devnull, 'w')
        subprocess.check_call(['7z', '-y', 'x', filename, '-o'+path], stdout=FNULL)
    except:
        extractLogger.error("[ERROR] Could not extract {}. exiting" .format(progname))
        extractLogger.exception("[ERROR] Could not extract {}. exiting" .format(progname))
        sys.exit()


def extract_zipfile(progname, filename, path):
    extractLogger.debug("Extracting {}" .format(progname))
    try:
        zip = zipfile.ZipFile(filename)
        zip.extractall(path)
        zip.close()
    except:
        extractLogger.error("Could not extract {}. exiting " .format(progname))
        extractLogger.exception("extract_zipfile did not work:")
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
    extractLogger.debug("Extracting {} with extract_dmg_mac".format(progname))
    try:
        outplist = subprocess.Popen(['hdiutil', 'attach', '-plist', filename], stdout=subprocess.PIPE).communicate()[0]
        pldict = plistlib.readPlistFromString(outplist)
        for se in pldict['system-entities']:
            if se.get('mount-point'):
                dmg_mountpoint = se.get('mount-point')+"/"
                extractLogger.debug("Mac Extract: DMG Mountpoint is {}".format(dmg_mountpoint))
                break
        else:
            dmg_mountpoint = None
            extractLogger.error('Mac Extract: Mac mountpoint could not be figured out.')
            return False

        for i in glob.glob(dmg_mountpoint+"/*.app"):
            shutil.copytree(i, os.path.join(path, os.path.basename(i)))
            extractLogger.debug('Mac Extract: Copying from {} to {}'
                               .format(i, os.path.join(path, os.path.basename(i))))
        try:
            extractLogger.debug('Mac Extract: Copying for {} done'.format(progname))
            return i
        except NameError:
            #aka no i
            return False

    except OSError:
        extractLogger.error("Mac Extract: hdiutil not installed. quitting")
        extractLogger.exception("Mac Extract: hdiutil not installed. quitting")
        raise
        sys.exit()


def extract_dmg(progname, dmgfile, path):
    extractLogger.debug("Extracting {}" .format(progname))
    tempdir = os.path.dirname(dmgfile)
    os.makedirs(tempdir+"/dmg")
    try:
        extractLogger.debug("Linux DMG Extract: img2dmg: {} {} {}".format("dmg2img", dmgfile, dmgfile+".img"))
        FNULL = open(os.devnull, 'w')
        subprocess.check_call(["dmg2img", dmgfile, dmgfile+".img"], stdout=FNULL)
        extractLogger.debug(
            "Linux DMG Extract: mounting: {} {} {} {} {} {} {}".format(
            'mount', '-t', 'hfsplus', '-o', 'loop', 'quiet', dmgfile+".img",
            "/dmg/"))

        subprocess.check_call(['mount', '-t', 'hfsplus', '-o', 'loop', os.path.join(dmgfile+".img"), os.path.join(tempdir+"/dmg/")])

        for i in glob.glob(tempdir+"/dmg/*.app"):
            subprocess.check_call(['cp', '-r', i, path])
        # syntax probs here?
        # we need extra code for mac os:
        # "diskutil eject os.path.join(tempdir+dmgfile+".img")"
        #extractLogger.debug("Unmounting {}".format(dmgfile+".img")
        if (sys.platform == "darwin"):
            subprocess.check_call(['diskutil', 'eject', os.path.join(tempdir+"/dmg/")])
        else:
            subprocess.check_call(['umount', os.path.join(tempdir+"/dmg/")])
    except:
        extractLogger.error("[ERROR] Could not extract {}. exiting " .format(progname))
        extractLogger.exception("[ERROR] Could not extract {}. exiting " .format(progname))
        sys.exit()


def mount_dmg(path_to_dmg):
    '''
    mounts the specified .dmg, returns a path to the mounted dmg.

    this will deprecate extract_dmg and extract_dmg_mac
    '''
    extractLogger.debug("Mounting {}".format(path_to_dmg))
    if (sys.platform == "darwin"):
        return mount_dmg_mac(path_to_dmg)
    elif (sys.platform == "win32"):
        extractLogger.debug("We dont support windows. fork & sent a pull request")
        return False
    else:
        return mount_dmg_linux(path_to_dmg)


def mount_dmg_mac(path_to_dmg):
    '''
    mounts a dmg under mac. dont call it directly, call it via mount_dmg

    takes a path to the dmg as argument, returns the path to the mountpoint
    '''
    try:
        outplist = subprocess.Popen(['hdiutil', 'attach', '-plist', path_to_dmg], stdout=subprocess.PIPE).communicate()[0]
        pldict = plistlib.readPlistFromString(outplist)
        for se in pldict['system-entities']:
            if se.get('mount-point'):
                dmg_mountpoint = se.get('mount-point')+"/"
                extractLogger.debug("mac mount: DMG Mountpoint is {}".format(dmg_mountpoint))
                return dmg_mountpoint
        else:
            extractLogger.error('Mac mount: Mac mountpoint could not be figured out.')
            return False

    except OSError:
        extractLogger.error("Mac Extract: hdiutil not installed. quitting")
        extractLogger.exception("Mac Extract: hdiutil not installed. quitting")
        raise
        sys.exit()


def mount_dmg_linux(path_to_dmg):
    '''
    mount a dmg under linux. dont call it directly

    you need img2dmg and access to mount and a recent kernel and stuff
    '''

    #we need them quite often so i define some variables

    tempdir = tempfile.mkdtemp()
    path_to_img = os.path.join(tempdir + ".img")
    os.makedirs(os.path.join(tempdir, "dmg"))
    dmg_mountpoint = os.path.join(tempdir, "dmg")

    try:
        extractLogger.debug("Linux DMG Extract: img2dmg: {} {} {}".format("dmg2img", path_to_dmg, path_to_img))
        subprocess.check_call(["dmg2img", path_to_dmg, path_to_img])
        extractLogger.debug(
            "Linux DMG mounting: {} {} {} {} {} {} {}".format(
            'mount', '-t', 'hfsplus', '-o', 'loop', 'quiet', path_to_img,
            dmg_mountpoint))

        subprocess.check_call(['mount', '-t', 'hfsplus', '-o', 'loop',
                              path_to_img, dmg_mountpoint])
        return dmg_mountpoint

    except:
        extractLogger.error("Could not mount {}".format(path_to_dmg))
        extractLogger.exception("Could not mount {}".format(path_to_dmg))
        return False


def extract_pkg(path_to_pkg):
    '''takes a path to a .pkg file, returns the path to the extracted
    files'''
