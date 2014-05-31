Disclaimer
=========
As of the moment, the situation about truecrypts future is unsure. We we're considering a OO-rewrite of parabird last week but stopped all of those intentions until things get a bit clearer. It looks like TC isn't completely broken ([see here](https://www.grc.com/misc/truecrypt/truecrypt.htm)) but for further development someone needs to fork it. We'll take a look at parabird again when things changed a bit. 

parabird
========

Parabird is a Python script for building a os independent [Linux, Windows and Mac OS] truecrypt encrypted usb-stick containing a portable version of thunderbird, enigmail, torbirdy and vidalia and a shared profile.

#### News:
* July 5th 2013: Releasing Parabird v.0.0.1 RC 3
* July 4th 2013: Releasing Parabird v.0.0.1 RC 2
* June 1st 2013: Releasing Parabird v.0.0.1 RC 1

#### Info:

**NOTE:** The script is functional, but this is still a Release Candidate. If you find a bug, please open an issue. Thunderbird for Mac OS and especially **the GPG/Enigmail Setup for Mac OS needs testing**. Give me a litte time to figure things out because it is also some kind of a python learning script for me. If you have some hints for solving our issues or any thunderbird tweaking tips, please get in touch.
Please also notice the **Security issue** being discussed on the [Testing Page](https://github.com/jafeha/parabird/wiki/Testing) and the [Dependencies](https://github.com/jafeha/parabird/wiki/Depedencies).

#### Download / Install:
If you want to test or run parabird, you best go with the released tarball: [parabird-0.0.1-RC3.tar.gz](https://github.com/jafeha/parabird/releases/v0.0.1-RC3/1826/parabird-0.0.1-rc3.tar.gz).

#### Contributing code:
If you like to join the parabird development, you best start downloading the git repo.

```
git clone https://github.com/jafeha/parabird
cd parabird
sudo python parabird.py
```

#### Usage:

```
python ./parabird_build.py --help
[INFO::utils]: Logfile: /tmp/parabird_log.txt
usage: parabird_build.py [-h] [-v] [-c] [-d DEVICE] [-t THUNDER]
                         [-a VIDALIA] [-n CONTAINER_NAME] [-s CONTAINER_SIZE]

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         increase output verbosity
  -c, --cache           use a cache in ~/.parabirdy/cache
  -d DEVICE, --device DEVICE
                        Device Flag to specify USB Stick
  -t THUNDER, --thunder THUNDER
                        Specify Thunderbird version to download
  -a VIDALIA, --vidalia VIDALIA
                        Specify Vidalia Version
  -n CONTAINER_NAME, --container_name CONTAINER_NAME
                        Specify Container Name
  -s CONTAINER_SIZE, --container_size CONTAINER_SIZE
                        Specify Container Size in Bytes
```
