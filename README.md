parabird
========

Parabird is a Python script for building a os independent [Linux, Windows and Mac OS] truecrypt encrypted usb-stick containing a portable version of thunderbird, enigmail, torbirdy and vidalia and a shared profile.

**NOTE:** The script is functional, but this is still a Release Candidate. If you find a bug, please open an issue. Thunderbird for Mac OS and especially **the GPG/Enigmail Setup for Mac OS needs testing**. Give me a litte time to figure things out because it is also some kind of a python learning script for me. If you have some hints for solving our issues or any thunderbird tweaking tips, please get in touch.

**SECURITY NOTE:** Until we've reached a more stable stage after some more testing, we use /dev/urandom instead of /dev/random. We do this for performance reasons. If you actually want to use Parabird productively **we strongy recommend to use /dev/random.** You can specify this changing the truecrypting command in the config.ini. If you like to know more about the difference between /dev/random and /dev/urandom, take a look here http://www.onkarjoshi.com/blog/191/device-dev-random-vs-urandom/

#### Download / Install:
If you want to test or run parabird, you best go with the tarball: [parabird-0.0.1-RC1.tar.gz](https://github.com/jafeha/parabird/raw/master/parabird-0.0.1-RC1.tar.gz)
Please take care of the depedencies and take a look at the usage below.

#### Contributing code:
If you like to join the parabird development, you best start downloading the git repo. Please take care of the depedencies and take a look at the usage below.

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
