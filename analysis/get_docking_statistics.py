#! /usr/bin/python2.7

# writen by Trent Balius
# modified by Jiankun Lyu
# modified by Trent Balius (2017/10/26)

# remove list from extract all file. 

import sys, os, os.path

def read_outdock_file_write_extract_all(infilename,outfile1,outfile2,dic_zinc_id,dic_zinc_id_scored,dic_zincid_error_bump,dic_zincid_error_clash,dic_zincid_error_no_match,dic_zincid_error_no_valid,dic_zincid_error_skip,\
                                        dic_zincid_error_miss):
#def read_outdock_file_write_extract_all(path,infilename,extractfilename,maxenergy):

    infile = open(infilename,'r')
    lines = infile.readlines()
    infile.close()

#   if (os.path.exists(extractfilename)):
#      outfile = open(extractfilename,'a')
#   else:
#      outfile = open(extractfilename,'w')


    flag_read = False
    flag_stat = False
##  close SDIFILE
## total minimization steps =        801219
## total number of hierarchies:         16114
## total number of orients (matches):      20811601
## total number of conformations (sets):       2147921
## total number of nodes (confs):       4984826
## total number of complexes:                2685046286
## end of file encountered
##Date and Time: 20171013 174229.9
##elapsed time (sec):     5484.6802  (hour):     1.5235
    minsteps = 0 ; numhier = 0 ; numorient = 0; numconf = 0; numnode = 0; numcomplex = 0 ; secs = 0.0; hours = 0.0
    #zincid_dic = {}
    #zincid_broken_dic = {}
    for line in lines:
        splitline = line.split()

        if len(splitline) ==0:
            continue

        if "we" == splitline[0]: # we reached the end of the file, docking results.
             flag_read = False

        if flag_read:         
          if len(splitline) == 21:
                #just output the ZINCID
                zincid = splitline[1]
                dic_zinc_id[zincid] = 1
                dic_zinc_id_scored[zincid] = 1
                outfile1.write("%s\n"%(zincid))
                outfile2.write("%s\n"%(zincid))
          elif ( len(splitline) > 2 ) and ( "ZINC" in splitline[1] ):
                zincid = splitline[1]
                dic_zinc_id[zincid] = 1
                if "bump" in line:
                    dic_zincid_error_bump[zincid] = 1
                elif "no_match" in line:
                    dic_zincid_error_no_match[zincid] = 1
                elif "No viable poses." in line:
                    dic_zincid_error_no_valid[zincid] = 1
                elif "clash" in line:
                    dic_zincid_error_clash[zincid] = 1
                elif "skip" in line:
                    dic_zincid_error_skip[zincid] = 1
                else: 
                    print(line)
                    dic_zincid_error_miss[zincid] = 1
                outfile2.write("%s\n"%(zincid))
        elif flag_stat:
          if "minimization" in line: 
              minsteps = minsteps+int(splitline[4])
          if "hierarchies" in line: 
              numhier = numhier+int(splitline[4])
          if "orients" in line: 
              numorient = numorient+int(splitline[5])
          if "conformations" in line: 
              numconf = numconf+int(splitline[5])
          if "nodes" in line: 
              numnode = numnode+int(splitline[5])
          if "complexes" in line: 
              numcomplex = numcomplex+int(splitline[4])
          if "elapsed time" in line: 
              secs = secs+float(splitline[3])
              hours = hours+float(splitline[5])
              flag_stat = False
         
        if  "mol#" == splitline[0]: # start of docking resutls
             flag_read = True
             flag_stat = False
        if splitline[0] == "close" and splitline[1] == "SDIFILE": 
             flag_read = False
             flag_stat = True

#   outfile.close()
    return minsteps, numhier,  numorient, numconf,  numnode,  numcomplex,  secs, hours

        
def main():
   if len(sys.argv) != 4:
      print("error:  this program takes 3 argument ")
      print("(0) path where dock directorys are.  ")    
      print("(1) dirlist where outdock file are.  ")    
      print("(2) prefix name of the count all files to be written.  ")    
      exit()
   
   path          = sys.argv[1]
   filename1     = sys.argv[2]
   output        = sys.argv[3]

   # stats 
   totminsteps = 0 ; totnumhier = 0 ; totnumorient = 0; totnumconf = 0; totnumnode = 0; totnumcomplex = 0 ; totsecs = 0.0; tothours = 0.0
   tot_dic_zinc_id = {} ; tot_dic_zinc_id_scored = {};
   tot_dic_zincid_error_bump = {} ; tot_dic_zincid_error_no_match = {}; tot_dic_zincid_error_clash = {} ; tot_dic_zincid_error_no_valid = {} ; tot_dic_zincid_error_skip = {} ; tot_dic_zincid_error_miss = {}

   if (os.path.exists(output)):
       print(("%s exists. stop. " % output))
       exit()
   print(("(1) dirlist = " + filename1))
   print(("(2) output = "  + output))
   fh = open(filename1)  

   # remove extension.
   splitfilename = output.split(".") 
   if(splitfilename[-1]!="txt"): 
      print("uhoh.  %s should have .txt extension. exiting...")
      exit()
   filename_prefix = ''
   for i in range(len(splitfilename)-1):
       filename_prefix = filename_prefix+splitfilename[i]+'.'
   outfile1 = open(filename_prefix+"scored.zincid",'w')
   outfile2 = open(filename_prefix+"docked.zincid",'w')

   for line in fh:
       print(line)
       #splitline = line.split() 
       #pathname = line.split()[0]
       filename = line.split()[0]+'/OUTDOCK'
       #read_outdock_file_write_extract_all(pathname,filename,output,max_energy)
       tempminsteps, tempnumhier,  tempnumorient, tempnumconf,  tempnumnode,  tempnumcomplex,  tempsecs, temphours = read_outdock_file_write_extract_all(path+"/"+filename,outfile1,outfile2,tot_dic_zinc_id,tot_dic_zinc_id_scored \
                                                                                                                      ,tot_dic_zincid_error_bump,tot_dic_zincid_error_no_match,tot_dic_zincid_error_clash,tot_dic_zincid_error_no_valid,\
                                                                                                                       tot_dic_zincid_error_skip,tot_dic_zincid_error_miss)

       totminsteps   = totminsteps   + tempminsteps
       totnumhier    = totnumhier    + tempnumhier 
       totnumorient  = totnumorient  + tempnumorient
       totnumconf    = totnumconf    + tempnumconf
       totnumnode    = totnumnode    + tempnumnode
       totnumcomplex = totnumcomplex + tempnumcomplex
       totsecs       = totsecs       + tempsecs
       tothours      = tothours      + temphours 
       #print len(tot_dic_zinc_id.keys())
       #print "totsecs       =" + str(totsecs)

   print(("total_min_steps = " + str(totminsteps)))
   print(("total_num_hier  = " + str(totnumhier)))
   print(("tot_num_orient  = " + str(totnumorient)))
   print(("tot_num_conf    = " + str(totnumconf)))
   print(("tot_num_node    = " + str(totnumnode)))
   print(("tot_num_complex = " + str(totnumcomplex)))
   print(("total_secs      = " + str(totsecs)))
   print(("total_hours     = " + str(tothours)))
   print("===========")
   print(("total_docked    = " + str(len(list(tot_dic_zinc_id.keys())))))
   print(("total_scored    = " + str(len(list(tot_dic_zinc_id_scored.keys())))))
   print("=====no pose (some overlap with scored and one another) ======")
   print(("bump error          = " + str(len(tot_dic_zincid_error_bump))))
   print(("no_match error      = " + str(len(tot_dic_zincid_error_no_match))))
   print(("clash error         = " + str(len(tot_dic_zincid_error_clash))))
   print(("no_valid_pose error = " + str(len(tot_dic_zincid_error_no_valid))))
   print(("miscellaneous error = " + str(len(tot_dic_zincid_error_miss))))
   print(("skip error          = " + str(len(tot_dic_zincid_error_skip))))

   outfile1.close()
   outfile2.close()


main()

