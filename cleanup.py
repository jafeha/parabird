import os  
import shutil 
import shlex
import argparse

from utils import ParaLogger, configtransport
def cleanup(mountpoint, tc_mountpoint, tempdir):

    mainLogger=ParaLogger('main')
    parser = configtransport()
    clparser = argparse.ArgumentParser()
    clparser = argparse.ArgumentParser(description='')
    clparser.add_argument("-d", "--device", help="Device Flag to specify USB Stick")
    args = clparser.parse_args()

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
        if args.device and os.path.exists(mountpoint) and os.path.ismount(mountpoint) == True:
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
        if args.device and os.path.exists(mountpoint) and os.path.ismount(mountpoint) == False:
            shutil.rmtree(mountpoint)
        if os.path.exists(tc_mountpoint) and os.path.ismount(tc_mountpoint) == False:
            shutil.rmtree(tc_mountpoint)
        if (sys.platform == "darwin") and if os.path.exists(tempdir+"/dmg"):
            subprocess.check_call(['diskutil', 'eject', os.path.join(tempdir+"/dmg/")])
        else:
            subprocess.check_call(['umount', os.path.join(tempdir+"/dmg/")])
        if os.path.exists(tempdir):
            shutil.rmtree(tempdir)
    except OSError:
        mainLogger.error("Some temporary Directories could not be removed")
        mainLogger.exception("Some temporary Directories could not be removed")


