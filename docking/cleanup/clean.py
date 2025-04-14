#!/usr/bin/env python
"""Clean out old docking results files for a run.

Mysinger 200706 Created
Mysinger 200908 Moved to optparse, separated clean and cleandir
"""

import os
import sys
from optparse import OptionParser
import cleandir
import mmmutils

def cleanout_run(indir='.', force=False):
    """Clean old docking results files for this run."""
    print(("Input directory: ", os.path.abspath(indir)))
    if not force and not cleandir.prompt_p():
        print("Exiting as requested!")
        return
    cleaned_files = ["dock.saved", "stderr"]
    for cfile in cleaned_files:
        if os.path.exists(cfile):
            os.remove(cfile)
    for subdir in mmmutils.read_dirlist(indir):
        cleandir.cleanout_dir(subdir)

def main(argv):
    description = "Clean out old docking results files for an entire run."
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
    cleanout_run(indir=options.indir, force=options.force)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
