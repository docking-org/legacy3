#!/usr/bin/python
# cp ~jji/bin/md4db-trent.pl 

# Writen by Trent Balius
# this script reads in a file, including files from zinc15.  
# the file will contain the full path to each database file.  
# you can download the file from zinc15 here: 
#    http://zinc15.docking.org/tranches/build/#
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
  print('Usage: setup_db2_zinc15.py [dir] [name] filename')
  print('dir is the path were to perpare database for docking')
  print('name is the idenifing name')
  print('file with path were dbs are,  this you can download from zinc15')
  sys.exit(-1)

root = "/nfs/db/dockable/zinc15/byproperty";
# this is "Shards"
dir  = sys.argv[1] # directory to make
name = sys.argv[2] # 
file = sys.argv[3]
indock      = "INDOCK"
dirlist      = "dirlist"
gridssphere = "dockfiles"

infh = open(file,'r')
fileslines = infh.readlines()
infh.close()

# populate a data structure to sort on size.
# this is one way to do this. 
filedata = []
for line in fileslines:
    #print line
    line = line.strip('\n')
    if not (os.path.exists(line)):
        print((line + " doesn't exist."))
        splitline =line.split('/')
        line = '' 
        N = len(splitline)
        for i in range(N):
           if i == N-1:
              line = line+'/db2'
           line = line+'/'+splitline[i]
        if not (os.path.exists(line)):
            print((line + " doesn't exist."))
            continue 
        else: 
            print(("the file is "+ line))
    handel = os.popen("ls -lL "+line)
                        #handel = os.popen("ls -1 "+root+"/"+first[i1]+second[i2]+"/"+third+fourth[i4]+fifth[i5]+sixth[i6]+"/db2/*.db2.gz")
    lines = handel.readlines()
    if len(lines) > 1:
        print(lines)
        exit()
    line = lines[0]
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


