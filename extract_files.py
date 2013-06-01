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
    try:
        extractLogger.debug("Extracting {}" .format(progname))
        try:
            tar = tarfile.open(filename)
            tar.extractall(path)
            tar.close()
        except:
            extractLogger.error("[ERROR] Could not extract {}. exiting " .format(progname))
            extractLogger.exception("[ERROR] Could not extract {}. exiting " .format(progname))
            sys.exit()
    except KeyboardInterrupt:
        extractLogger.error("You've hit Strg+C for interrupting Parabird. Now clean up your own mess. Exiting...")
        sys.exit()


def extract_zipfile(progname, filename, path):
    try:
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
    except KeyboardInterrupt:
        extractLogger.error("You've hit Strg+C for interrupting Parabird. Now clean up your own mess. Exiting...")
        sys.exit()
