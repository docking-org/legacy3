#!/usr/bin/python
# cp ~jji/bin/md4db-trent.pl 

# Writen by Trent Balius
# modifed from ~jji/bin/md4db-trent.pl
# refer to http://wiki.bkslab.org/index.php/Physical_property_space
# go to bottom of wiki page for next 4

# note that the space is very uneven, we will make the chuncks roughly the same size.  

import os
import sys
import shutil

class File_DATA:
    def __init__(self, size, name):
        self.size = size
        self.name = name
    def __cmp__(self, other):
        return cmp(self.size, other.size)
# this defines a compares two LIG_DATA by comparing the two scores
# it is sorted in decinding order.
def bySize(x, y):
    return cmp(x.size, y.size)


if len(sys.argv) <2 or len(sys.argv) > 5:
  print((len(sys.argv)))
  print('Usage: setup_db2_zinc15.py [dir] [name] [shards|frags|custom] [custum definition]')
  print('dir is the path were to perpare database for docking')
  print('name is the idenifing name')
  print('there are perdefined choices: shards, frags or you can give a custum selection')
  print('custum selection will a defintion of the 6 axes (), the should be devied by commas')
  sys.exit(-1)

root = "/nfs/db/dockable/zinc15/byproperty";
# this is "Shards"
dir  = sys.argv[1] # directory to make
name = sys.argv[2] # 
type = sys.argv[3]
indock      = "INDOCK"
dirlist      = "dirlist"
gridssphere = "dockfiles"

if (type == "custom"):
    custom = sys.argv[4] 
    splitcus = custom.split(',')
    if (len(splitcus) != 6):
        print("ERROR: custum parm is not right.")
    first  = splitcus[0] # mwt
    second = splitcus[1] # logP
    third  = splitcus[2] # phmod_fk = ref, mid
    fourth = splitcus[3] # clean axis
    fifth  = splitcus[4] # purchasability
    sixth  = splitcus[5]  #charge

elif (type == "shards"):
  # mwt 
  first  = "A" # <= 200 amu
  # logP 
  second = "ABCDEFGHIJK" #   no restriction on logP
  # we want physiological pH
  third = "01" # phmod_fk = ref, mid
  # clean axis, not yet implemented property, take all for now
  fourth = "ABCDE" 
  #fourth = "AB" 
  # purchasability
  fifth = "ABCD" # in stock and on demand
  # charge, you don't care, take all?
  sixth = "ABCDE" # any 
#elif (type == "frags"):
else: 
  print((type + " is not defined. "))


fileslines = []
for i1 in range(len(first)):
    for i2 in range(len(second)):
        for i3 in range(len(third)):
            for i4 in range(len(fourth)):
                for i5 in range(len(fifth)):
                    for i6 in range(len(sixth)):
                        path = root+"/"+first[i1]+second[i2]+"/"+third[i3]+fourth[i4]+fifth[i5]+sixth[i6]+"/db2/*.db2.gz"
                        handel = os.popen("ls -l "+path)
                        #handel = os.popen("ls -1 "+root+"/"+first[i1]+second[i2]+"/"+third+fourth[i4]+fifth[i5]+sixth[i6]+"/db2/*.db2.gz")

                        for line in handel.readlines(): 
                            fileslines.append(line)
                        handel.close()

# populate a data structure to sort on size.
# this is one way to do this. 
filedata = []
for line in fileslines:
    #print line
    splitline = line.split()
    #print splitline[0], splitline[1], splitline[2], splitline[3], splitline[4]
    temp_fd = File_DATA(int(splitline[4]), splitline[8])

    filedata.append(temp_fd)

# sort by file size, bigest file is at the end of the list.
filedata.sort(bySize)
#handel.closed

total = 0 # loop over the files from smallest to largest. 
          # when the size exceds the max make new file.
maxfilesize = filedata[-1].size # ge the value at the end of the list
count = 1
#filename = '%s%04d'%(name,count)
filename = 'split_database_index'
dirname   = '%s/%s%04d'%(dir,name,count)

os.system('rm -rf '+dirname+';mkdir -p '+dirname)
#os.system('mkdir -p '+dirname)

if not (os.path.exists(dir)):
    print((dir + "does not exists.  "))
    exit()
elif not (os.path.exists(dir+"/"+indock)):
    print((dir+"/"+indock + "does not exists.  ")) 
    exit()
elif not (os.path.exists(dir+"/"+gridssphere)):
    print((dir+"/"+gridssphere))
    exit()
filehdirlist = open(dir+'/'+dirlist,'w')
filehdirlist.write(dirname+'\n')
fileh = open(dirname+'/'+filename,'w')
#shutil.copy(dir+"/"+indock, dirname)
os.system("cp "+dir+"/"+indock+" "+dirname)
for data in filedata:
    if total < maxfilesize:
        print((data.size, data.name))
        fileh.write(data.name+'\n')
    else: 
        print("start new file") 
        print(total)
        total = 0
        fileh.close()
        count = count+1
        #filename = 'temp%04d'%count
        dirname   = '%s/%s%04d'%(dir,name,count)
        os.system('rm -rf '+dirname+';mkdir -p '+dirname)
        os.system("cp "+dir+"/"+indock+" "+dirname)
        filehdirlist.write(dirname+'\n')
        fileh = open(dirname+'/'+filename,'w')
        fileh.write(data.name+'\n')
    total = total + data.size

#fileh.write(data.name+'\n')
fileh.close()
filehdirlist.close()


