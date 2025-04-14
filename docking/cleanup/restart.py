#!/usr/bin/env python
"""Restart dock for as needed for subjobs.

Michael Mysinger 200607 Created
Michael Mysinger 200711 Modified for optparse and force
Michael Mysinger 200809 Remove condor and offer multiple dock executables
"""

import os
import sys
from optparse import OptionParser
import sh
import check
import mmmutils
import restartdir
 
def restart_jobs(jobs, force=False, noscores=False, dock_path=None):
    scorednone = False
    if force == True:
        for job in jobs:
            print((job[0], job[1]))
            if job[1] not in check.DONE_TYPES:
                print(("Forcing %s to restart." % job[0]))
                restartdir.restart_dir(indir=job[0], dock_path=dock_path)
    else:
        for job in jobs:
            print((job[0], job[1]))
            restart = False
            if job[1] == check.NOT_SUB:
                print(("%s was not yet submitted, submitting now." % job[0]))
                restart = True
            elif job[1] == check.NO_OUTDOCK:
                print(("%s failed to start dock, restarting now." % job[0]))
                restart = True
            elif job[1] == check.DOCK_ERROR:
                print(("%s failed inside DOCK, restarting now." % job[0]))
                restart = True
            elif job[1] == check.BROKEN:
                print(("%s OUTDOCK is incomplete, restarting now." % job[0]))
                restart = True
            elif job[1] == check.SCORED_NONE and noscores:
                print(("%s scored no ligands, restarting now." % job[0]))
                restart = True
            if restart:
                restartdir.restart_dir(indir=job[0], dock_path=dock_path)

def restart_run(force=False, noscores=False, dock_path=None):
    """Restart failed dock jobs."""
    dirs = list(mmmutils.read_dirlist('.'))
    num = len(dirs)
    outdocks = dirs | sh.sed('$', os.sep+'OUTDOCK')
    done = sum((sh.tail(x, 1) | sh.grep('^elapsed time') | sh.count
                for x in outdocks if os.path.exists(x)))
    if done != num:
        head = os.path.split(os.getcwd())[0]
        target = os.path.split(head)[1]
        print(('%s: %s/%s' % (target, done, num)))
        jobs = check.notdone()
        if jobs:
            restart_jobs(jobs, force=force, noscores=noscores, 
                         dock_path=dock_path)

def main(argv):
    description = "Restart DOCK as needed for subdirectories."
    usage = "%prog [options]"
    version = "%prog *version 200809* created by Michael Mysinger"
    parser = OptionParser(usage=usage, description=description,
                          version=version)
    parser.set_defaults(force=False, noscores=False, dock_path=None)
    parser.add_option("-f", "--force-it", action="store_true",
           dest="force", help="force restart for all unfinished jobs")
    parser.add_option("-n", "--noscores", action="store_true",
           help="restart jobs that scored no ligands")
    parser.add_option("-d", "--dock-path",
           help="full path of dock to use during restart " + 
                      "(default: ./dock.saved)")
    options, args = parser.parse_args(args=argv[1:])
    if len(args):
        parser.error("program takes no positional arguments.\n" +
                     "  Use --help for more information.")
    restart_run(force=options.force, noscores=options.noscores, 
                dock_path=options.dock_path)
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
