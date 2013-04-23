import os.path
import tarfile
import zipfile
import subprocess

# We could think about adding integrity checks here.

def extract_tarfile(progname, filename, path):
    mainLogger.info("[INFO] Extracting %s" %(progname))
    try:
        tar = tarfile.open(filename)
        tar.extractall(path)
        tar.close()
    except:
        mainLogger.error("[ERROR] Could not extract %s. exiting " %(progname))
        exit()


#def extract_7z(file, path):
    

def extract_zipfile(progname, filename, path):
    mainLogger.info("[INFO] Extracting %s" %(progname))
    try:
        zip = zipfile.ZipFile(filename)
        zip.extractall(path)
        zip.close()
    except:
        mainLogger.error("[ERROR] Could not extract %s. exiting " %(progname))
        exit()

# def extract_dmg
