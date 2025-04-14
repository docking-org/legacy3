#! /usr/bin/python2.7

# writen by Trent balius

# remove list from extract all file. 

import sys, os, os.path


def sort_extract_file(filename,filename_prefix):

   print("sorting ...")
   #cmd = "sort -rk 21 " + filename + " > " + filename_prefix+"sort.txt"
   cmd = "sort -nk 22 " + filename + " > " + filename_prefix+"sort.txt"
   print("running . . . ") 
   print(cmd)
   os.system(cmd)
   #os.popen('"'+cmd+'"')
   print("done sorting.")

def make_uniq(infilename,filename_prefix):
    print("making unique ...")
    infile = open(infilename,'r')
    outfile = open(filename_prefix+"sort.uniq.txt",'w')
    zdic ={} # dictionary of zinc names
    for line in infile: 
        #print line
        splitline = line.split()
        zname = splitline[2]
        #print zname
        if zname in zdic: 
           continue
        else:
           outfile.write(line)
           zdic[zname]=1
    infile.close()       
    outfile.close()       
    print("done making unique.")
        
def main():
   if len(sys.argv) != 4:
      print("error:  this program takes 3 argument ")
      print("(1) combined extract_all file (from parallel run).  ")    
      print("(2) name of the extract all file to be written.  ")    
      print("(3) max_energy to be written to file.  ")    
      exit()
   
   filename1     = sys.argv[1]
   output        = sys.argv[2]
   max_energy    = float(sys.argv[3])
   if (os.path.exists(output)):
       print(("%s exists. stop. " % output))
       exit()
   print(("(1) dirlist = " + filename1))
   print(("(2) output = "  + output))
   print(("(3) energy threshold = %6.3f" % max_energy))
   fh = open(filename1)  

   # remove extension.
   splitfilename = output.split(".") 
   if(splitfilename[-1]!="txt"): 
      print("uhoh.  %s should have .txt extension. exiting...")
      exit()
   filename_prefix = ''
   for i in range(len(splitfilename)-1):
       filename_prefix = filename_prefix+splitfilename[i]+'.'

   sort_extract_file(filename1,filename_prefix)
   make_uniq(filename_prefix+"sort.txt",filename_prefix)

main()

