#!/usr/bin/env python
"""
use munkres-kuhn to get RMSD between first mol2 file and all poses in 
 a second file.
Ryan Coleman 2013
"""

import os
import sys
import string
import optparse 
import mol2extend

def mol2rmsd(firstMol2name, secondMol2name, hydrogens=True):
  '''firstmol2 has a single mol2 in that file, secondmol2 can have multiple 
  poses. rmsd using munkres-kuhn for symmetry corrections, etc, is reported'''
  firstMol2 = open(firstMol2name, 'r')
  secondMol2 = open(secondMol2name, 'r')
  lines = firstMol2.readlines()
  lines.extend(secondMol2.readlines())
  mol2data = mol2extend.Mol2(mol2text=lines)
  print('mol# RMSD-in-angstroms')
  for count in range(1, mol2data.xyzCount):
    print((count, mol2data.getAdvancedRMSD(0, count, hydrogens=hydrogens)))

def main(argv):
  description = "Get the rmsd between the first file and the second (with multiples if possible)"
  version = "%prog *version 20130311* "
  usage = "%prog [options] first.mol2 second.multiple.mol2"
  parser = optparse.OptionParser(usage=usage, description=description, \
      version=version)
  parser.add_option("--nohydrogens", action="store_false", default=True, \
      dest="hydrogens", \
      help="don't use hydrogens in RMSD calculations (default: use them)")
  options, args = parser.parse_args(args=argv[1:])
  if 2 != len(args):
    parser.error("program needs 2 positional arguments.\n" +
                 "  Use --help for more information.")
  else:
    firstMol2 = args[0]
    secondMol2 = args[1]
    mol2rmsd(firstMol2, secondMol2, options.hydrogens)

if -1 != string.find(sys.argv[0], "mol2rmsd.py"):
  main(sys.argv)
