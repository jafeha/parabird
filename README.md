parabird
========

Simple script written in python to build an os independent truecrypt encrypted usb-stick containing a portable thunderbird, enigmail, torbirdy and vidalia.

NOTE: The script is not yet functional, it's pre-pre-pre-alpha. Give me a litte time to figure things out because it is also a python learning script for me.

Requirements:

* USB-Stick with at least 4GB free space
* Internet Connection
* Linux based Host
* Depending on your Host you might need adminstrator priviledges for un/mounting the tc container
There are some Depedencies:

* Python >= Python2.7
* You should have Truecrypt installed, it doesen't matter if it gui or console based, both versions should work.
* Mozilla uses 7z to pack Thunderbird for Windows, you'll need it for extracting. 

Depedency checks are done automatically. The Script should exit if any Dependency won't match.

Usage:
======
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

