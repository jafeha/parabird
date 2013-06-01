#!/usr/bin/env python
import subprocess
import fnmatch
import os
import shlex

'''
seven_zip module. handles interaction with 7zip, p7zip.
Only supports snooping in archives and unpacking

you'll need the 7zip binary in the path. get theese from here:
- http://www.7-zip.org/ (windows)
- http://p7zip.sourceforge.net/ (unix)



(c) jonas osswald 2013.
licensed as lgpl.

please consider a donation to Igor Wiktorowitsch Pawlow, paypal@7-zip.org
'''


class SevenZipError(Exception):
    """Base Exception"""
    pass


class SevenZipNotInstalledError(SevenZipError):
    '''Seven Zip is not Installed'''
    pass


class ExtractError(SevenZipError):
    """General exception for extract errors. File does not exist, is not
    readable, ..."""
    def __init__(self, *args):
        for i in args:
            print i


class ReadError(SevenZipError):
    """Exception for unreadable compression methods or corrupt
    archives"""
    pass


class FileNotInArchiveError(ReadError):
    '''The desired file is not present in the archive.'''


class BadCommandlineError(SevenZipError):
    """Bad commandline. See man 7z"""
    pass


class NotEnoughMemoryError(SevenZipError):
    '''Not Enough Memory'''
    pass


class UserStoppageError(SevenZipError):
    '''The User stopped the 7z process wirh ctrl+c or with some signal'''
    pass


class SevenZipExecutable(object):
    '''TODO: Also compress and create archives, not only extract'''

    def __init__(self):
        self.command = self.guess_seven_zip_executable()

    def guess_seven_zip_executable(self):
        '''this function quesses which executable should be used on this computer
        '''
        try:
            sz_out = subprocess.check_output('7z')
            return "7z"
        except OSError:
                try:
                    sz_out = subprocess.check_output('7za')
                    return "7za"
                except OSError:
                    try:
                        sz_out = subprocess.check_output('7z.exe')
                        return "7z.exe"

                    except OSError:
                        raise SevenZipNotInstalledError
                        print "no 7zip found."

    def run_command(self, path_to_archive='', command='', options='', path_to_extract=''):
        if path_to_extract == '':
            commandline = "{} {} '{}' {} -y".format(self.command, command,
                      path_to_archive, options)
        else:
            commandline = "{} {} '{}' -o'{}' {} -y".format(self.command, command,
                      path_to_archive, path_to_extract, options)
        try:
            #output = subprocess.check_output([self.command, command, path_to_archive, "-o" + path_to_extract, options, '-y'])
            output = subprocess.check_output(shlex.split(commandline))
            if output.find('Everything is Ok') >= 0:
                return output
            elif output.find('No files to process') >= 0:
                print "Commandline: ", commandline
                print "output", output
                raise FileNotInArchiveError

            elif output.find('Listing archive') >= 0:
                return output
            else:
                print output
                return output
            return output

        except subprocess.CalledProcessError, e:
            print "commandline: ", commandline
            if e.returncode == 7:
                print commandline
                raise BadCommandlineError
            elif e.returncode == 2:
                print commandline
                raise ExtractError(commandline)
            elif e.returncode == 8:
                raise NotEnoughMemoryError
            elif e.returncode == 255:
                raise UserStoppageError
            elif e.returncode == 1:
                #this os only a warning from 7z
                pass


class SevenZipMember(object):
    """
    .. class:: SevenZipMember

    This Class is used for so called "Members". A Member is a file in an archive
    You can create Members with ``SevenZip.getmember("name")`` or yield all members::

        >>> for i in seven_zip_object.getmembers:
        >>>    print i.path, i.method

    Or you can yield all members matching a specific name::

        >>> for i in seven_zip_object.searchmembers("*.c"):
        >>>     i.extract("~/code/")

    """
    def __init__(self, path_to_archive, file_dict):
        '''SevenZipMember foo'''
        self._file_dict = file_dict
        self.path_to_archive = path_to_archive
        try:
            #: Path to the whole Archive
            self.path_to_archive = path_to_archive

            #: Path of the Member in the File
            self.path = file_dict['Path']  # This is the Name of the member
            self.name = file_dict['Path']

            #: Size in bytes
            self.size = int(file_dict['Size'])
            self.method = file_dict['Method']
            self.mode = file_dict['Mode']
        except KeyError:
            pass
            #raise ReadError. FIXME: Debug this for dmg->pkg

    def get_info(self):
        '''return dict with info's about member. dict is taken from :py:class:`SevenZip`'''
        return self._file_dict

    def isarchive(self):
        #TODO implement some useful determination if member itselv is an archive
        pass
    def has_archive_filename(self):
        '''is the member extracktable?
        Based on a stupid guess of the filename...'''
        archive_filenames = ["*.tar", "Payload*", "*.ar", "*.7z", "*.bz", "*.gz",
        "*.cpio", "*.pkg", "*.mpkg", "*.rpm", "*.deb", "*.hfs",]

        for pattern in archive_filenames:
            if fnmatch.fnmatch(self.path, pattern):
                return True
        else:
            return False

    def __str__(self):
        stringy = "<SevenZipMember: {} :: {}>".format(self.path_to_archive, self.path)
        return stringy

    def extract(self, extractpath):
        '''
        Extract the file of the member.

        :param extractpath: Extract the files There
        :rtype: Path to extracted File as string

        '''
        executable = SevenZipExecutable()
        executable.run_command(path_to_archive=self.path_to_archive,
                               command='x', options='-ir!'+self.path,
                               path_to_extract=extractpath)

        return os.path.normpath(os.path.join(extractpath, self.path))


class SevenZip(object):
    '''SevenZip class. create a object like this::

        >>> zipfile = seven_zip.SevenZip("file.zip")
    
    then you can do fancy stuff like::

        >>> zipfile.getnames()
    
    to print all files in the archive. or extract it::

        >>> zipfile.extractall("~/")

    or more advanced: extract only jpg's bigger than 1MB to a special folder::

        >>> for member in zipfile.searchmember("*.jpg"):
        >>>    if member.size > (1024**2):
        >>>        member.extract("/tmp/bigpictures")

    '''

    members = []

    def _parse_list(self, liststring):
        d = {}
        for i in liststring.splitlines():
            try:
                key, value = i.split(' = ')
                d[key] = value
            except ValueError:
                continue
        if d:
                return d

    def __init__(self, name):
        '''open a compressed file that 7zip can read'''
        self.path = name  # dont use this
        #: Path to the archive
        self.archive_path = name  # use this
        self.executable = SevenZipExecutable()

        sz_out = self.executable.run_command(command='l', options='-slt',
                                 path_to_archive=name, path_to_extract='/tmp/')
        begin = sz_out.find("\n--\n")
        end = sz_out.find('\n\n', begin)
        archinfo = self._parse_list(sz_out[begin:end])
        try:
            #: Type of the archive, e.g. zip
            self.archive_type = archinfo['Type']
            #: Method of the Archive (e.g. )
            self.method = archinfo['Method']
            self.blocks = archinfo['Blocks']
        except KeyError:
            pass
        list_of_files = sz_out[end:].split("\n\n")
        for single_file in list_of_files:
            single_file_dict = self._parse_list(single_file)
            if single_file_dict:
                self.members.append(single_file_dict)
    def __str__(self):
        return "<SevenZip Object: {}>".format(self.path)

    def getnames(self):
        '''get the names from an archive.
        returns the names of the files in the archive.'''
        names = []
        for file_dict in self.members:
            names.append(file_dict['Path'])
        return names

    def getmembers(self):
        '''yield :py:class:`SevenZipMember` for all Files in the Archive'''
        for i in self.members:
            yield SevenZipMember(self.path, i)

    def getmember(self, path_in_archive):
        '''
        return the :py:class:`SevenZipMember` for the ``path_in_archive``.
        If there's no File like ``path_in_archive`` return False

        :param path_in_archive: The Name/Path of the new Member
        :rtype: :py:class:`SevenZipMember`

        ''' 
        for d in self.members:
            if d['Path'] == path_in_archive:
                return SevenZipMember(self.path, d)
        else:
            return False

    def searchmember(self, path_in_archive):
        '''yield all :py:class:`SevenZipMember`(s) wildcard matching to the specified path'''
        for d in self.members:
            if fnmatch.fnmatch(d['Path'], path_in_archive):
                yield SevenZipMember(self.path, d)

    def extract(self, name, path_to_extr):
        '''extract the file name to the path

:param name: The name of the File to be extractet out of the archive
:param path_to_extr: The Path where the File should be written to
:rtype: Path to extracted file as string

        '''
        output = self.executable.run_command(path_to_archive=self.path,
                                             command="x", options="-ir!"+name,
                                             path_to_extract=path_to_extr)
        return os.path.normpath(os.path.join(path_to_extr, name))

    def extract_all(self, path):
        '''extract all files to path.
        this will overwrite files, create directorys etc. **you have been warned!**
        returns the paths to the extracted files (as a list)'''
        self.executable.run_command(path_to_archive=self.archive_path,
                        command="x", options='', path_to_extract=path)
        ret = []
        for i in self.getnames():
            ret.append(os.path.normpath(os.path.join(path, i)))
        return ret

    def _extract_dmg(self, path):
        self.extract('2.hfs', path)
        sz_hfs = SevenZip(os.path.join(path, '2.hfs'))
        ret = sz_hfs.extract_all(path)
        os.remove(os.path.join(path, '2.hfs'))
        return ret

    def _extract_pkg(self, path):
        ret = []
        for i in self.searchmember("*.pkg/Payload"):
            payload_filename = i.extract(path)
            #we extracted the Payload file from the PKG.
            #This file holds a Payload~ file which we also need to extract
            plf = SevenZip(payload_filename)
            inner_plf = plf.extract("Payload~", path)
            innerPayloadFile = SevenZip(inner_plf)
            files = innerPayloadFile.extract_all(path)
            #os.remove(payload_filename)
            #os.remove(inner_plf)
            for j in files:
                ret.append(j)
        return ret

    def _extract_tar(self, path):
        pass

    def extract_smart(self, path):
        '''extracts the archive like someone would excpect'''
        if fnmatch.fnmatch(self.archive_path, "*.dmg"):
            return self._extract_dmg(path)

        elif fnmatch.fnmatch(self.archive_path, "*.pkg"):
            return self._extract_pkg(path)

        elif fnmatch.fnmatch(self.archive_path, "*.tar.*"):
            return self._extract_tar(path)
        else:
            return False

    def extract_super_smart(self, path):
        '''extracts files out of pkg's in dmg's '''
        if fnmatch.fnmatch(self.archive_path, "*.dmg"):
            #print "i'm a dmg"
            foo = self.getnames()
            for fname in foo:

                if fnmatch.fnmatch(fname, "2.hfs"):
                    #print "there is a 2.hfs"
                    ret = []
                    for file_in_dmg in self._extract_dmg(path):
                        #print "i am in the file in dmg"
                        if fnmatch.fnmatch(file_in_dmg, "*.pkg"):
                            #print file_in_dmg
                            pkgs = SevenZip(file_in_dmg)
                            files = pkgs._extract_pkg(path)
                            ret.append(files)
                    return ret
        else:
            print "super_smart is for dmg's only"
            return False
