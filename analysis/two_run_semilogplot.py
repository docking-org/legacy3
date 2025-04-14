#!/bin/env python
"""
call two_run_compare on 2 directories, then plot
"""

import matplotlib  # must import first
matplotlib.use('Agg')  # allows you to not have an x-server running
#these lines must be first, if pylab is imported first it ruins this

import os
import sys
from optparse import OptionParser
import two_run_compare
import extract_all
import pylab

def two_run_semilogplot(onedir, twodir, outNamePrefix=None):
    """run two_run_compare, then plot"""
    if outNamePrefix is None:
        outNamePrefix = onedir.strip('/') + '_' + twodir.strip('/')
    outNameTxt = outNamePrefix + '.compare.txt'
    outNamePlot = outNamePrefix + '.plot.png'
    outNameMinimumPlot = outNamePrefix + '.minimum.plot.png'
    outNameLigPlot = outNamePrefix + '.lig.plot.png'
    outNameDecPlot = outNamePrefix + '.dec.plot.png'
    success, allKeys, exDicts = \
                two_run_compare.two_run_compare(onedir, twodir, outNameTxt)
    if success:
        #make a graph with all the data, ligands colored differently
        xData, yData = [], []
        xDecData, yDecData = [], []
        xLigData, yLigData = [], []
        line = [0.01*(count-200) for count in range(40000)]
        #lineMinus50 = [0.01*(count-200)-50 for count in xrange(40000)]
        #linePlus50 = [0.01*(count-200)+50 for count in xrange(40000)]
        for aKey in allKeys:
            if aKey in exDicts[0] and aKey in exDicts[1]:
                xData.append(float(exDicts[0][aKey]))
                deltaG = float(exDicts[0][aKey]) - float(exDicts[1][aKey])
                yData.append(deltaG)
                if aKey[0].find('lig') != -1:
                  xLigData.append(float(exDicts[0][aKey]))
                  yLigData.append(deltaG)
                elif aKey[0].find('dec') != -1:
                  xDecData.append(float(exDicts[0][aKey]))
                  yDecData.append(deltaG)
        pylab.semilogy(xDecData, yDecData, '.', color='red')
        pylab.semilogy(xLigData, yLigData, 'o', color='blue')
        #pylab.semilogy(lineMinus50, line, color='grey')
        #pylab.semilogy(linePlus50, line, color='grey')
        pylab.semilogy(line, line, color='grey')
        curAxis = pylab.axis('tight')
        pylab.semilogy(line, line, color='grey')
        pylab.axis([curAxis[0]-2, min(500, curAxis[1]), 0, 500])
        pylab.savefig(outNamePlot)
        pylab.clf()
        pylab.semilogy(xLigData, yLigData, 'o', color='blue')
        #pylab.semilogy(line, line, color='grey')
        curAxis = pylab.axis('tight')
        pylab.semilogy(line, line, color='grey')
        pylab.axis([curAxis[0]-2, min(500, curAxis[1]), 0, 500])
        pylab.savefig(outNameLigPlot)
        pylab.clf()
        pylab.semilogy(xDecData, yDecData, '.', color='red')
        #pylab.semilogy(line, line, color='grey')
        curAxis = pylab.axis('tight')
        pylab.semilogy(line, line, color='grey')
        pylab.axis([curAxis[0]-2, min(500, curAxis[1]), 0, 500])
        pylab.savefig(outNameDecPlot)
        pylab.clf()
        uniqueDicts = []
        for exDict in exDicts:
            uniqueDicts.append(extract_all.takeMinimum(exDict))
        xDecData, yDecData = [], []
        xLigData, yLigData = [], []
        uniqueKeys = list(set(list(uniqueDicts[0].keys()) + list(uniqueDicts[1].keys())))
        uniqueLigNoDelta, uniqueDecNoDelta = 0, 0
        for aKey in uniqueKeys:
            if aKey in uniqueDicts[0] and aKey in uniqueDicts[1]:
                omegaG = float(uniqueDicts[0][aKey][1])
                deltaG = omegaG - float(uniqueDicts[1][aKey][1])
                if uniqueDicts[0][aKey][0].find('lig') != -1:
                  xLigData.append(omegaG)
                  yLigData.append(deltaG)
                  if deltaG < 0.0001:
                      uniqueLigNoDelta += 1
                elif uniqueDicts[0][aKey][0].find('dec') != -1:
                  xDecData.append(omegaG)
                  yDecData.append(deltaG)
                  if deltaG < 0.0001:
                      uniqueDecNoDelta += 1
        #pylab.plot(xDecData, yDecData, '.', color='red')
        #pylab.plot(xLigData, yLigData, 'o', color='blue')
        pylab.semilogy(xDecData, yDecData, '.', color='red')
        pylab.semilogy(xLigData, yLigData, 'o', color='blue')
        curAxis = pylab.axis('tight')
        pylab.semilogy(line, line, color='grey')
        pylab.axis([curAxis[0]-2, min(500, curAxis[1]), 0, 500])
        pylab.savefig(outNameMinimumPlot)
        pylab.clf()
        print((uniqueLigNoDelta, len(xLigData)))
        print((uniqueDecNoDelta, len(xDecData)))

def main(argv):
    description = "Make graph of extracted differences between directories"
    usage = "%prog one_dir(nomnm) other_dir(mnm)"
    version = "%prog *version 201004* created by Ryan Coleman"
    parser = OptionParser(usage=usage, description=description,
                          version=version)
    parser.add_option("-t", "--title", type="string", action="store", \
      dest="title", default=os.path.basename(os.getcwd()), \
      help="title of graph, prepended to output filenames, (default: %default)")
    options, args = parser.parse_args() #default reads from argv[1:]
    if len(args) != 2:
        parser.error("program takes 2 positional arguments.\n" +
                     "  Use --help for more information.")
    else:
        onedir = args[0]
        twodir = args[1]
    return two_run_semilogplot(onedir, twodir, options.title)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
