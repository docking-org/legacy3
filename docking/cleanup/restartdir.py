#!/usr/bin/env python
"""Restart dock for a subdirectory.

Michael Mysinger 200607 Created
Michael Mysinger 200711 Split from restart.py and modified for optparse
Michael Mysinger 200809 Extensive update: remove condor, support multiple 
                          dock executables, better indir handling
"""

import os
import sys
from optparse import OptionParser
import subprocess
import cleandir

SGE_SUBMIT = ["qsub"]
RESUBMIT_SCRIPT = "rerun.csh"

def restart_dir(indir='.', dock_path=None):
    valid = True
    if valid:
        cleandir.cleanout_dir(indir)
        cwd = os.getcwd()
        os.chdir(indir)
        if dock_path is None:
            if not os.path.exists("../dock.saved"):
                print("No saved dock found, using default dock version instead.")
                print("You can use the -d option to run a different dock.")
                args = [os.path.join(os.path.dirname(__file__), RESUBMIT_SCRIPT)]
            else:
                args = [os.path.join(os.path.dirname(__file__), RESUBMIT_SCRIPT)]
        else:
            args = [os.path.join(os.path.dirname(__file__), RESUBMIT_SCRIPT)]
            args.append(os.path.abspath(dock_path))
        p = subprocess.Popen(SGE_SUBMIT + args, stdout=subprocess.PIPE)
        print((p.communicate()[0]))
        open('submitted', 'w').close()
        os.chdir(cwd)
    return valid

def main(argv):
    description = "Restart dock for a given input directory."
    usage = "%prog [options]"
    version = "%prog *version 200809* created by Michael Mysinger"
    parser = OptionParser(usage=usage, description=description,
                          version=version)
    parser.set_defaults(indir='.', dock_path=None)
    parser.add_option("-i", "--indir",
                      help="input directory (default: %default)")  
    parser.add_option("-d", "--dock-path", 
                      help="full path of dock to use during restart " + 
                      "(default: ./dock.saved)")
    options, args = parser.parse_args(args=argv[1:])
    if len(args):
        parser.error("program takes no positional arguments.\n" +
                     "  Use --help for more information.")
    flag = restart_dir(indir=options.indir, dock_path=options.dock_path)
    return not flag

if __name__ == '__main__':
    sys.exit(main(sys.argv))
