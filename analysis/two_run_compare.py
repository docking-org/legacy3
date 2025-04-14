#!/bin/env python
"""run extract_all in each of 2 directories, then combine them into one master 
file that is used to make graphs/import into other program.

"""

import os
import sys
from optparse import OptionParser
import extract_all

def two_run_compare(onedir, twodir, outName=None):
  """run extract_all in each dir. if successful, make comparison file."""
  extracted = ['', '']
  extracted[0] = extract_all.get_scores_all(onedir)
  extracted[1] = extract_all.get_scores_all(twodir)
  extractedDicts = [{}, {}]
  allKeys = set()
  for count in range(2):
    for line in extracted[count]:
      allKeys.add(line[extract_all.zincCol])
      extractedDicts[count][line[extract_all.zincCol]] = \
          (line[extract_all.dirCol], float(line[extract_all.scoreCol]), \
          line[extract_all.zincCol])
  allKeys = list(allKeys)
  allKeys.sort()
  if outName is None:
    outName = onedir.strip('/') + '_' + twodir.strip('/')+'.compare.txt'
  outFile = open(outName, 'w') #comparison file output
  for aKey in allKeys:
    if aKey in extractedDicts[0] and aKey in extractedDicts[1]:
      outFile.write(str(aKey) + '\t')
      outFile.write(str(extractedDicts[0][aKey][0]) + '\t')
      outFile.write(str(extractedDicts[0][aKey][1]) + '\t')
      outFile.write(str(extractedDicts[1][aKey][1]) + '\n')
    else:
      print((aKey, "not present in both files"))
  outFile.close()
  print("keys match in both files, two_run_compare finished")
  return allKeys, extractedDicts

def main(argv):
  description = "Run extract_all on both directories"
  usage = "%prog one_dir other_dir"
  version = "%prog *version 201004* created by Ryan Coleman"
  parser = OptionParser(usage=usage, description=description,
                          version=version)
  options, args = parser.parse_args(args=argv[1:])
  if len(args) != 2:
    parser.error("program takes 2 positional arguments.\n" +
                   "  Use --help for more information.")
  else:
    onedir = args[0]
    twodir = args[1]
  two_run_compare(onedir, twodir)[0]

if __name__ == '__main__':
  sys.exit(main(sys.argv))
