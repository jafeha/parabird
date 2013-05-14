#!/usr/bin/env python
# encoding: utf-8

import subprocess
import sys
import os
import tempfile
import shlex
import shutil
import argparse
import glob
import statvfs

from utils import ParaLogger, detect_stick, dependency_check, download_application, get_extension_id, copy_from_cache, configtransport, suite, update_config
from extract_files import extract_tarfile, extract_7z, extract_zipfile, extract_dmg_mac, extract_dmg

try:

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

    # Parsing Arguments given as Parameter from Shell
    clparser = argparse.ArgumentParser()
    clparser = argparse.ArgumentParser(description='')
    clparser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    clparser.add_argument("-c", "--cache", help="use a cache in ~/.parabirdy/cache", action="store_true")
    clparser.add_argument("-d", "--device", help="Device Flag to specify USB Stick")
    clparser.add_argument("-t", "--thunder", help="Specify Thunderbird version to download")
    clparser.add_argument("-a", "--vidalia", help="Specify Vidalia Version")
    clparser.add_argument("-n", "--container_name", help="Specify Container Name")
    clparser.add_argument("-s", "--container_size", help="Specify Container Size in Bytes")

    args = clparser.parse_args()

    #
    # Upgrading the Config
    #

    if (sys.platform == "darwin"):
        parser.set('truecrypting', 'tc_binary', parser.get('truecrypting', 'tc_mac_binary'))
        extract_dmg = extract_dmg_mac
    elif (sys.platform == "win32"):
        mainLogger.error("parabirdy does'nt run on windows. by us a windows license (and some gifts) or reboot in linux. virtualisation might also work")
        sys.exit()

    # Removed, because there is no verbosity support, could be reimplemented later.
    # see the logging module for built in verbosity support
    #if args.verbose:
    #   mainLogger.info("verbosity turned on")

    print "=" * 60, "\nChecking Dependencies and Configure\n", "=" * 60

    print "Tempdir is:", tempdir

    mainLogger.info("Checking all Dependencies...")

    mainLogger.debug("truerypt binary is {}".format(parser.get('truecrypting', 'tc_binary')))
    dependency_check([parser.get('truecrypting', 'tc_binary'), "--text", "--version"])
    dependency_check("7z")
    if (sys.platform == "darwin"):
        dependency_check(["hdiutil", "info"])
    else:
        dependency_check("dmg2img")

    mainLogger.info("Configuring...")

    #
    # Setting Parameters given from argparse
    #

    update_config("DEFAULT", "device", args.device)
    update_config("thunderbird_linux", "version", args.thunder)
    update_config("thunderbird_windows", "version", args.thunder)
    update_config("thunderbird_mac", "version", args.thunder)
    update_config("vidalia_linux", "version", args.vidalia)
    update_config("vidalia_windows", "version", args.vidalia)
    update_config("vidalia_mac", "version", args.vidalia)
    update_config("DEFAULT", "container_name", args.container_name)
    update_config("truecrypting", "size", args.container_size)

    print "=" * 60, "\nMounting and Truecrypting\n", "=" * 60

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
            mainLogger.info('Mounting USB Stick to' + mountpoint)

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
    mainLogger.info("Creating Container " + parser.get('DEFAULT', 'container_name') + " on USB-Stick: " + parser.get('DEFAULT', 'device'))
    mainLogger.info("NOTE: this could take a while, depending on how fast your USB-Stick and your PC is. So please be patient, stay calm and drink a cup of coffee after you entered your password twice if you know you're not running 21st century hardware...")

    #
    # Exit if the container already exists
    #

    if os.path.exists(parser.get('DEFAULT', 'container_path')):
        mainLogger.info("The Container given (" + parser.get('DEFAULT', 'container_path')+") already exists. Exiting...")
        exit()

    #
    # Exit if there is not enough free diskspace
    #

    s = os.statvfs(mountpoint)
    totalSize = (s.f_bavail * s.f_frsize)
    if totalSize < int(parser.get('truecrypting', 'size')):
        mainLogger.info("Insufficient Diskpace on your Device: {}".format(parser.get('DEFAULT', 'device')))
        exit()

    #
    # Create Container
    #
    mainLogger.debug('Truecrypting create: ' + parser.get('truecrypting', 'create'))
    subprocess.check_call(shlex.split(parser.get('truecrypting', 'create')))

    #
    # Mount Container
    #

    mainLogger.info("Mounting Truecrypt Container")
    subprocess.check_call(shlex.split(parser.get('truecrypting', 'mount')))

    print "=" * 60, "\nCreating Folders, Downloading and Extracting \n", "=" * 60

    #
    # Create Folders
    #

    mainLogger.info("Creating Folders in Truecrypt Container")

    try:
        for prog in suite("all"):
            if not os.path.exists(parser.get(prog, 'path')):
                os.makedirs(parser.get(prog, 'path'))
            if not os.path.exists(tc_mountpoint+"/data/profile"):
                os.makedirs(tc_mountpoint+"/data/profile")
            if not os.path.exists(tc_mountpoint+"/data/gpg"):
                os.makedirs(tc_mountpoint+"/data/gpg")

    except OSError:
        mainLogger.error("[ERROR] Folder already exists")
        mainLogger.exception("[ERROR] Folder already exists")

    #
    # Download Applications
    #

    mainLogger.info('Downloading / Copying Applications to: ' + tempdir)

    if (args.cache):
        download_application = copy_from_cache
    for progname in suite("all"):
        mainLogger.debug("Getting {}".format(progname))
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

    mainLogger.info('Extracting Applications')

    extract_tarfile("Thunderbird [Linux]", tempdir+"/"+parser.get('thunderbird_linux', 'file'), parser.get('thunderbird_linux', 'path'))
    parser.set('torbirdy', 'path', os.path.join(parser.get('thunderbird_linux', 'path'), 'thunderbird/distribution/extensions/torbirdy'))
    extract_zipfile("Torbirdy", tempdir+"/"+parser.get('torbirdy', 'file'), parser.get('torbirdy', 'path'))
    os.rename(parser.get('torbirdy', 'path'), os.path.join(parser.get('thunderbird_linux', 'path'), 'thunderbird/distribution/extensions/', get_extension_id(os.path.join(parser.get('torbirdy', 'path'), 'install.rdf'))))

    parser.set('enigmail', 'path', os.path.join(parser.get('thunderbird_linux', 'path'), 'thunderbird/distribution/extensions/enigmail'))
    extract_zipfile("Enigmail", tempdir+"/"+parser.get('enigmail', 'file'), parser.get('enigmail', 'path'))
    os.rename(parser.get('enigmail', 'path'), os.path.join(parser.get('thunderbird_linux', 'path'), 'thunderbird/distribution/extensions/', get_extension_id(os.path.join(parser.get('enigmail', 'path'), 'install.rdf'))))

    extract_zipfile("GPG 4 USB [Linux]", tempdir+"/"+parser.get('gpg4usb', 'file'), parser.get('gpg4usb', 'path'))
    extract_tarfile("Vidalia [Linux]", tempdir+"/"+parser.get('vidalia_linux', 'file'), parser.get('vidalia_linux', 'path'))

    # Extract Mac Applications

    extract_dmg("Thunderbird [Mac OS]", os.path.join(tempdir, parser.get('thunderbird_mac', 'file')), parser.get('thunderbird_mac', 'path'))

    parser.set('torbirdy', 'path', os.path.join(parser.get('thunderbird_mac', 'path'), 'Thunderbird.app/Contents/MacOS/distribution/extensions/torbirdy'))
    extract_zipfile("Torbirdy", tempdir+"/"+parser.get('torbirdy', 'file'), parser.get('torbirdy', 'path'))
    os.rename(parser.get('torbirdy', 'path'), os.path.join(parser.get('thunderbird_mac', 'path'), 'Thunderbird.app/Contents/MacOS/distribution/extensions/', get_extension_id(os.path.join(parser.get('torbirdy', 'path'), 'install.rdf'))))

    parser.set('enigmail', 'path', os.path.join(parser.get('thunderbird_mac', 'path'), 'Thunderbird.app/Contents/MacOS/distribution/extensions/enigmail'))
    extract_zipfile("Enigmail", tempdir+"/"+parser.get('enigmail', 'file'), parser.get('enigmail', 'path'))
    os.rename(parser.get('enigmail', 'path'), os.path.join(parser.get('thunderbird_mac', 'path'), 'Thunderbird.app/Contents/MacOS/distribution/extensions/', get_extension_id(os.path.join(parser.get('enigmail', 'path'), 'install.rdf'))))

    #extract_dmg("GPG Tools [Mac OS]", os.path.join(tempdir, parser.get('gpg4mac', 'file')), parser.get('gpg4mac', 'path'))
    extract_zipfile("Vidalia [Mac OS]", tempdir+"/"+parser.get('vidalia_mac', 'file'), parser.get('vidalia_mac', 'path'))

    # Extract Windows Applications

    extract_7z("Thunderbird [Windows]", tempdir+"/"+parser.get('thunderbird_windows', 'file'), parser.get('thunderbird_windows', 'path'))

    parser.set('torbirdy', 'path', os.path.join(parser.get('thunderbird_windows', 'path'), 'core/distribution/extensions/torbirdy'))
    extract_zipfile("Torbirdy", tempdir+"/"+parser.get('torbirdy', 'file'), parser.get('torbirdy', 'path'))
    ID = get_extension_id(os.path.join(parser.get('torbirdy', 'path'), 'install.rdf'))
    shutil.copy2(os.path.join(tempdir+"/"+parser.get('torbirdy', 'file')), os.path.join(parser.get('thunderbird_windows', 'path'), 'core/distribution/extensions/', ID+'.xpi'))

    parser.set('enigmail', 'path', os.path.join(parser.get('thunderbird_windows', 'path'), 'core/distribution/extensions/enigmail'))
    extract_zipfile("Enigmail", tempdir+"/"+parser.get('enigmail', 'file'), parser.get('enigmail', 'path'))
    ID = get_extension_id(os.path.join(parser.get('enigmail', 'path'), 'install.rdf'))
    shutil.copy2(os.path.join(tempdir+"/"+parser.get('enigmail', 'file')), os.path.join(parser.get('thunderbird_windows', 'path'), 'core/distribution/extensions/', ID+'.xpi'))

    extract_zipfile("GPG 4 USB [Windows]", tempdir+"/"+parser.get('gpg4usb', 'file'), parser.get('gpg4usb', 'path'))
    extract_7z("Vidalia [Windows]", tempdir+"/"+parser.get('vidalia_windows', 'file'), parser.get('vidalia_windows', 'path'))

    #
    # Copy Starter
    #

    mainLogger.info('Copying all Starters to: ' + tc_mountpoint)
    for i in glob.glob('starter/*'):
        shutil.copy2(i, tc_mountpoint)

    mainLogger.info('Copying Thunderbird configs to: ' + tc_mountpoint+"/conf/")
    os.makedirs(tc_mountpoint+"/conf")
    for i in glob.glob('prefs/*'):
        shutil.copy2(i, tc_mountpoint+"/conf/")

    print "=" * 60, "\nTidying up... \n", "=" * 60

    #
    # Unmounting Truecrypt
    #

    try:
        if os.path.exists(tc_mountpoint) and os.path.ismount(tc_mountpoint):
            mainLogger.info("Unmounting Truecrypt Container")
        mainLogger.debug('UNMOUNT COMMAND: ' + parser.get('truecrypting', 'unmount'))
        subprocess.check_call(shlex.split(parser.get('truecrypting', 'unmount')))

    except OSError:
        mainLogger.error("Could not unmount tc container on {}").format(tc_mountpoint)
        mainLogger.exception("Could not unmount tc container on {}").format(tc_mountpoint)
    #
    # Unmounting USB-Stick
    #

    try:
        if args.device and os.path.exists(mountpoint) and os.path.ismount(mountpoint) is True:
            mainLogger.info("Unmounting USB-Stick")
            if (sys.platform == "darwin"):
                subprocess.check_call(['diskutil', 'eject', mountpoint])
            else:
                subprocess.check_call(["umount", mountpoint])
    except OSError:
        mainLogger.error("Could not umount {}").format(mountpoint)
        mainLogger.exception("Could not umount {}").format(mountpoint)

    #
    # Removing Temporary Directories
    #

    mainLogger.info("Cleaning up Temporary Directories")

    try:
        if args.device and os.path.exists(mountpoint) and os.path.ismount(mountpoint) is False:
            shutil.rmtree(mountpoint)
        if os.path.exists(tc_mountpoint) and os.path.ismount(tc_mountpoint) is False:
            shutil.rmtree(tc_mountpoint)
        if (sys.platform == "darwin") and os.path.exists(tempdir+"/dmg") and os.path.ismount(tempdir+"/dmg") is True:
            subprocess.check_call(['diskutil', 'eject', os.path.join(tempdir+"/dmg")])
        elif os.path.exists(tempdir+"/dmg") and os.path.ismount(tempdir+"/dmg") is True:
            subprocess.check_call(['umount', os.path.join(tempdir+"/dmg/")])
        if os.path.exists(tempdir):
            shutil.rmtree(tempdir)
    except OSError:
        mainLogger.error("Some temporary Directories could not be removed")
        mainLogger.exception("Some temporary Directories could not be removed")

    print "=" * 60, "\nThe Container {} was sucessfully created." .format(mountpoint+"/container.tc")
    print "You can mount it using truecrypt."
    print "=" * 60

except KeyboardInterrupt:
    mainLogger.error("You've hit Strg+C for interrupting Parabird. Now clean up your own mess. Exiting...")
    sys.exit()
