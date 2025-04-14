#!/bin/env python

"""
gets timings from OUTDOCK, sum over the entire dirlist.
Ryan Coleman 2013
"""

import os
import sys
import operator
import string
from optparse import OptionParser
import collections
import mmmutils
import checkdir
import extract_all

#constants for this module
elapsedCol = 0 #must be 'elapsed'
hoursCol = 5 #where the hours run is located

def timings_all(indirs=['.'], outfilename=None, name='target'):
  """check if done, if all done, sum timings from outdock. 
  if outfile is None, write to stdout, otherwise write to file"""
  allDone = True  
  totalHours = collections.defaultdict(float) #map from indir name to hours
  for indir in indirs:
    for subdir in mmmutils.read_dirlist(indir): 
      if checkdir.docheckdir(subdir):
        outFile = open(os.path.join(subdir, extract_all.outdockName),'r')
        for line in outFile:
          pass #don't care about any lines except the last, don't save them 
        tokens = string.split(line)
        if tokens[0] != 'elapsed':
          allDone = False
          print(subdir + ' did not finish')
        totalHours[indir] += float(tokens[hoursCol])
      else:
        allDone = False
  if not allDone:
    print("Error! The above jobs are not done, use --done to override!")
    return False
  if outfilename is not None:
    outFile = open(outfilename, 'w')
  if outfilename is not None:
    outFile.write('time in hours')
    outFile.write('target,')
  else:
    print('time in hours')
    print('target,', end=' ')
  for indir in indirs:
    if outfilename is not None:
      outFile.write(indir + ',')
    else:
      print(indir, ',', end=' ')
  if outfilename is not None:
    outFile.write('\n' + name + ',')
  else:
    print(' ')
    print(name, ',', end=' ')
  for indir in indirs:
    if outfilename is not None:
      outFile.write(str(totalHours[indir]) + ',')
    else:
      print(totalHours[indir], ',', end=' ')
  if outfilename is not None:
    outFile.write('\n')
  else:
    print(' ')
  return True

def main(argv):
  description = "Get timings in all directories in dirlist"
  usage = "%prog one directory to get timings for [list of more directories]"
  version = "%prog *version 2013* created by Ryan Coleman"
  parser = OptionParser(usage=usage, description=description,
                          version=version)
  parser.add_option('-o', '--outfilename', dest='outfilename', type='string', \
      default=None, help='output file name, default is standard out')
  parser.add_option('-t', '--target', dest='target', type='string', \
      default='-', help='target name for output, if desired')
  options, args = parser.parse_args(args=argv[1:])
  if 0 == len(args):
    args = ['.']
  ranOkay = timings_all(indirs=args, outfilename=options.outfilename, \
      name=options.target)
  if ranOkay:
    return 0
  else:
    return 1

if __name__ == '__main__':
  sys.exit(main(sys.argv))
