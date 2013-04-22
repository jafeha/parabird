parabird
========

Python script for building an os independent [Linux, Windows and Mac OS] truecrypt encrypted usb-stick containing a portable thunderbird, enigmail, torbirdy and vidalia.

**NOTE:** The script is not yet functional, it's pre-pre-alpha. Give me a litte time to figure things out because it is also some kind of a python learning script for me.

Requirements:
-------------

* USB-Stick with a maximum of 4GB space (limit for FAT32 formatted sticks). The programs won't take that much space and there should be enough space left for mails. we don't force users to use an NTFS formatted USB-Stick, so you won't be able to use a container bigger than 4GB on a FAT32 formatted USB-Stick
* Internet Connection
* Linux or Mac OS based Host for building the Stick
* Depending on your Host it's very likly that you need adminstrator priviledges for un/mounting the tc container

Depedencies:
------------

* Python >= Python2.7
* You should have Truecrypt installed, it doesen't matter if it gui or console based, both versions should work.
* Mozilla uses 7z to pack Thunderbird for Windows, you'll need it for extracting. 
* Unfortunately we need the package dmg2img to deal with compressed dmg files

Depedency checks are done automatically. The Script should exit if any Dependency won't match.

Implementation:
---------------
So far we  haven't reached a fully working state yet, but this is the functionality working so far:

- [x] Detecting mounting and unmounting an USB-Stick  
- [x] Creating a Truecrypt container on the USB-Stick
- [x] Downloading all necessary applications
- [x] Creating a file stucture within the container
- [x] Full Logging support
- [x] Configurable using a Configparser (see config.ini)
- [x] Dependency checks
- [ ] Extracting all applications to the
- [ ] Configuring all applications
- [ ] Writing startup scripts for all supported Operation systems
- [ ] Better truecrypt configuration: specify container size and dynamic volumes
- [ ] Support for torified USB-Stick creation (won't happen before first release)
- [ ] Release Party

Usage:
------

```
python parabird_build.py --help

usage: parabird_build.py [-h] [-v] [-d DEVICE] [-t THUNDER] [-b TORBIRDY]
                         [-e ENIGMAIL] [-a VIDALIA] [-n CONTAINER_NAME]

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         increase output verbosity
  -d DEVICE, --device DEVICE
                        Device Flag to specify USB Stick
  -t THUNDER, --thunder THUNDER
                        Specify Thunderbird version to download
  -b TORBIRDY, --torbirdy TORBIRDY
                        Specify Torbirdy Version
  -e ENIGMAIL, --enigmail ENIGMAIL
                        Specify Enigmail Version
  -a VIDALIA, --vidalia VIDALIA
                        Specify Vidalia Version
  -n CONTAINER_NAME, --container_name CONTAINER_NAME
                        Specify Container Name
```
