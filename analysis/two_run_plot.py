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


def two_run_plot(onedir, twodir, outNamePrefix=None, maxY=10):
  """run two_run_compare, then plot"""
  if outNamePrefix is None:
    outNamePrefix = onedir.strip('/') + '_' + twodir.strip('/')
  maxX = maxY
  lastBigChangeName = ""
  outNameTxt = outNamePrefix + '.compare.txt'
  outNamePlot = outNamePrefix + '.plot.png'
  outNameNoZeroPlot = outNamePrefix + '.no0.plot.png'
  outNameMinimumPlot = outNamePrefix + '.minimum.plot.png'
  outNameLigPlot = outNamePrefix + '.lig.plot.png'
  outNameDecPlot = outNamePrefix + '.dec.plot.png'
  allKeys, exDicts = \
     two_run_compare.two_run_compare(onedir, twodir, outNameTxt)
  #make a graph with all the data, ligands colored differently
  xData, yData = [], []
  xDecData, yDecData = [], []
  xLigData, yLigData = [], []
  xDecDataZ, yDecDataZ = [], []
  xLigDataZ, yLigDataZ = [], []
  line = [0.01*(count-20000) for count in range(40000)]
  #lineMinus50 = [0.01*(count-200)-50 for count in xrange(40000)]
  #linePlus50 = [0.01*(count-200)+50 for count in xrange(40000)]
  for aKey in allKeys:
    if aKey in exDicts[0] and aKey in exDicts[1]:
      xDatum = float(exDicts[0][aKey][1])
      yDatum = float(exDicts[1][aKey][1])
      xData.append(float(exDicts[0][aKey][1]))
      yData.append(float(exDicts[1][aKey][1]))
      if yDatum < maxY:
        if xDatum > maxX:
          lastBigChangeName = aKey
          #maxX = xDatum
      if exDicts[0][aKey][0].find('lig') != -1:
        xLigData.append(float(exDicts[0][aKey][1]))
        yLigData.append(float(exDicts[1][aKey][1]))
        if xDatum != yDatum:
          xLigDataZ.append(xDatum)
          yLigDataZ.append(yDatum)
      elif exDicts[0][aKey][0].find('dec') != -1:
        xDecData.append(float(exDicts[0][aKey][1]))
        yDecData.append(float(exDicts[1][aKey][1]))
        if xDatum != yDatum:
          xDecDataZ.append(xDatum)
          yDecDataZ.append(yDatum)
  print(lastBigChangeName)
  pylab.plot(xDecData, yDecData, '.', color='red')
  pylab.plot(xLigData, yLigData, 'o', color='blue')
  #pylab.plot(lineMinus50, line, color='grey')
  #pylab.plot(linePlus50, line, color='grey')
  curAxis = pylab.axis('tight')
  pylab.xlabel(onedir)
  pylab.ylabel(twodir)
  pylab.plot(line, line, color='grey')
  pylab.axis([curAxis[0]-1, min(maxX, curAxis[1]) + 1, curAxis[2]-1, \
                    min(maxY, curAxis[3]) + 1])
  pylab.suptitle(outNamePrefix)
  #pylab.set_size_inches(8., 8.) #square figures
  pylab.savefig(outNamePlot)
  pylab.clf()
  pylab.plot(xDecDataZ, yDecDataZ, '.', color='red')
  pylab.plot(xLigDataZ, yLigDataZ, 'o', color='blue')
  curAxis = pylab.axis('tight')
  pylab.xlabel(onedir)
  pylab.ylabel(twodir)
  pylab.plot(line, line, color='grey')
  pylab.axis([curAxis[0]-1, min(maxX, curAxis[1]) + 1, curAxis[2]-1, \
                    min(maxY, curAxis[3]) + 1])
  pylab.suptitle(outNamePrefix)
  pylab.savefig(outNameNoZeroPlot)
  pylab.clf()
  pylab.plot(xLigData, yLigData, 'o', color='blue')
  curAxis = pylab.axis('tight')
  pylab.xlabel(onedir)
  pylab.ylabel(twodir)
  pylab.plot(line, line, color='grey')
  pylab.axis([curAxis[0]-1, min(maxX, curAxis[1]) + 1, curAxis[2]-1, \
                   min(maxY, curAxis[3]) + 1])
  pylab.suptitle(outNamePrefix)
  pylab.savefig(outNameLigPlot)
  pylab.clf()
  pylab.plot(xDecData, yDecData, '.', color='red')
  #pylab.plot(line, line, color='grey')
  curAxis = pylab.axis('tight')
  pylab.xlabel(onedir)
  pylab.ylabel(twodir)
  pylab.plot(line, line, color='grey')
  pylab.axis([curAxis[0]-1, min(maxX, curAxis[1]) + 1, curAxis[2]-1, \
                 min(maxY, curAxis[3]) + 1])
  pylab.suptitle(outNamePrefix)
  pylab.savefig(outNameDecPlot)
  pylab.clf()

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
  return two_run_plot(onedir, twodir, options.title)

if __name__ == '__main__':
  sys.exit(main(sys.argv))
