#!/bin/env python
"""Check status of dock subjobs for this run.

Michael Mysinger 200705 Created
Michael Mysinger 200707 Modified for optparse and outdir
Michael Mysinger 200801 Changed misguided outdir to indir
Michael Mysinger 200809 Remove condor support to simplify stderr handling
Michael Mysinger 200909 Added separate cleandir program
"""

import os
import sys
from optparse import OptionParser
import mmmutils

from checkdir import *

def notdone(indir='.'):
    """Return dictionary of unfinished directories and their status"""
    result = []
    for subdir in mmmutils.read_dirlist(indir):
        check = checkdir(subdir)
        if check is not None:
            result.append((os.path.basename(subdir), check))
    return result

def docheck(indir='.'):
    """Test if all dock subjobs are done."""
    jobs = notdone(indir=indir)
    jobsleft = [x for x in jobs if x[1] not in DONE_TYPES]
    if not jobsleft:
        return True
    for job in jobsleft:
        print((job[0], job[1]))
    return False

def main(argv):
    description = "Check status of dock subjobs for this run."
    usage = "%prog [options]"
    version = "%prog *version 200909* created by Michael Mysinger"
    parser = OptionParser(usage=usage, description=description,
                          version=version)
    parser.set_defaults(indir='.')
    parser.add_option("-i", "--indir",
           help="check results inside this directory (default: %default)")  
    options, args = parser.parse_args(args=argv[1:])
    if len(args):
        parser.error("program takes no positional arguments.\n" +
                     "  Use --help for more information.")
    passed = docheck(indir=options.indir)
    return not passed

if __name__ == '__main__':
    sys.exit(main(sys.argv))
