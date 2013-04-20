import os.path
import tarfile
import zipfile
import subprocess

# We could think about adding integrity checks here.

def extract_tarfile(filename, path):
    tar = tarfile.open(filename)
    tar.extractall(path)
    tar.close()

#def extract_7z(file, path):
    

def extract_zipfile(filename, path):
    zip = zipfile.ZipFile(filename)
    zip.extractall(path)
    zip.close()
