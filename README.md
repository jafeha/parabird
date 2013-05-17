parabird
========

Parabird is a Python script for building a os independent [Linux, Windows and Mac OS] truecrypt encrypted usb-stick containing a portable version of thunderbird, enigmail, torbirdy and vidalia and a shared profile.

**NOTE:** The script is functional, but it is definitely in beta state. At the moment **GPG is not supported for Mac OS**. Give me a litte time to figure things out because it is also some kind of a python learning script for me. If you have some hints for solving our issues or any thunderbird tweaking tips, please get in touch. 

#### Download / Install:
Downloading and running parabird is quite simple. Please take care of the depedencies and take a look at the usage below.

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
