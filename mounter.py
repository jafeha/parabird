import subprocess

import re

def mountparse(line_from_mount):
    '''
    give it a line from mount(not /etc/fstab!) as a string and it return a dict
    with the following keys:
        
    device(eg /dev/sdc), mountpoint /media/foo, os (linux or darwin),
    type (fstype), opts (mountoptions)
    '''
    ret={}

 
    device_point = r'''
    ^       # beginning of the line
    (.+)    #   some chars until there is a whitespace and a on - DEVICE
    \s      #   whitespace
    on      #   on - valid at linux and osx
    \s      #   whitespace
    (.+)\s  #   some chars until there is a whitespace and a "type" or ( - MPOINT            
    (\(.*\s| #( with a whitespace after some time (mac) OR              )
    type\s) #type with a whitespace short after(linux)
    (.*)\)           
    '''
    d_p = re.compile(device_point, re.VERBOSE)
    dm_listet = d_p.search(line_from_mount).groups()
    
    try:
        ret["device"], ret["mountpoint"] = dm_listet[0], dm_listet[1]
    except ValueError:
        print "could'nt decifer your mounts. is it a linux or a mac with /dev/foobar on /mountpoint ?"
    if (dm_listet[2].find("type")>=0):
        ret['os'] = 'linux'
        try:
            ret["type"], ret["opts"] = dm_listet[3].split(" (")
        except ValueError:
            print "not a linux? dont know what to do, splitting of", dm_listet[3], "failed"
    else:
        ret['os'] = 'darwin'
        temp = dm_listet[2].split(', ')
        ret['type'] = temp[0].replace('(', '')
        ret['opts'] = ", ".join(temp[1:]) + dm_listet[3]

    return ret    


#read from mount for the first time
output_first,error_first = subprocess.Popen("mount",stdout = subprocess.PIPE,
    stderr= subprocess.PIPE).communicate()

    
print "Pleaze insert stick, and wait thill is it mountet, then press ENTER"
raw_input()

#read from mount for the second time
output_second,error_second = subprocess.Popen("mount",stdout = subprocess.PIPE,
    stderr= subprocess.PIPE).communicate()

#convert it to sets
output_first_set = set(output_first.split("\n"))
output_second_set = set(output_second.split("\n"))

#iterate through the items, which are not in both sets (e.g. new lines)

for i in output_first_set.symmetric_difference(output_second_set):
    print mountparse(i)