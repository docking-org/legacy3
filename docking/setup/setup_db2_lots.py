#!/usr/bin/env python

import os
import sys
import glob
import math
import tempfile
import shutil
import string
import collections

dirlist = 'dirlist'
prefix = 'docking.'
indock = 'INDOCK'
splitName = 'split_database_index'

if len(sys.argv) < 2:
  print('Usage: setup_db2_lots.py desiredNumDirs prefix "/path/to/db2files/*.db2.gz"')
  sys.exit(-1)
else:
  numDirs = int(sys.argv[1])
  zlenDirs = int(math.log10(numDirs)) + 1 
  prefix = sys.argv[2] 
  dirGlobNames = sys.argv[3:]
  if len(dirGlobNames) == 1: #only provided path
    if dirGlobNames[0].rfind('.gz') == -1: #if the path doesn't have a wildcard
      dirGlobNames[0] = os.path.join(dirGlobNames[0], '*.db2.gz')
tempFile = tempfile.NamedTemporaryFile(prefix=dirlist + '.', suffix='.backup', \
    delete=False, dir=os.getcwd())
tempName = tempFile.name
tempFile.close()
try:
  shutil.copy(dirlist, tempName)
  print(("backing up old dirlist to " + tempName))
except IOError: #dirlist didn't exist, no need to backup
  pass #which is fine
dirlistFile = open(dirlist, 'w') #overwrite old file
splitFiles = collections.defaultdict(list)
db2count = 0
for dirGlobName in dirGlobNames:
  for db2File in glob.iglob(dirGlobName):
    print(('adding', db2File))
    if db2count < numDirs:
      dirName = prefix + string.zfill(db2count, zlenDirs)  
      dirlistFile.write(dirName + '\n')
      os.mkdir(dirName)
      os.symlink(os.path.join(os.getcwd(), indock), \
          os.path.join(dirName, indock))
      splitFiles[os.path.join(dirName, splitName)].append(db2File)
    else:
      dirName = prefix + string.zfill(db2count % numDirs, zlenDirs)  
      splitFiles[os.path.join(dirName, splitName)].append(db2File)
    db2count += 1
dirlistFile.close()  
for splitFileKey, splitFileValues in list(splitFiles.items()):
  splitFile = open(splitFileKey, 'w')
  for splitFileValue in splitFileValues:
    splitFile.write(splitFileValue + '\n')
  splitFile.close()
