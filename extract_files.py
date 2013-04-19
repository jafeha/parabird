import os.path
import tarfile
import zipfile
import subprocess

# We could think about adding integrity checks here.

def extract_tarfile(file, path, parser):
    tar = tarfile.open(path)
    tar.extractall(destination)
    tar.close()

def extract_7z(file, path, parser):
    

def extract_zip(file, path, parser):
    zip = zipfile.ZipFile(path)
    zip.extractall(destination)
    zip.close()
