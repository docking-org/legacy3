#!/usr/bin/env python
"""Clean out old docking results files for a single directory.

Mysinger 200706 Created
Mysinger 200908 Moved to optparse, separated clean and cleandir
"""

import os
import sys
import fnmatch
from optparse import OptionParser

def prompt_p():
    """Ask the user if they want to continue."""
    print("This will indiscriminantly delete ALL docking output here.")
    reply = eval(input("Are you sure (yes/No)? "))
    reply = reply.lower()
    return (reply == "yes" or reply == "y")

def cleanout_dir(jobdir):
    """Clean old docking results files from jobdir."""
    outfiles = ['OUTDOCK', 'stderr', 'stdout', 'test.1', 'test.eel1', 
                'test.1.gz', 'test.eel1.gz', 'condor.log', 'submitted', 
                'broken.eel1', 'outofbounds.eel1']
    names = os.listdir(jobdir)
    fnames = [x for x in fnmatch.filter(names, 'core*')]
    outfiles.extend(fnames)
    for outfile in outfiles:
        fn = os.path.join(jobdir, outfile)
        if os.path.exists(fn):
            os.remove(fn)

def cleanout(indir='.', force=False):
    print(("Input directory: ", os.path.abspath(indir)))
    if not force and not prompt_p():
        print("Exiting as requested!")
        return
    cleanout_dir(indir)

def main(argv):
    description = "Clean out old docking results files for a single directory."
    usage = "%prog [options]"
    version = "%prog *version 200908* created by Michael Mysinger"
    parser = OptionParser(usage=usage, description=description,
                          version=version)
    parser.set_defaults(indir='.', force=False)
    parser.add_option("-i", "--indir",
           help="input directory (default: %default)")
    parser.add_option("-f", "--force", action="store_true",
           help="forced output removal without prompting!")
    options, args = parser.parse_args(args=argv[1:])
    if len(args):
        parser.error("program takes no positional arguments.\n" +
                     "  Use --help for more information.")
    cleanout(indir=options.indir, force=options.force)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
