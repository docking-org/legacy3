#!/usr/bin/env python
"""Calculate AUC and logAUC.

Michael Mysinger 200710 Created
Michael Mysinger 200801 wrapio
Ryan Coleman 20111107 changed to use new code
"""

import os
import sys
import itertools
from optparse import OptionParser
import mmmutils
import enrich

def logAUC(indir):
    print((100*enrich.get_roc_own_logAUC(indir=indir)))

def main(argv):
    description = "Calculate AUC and logAUC."
    usage = "%prog [options]"
    version = "%prog *version 200801* created by Michael Mysinger"
    parser = OptionParser(usage=usage, description=description,
                          version=version)
    parser.set_defaults(indir='.')
    parser.add_option("-i", "--indir", dest="indir", 
                      help="input directory (default: %default)")
    options, args = parser.parse_args(args=argv[1:])
    if len(args) != 0:
        parser.error("program takes no positional arguments.\n" + 
                     "  Use --help for more information.")
    logAUC(options.indir)
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
