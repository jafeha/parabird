parabird
========

Python script for building an os independent [Linux, Windows and Mac OS] truecrypt encrypted usb-stick containing a portable thunderbird, enigmail, torbirdy and vidalia.

**NOTE:** The script is only partial functional, it is definitely in alpha state. Give me a litte time to figure things out because it is also some kind of a python learning script for me. If you have some hints for solving our issues or any thunderbird tweaking tips, please get in touch.

Requirements:
-------------

* USB-Stick with at least 1GB free disk space (we regret, but we have recommend FAT32 file system)
* Internet Connection
* Linux or Mac OS based Host for building the Stick
* You will need admin priviledges for building the stick because it is necessary for un/mounting the tc container

Depedencies:
------------

* Python >= Python2.7
* python-requests
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
- [x] Use Predownloaded packages using --cache
- [x] Creating a file stucture within the container
- [x] Full Logging support
- [x] Configurable using a Configparser (see config.ini)
- [x] Dependency checks
- [x] Truecrypt configuration: specify container size
- [x] Extracting all applications
- [x] Extract GPG for Mac OS
- [x] Configure Linux applications
- [x] Configure Windows applications
- [x] Configure Mac applications
- [x] GPG Setup Party
- [x] Write startup scripts for all supported Operation systems (3/3)
- [ ] Testing
- [ ] Better truecrypt configuration: dynamic volumes
- [ ] Support for torified USB-Stick creation (won't happen before first release)
- [ ] Release Party

Usage:
------

```
python ./parabird_build.py --help
[INFO::utils]: Logfile: /tmp/parabird_log.txt
usage: parabird_build.py [-h] [-v] [-c] [-d DEVICE] [-t THUNDER] [-b TORBIRDY]
                         [-e ENIGMAIL] [-a VIDALIA] [-n CONTAINER_NAME]
                         [-s CONTAINER_SIZE]

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         increase output verbosity
  -c, --cache           use a cache in ~/.parabirdy/cache
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
  -s CONTAINER_SIZE, --container_size CONTAINER_SIZE
                        Specify Container Size in Bytes
```
