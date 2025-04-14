#! /bin/csh

# This script is written by Trent Balius, Shoichet lab in 2018. 
# modified by Reed Stein to call get_poses_blazing_faster.py, 2019
# This script has been modified by Jiankun Lyu, Shoichet lab in 2019.
# this script will get the top X lines for the extract_all.sort.uniq.txt, brack it up into files and run getposes_blazingfast.py on them in parallel. 

set file = extract_all_dirlist_combined.sort.uniq.txt
set fileprefix = extract_for_getposes_parallel
#set topX       = 100000
#set number_per_file = 5000
set topX            = $1
set number_per_file = $2
set docking_dir     = $3
#set topX       = "100"
#set number_per_file = "10"

#echo "I AM HERE"
echo "topX = $topX"
echo "number_per_file = $number_per_file"
echo "docking_dir = $docking_dir"


if ($topX < $number_per_file) then
   echo "$topX < $number_per_file"
   exit
endif


set pwd = `pwd`

cd $pwd

head -${topX} ${file} > ${fileprefix}_head.txt

echo "split --lines=${number_per_file} --suffix-length=6  ${fileprefix}_head.txt ${fileprefix}_split"

split --lines=${number_per_file} --suffix-length=6  ${fileprefix}_head.txt ${fileprefix}_split


foreach splitfile ( ` ls ${fileprefix}_split* ` ) 
echo ${splitfile}

# make sure that the link is pointing to something.  
#set lsoutput = `ls -l sgejob_*/${splitfile}.db2.gz`
#echo "WHAT:: $lsoutput"
#if ("$lsoutput" == "") then
#    rm ${splitfile}.db2.gz
#endif

if (-e "poses_${splitfile}.mol2") then
#   echo "I AM HERE(2)"
   echo "poses_${splitfile} has been generated" 
   continue
endif

#rm stdout_${splitfile} stderr_${splitfile} script_qsub_${splitfile}.csh 
#echo "I AM HERE(3)"

cat << EOF >! par_getposes_qsub_${splitfile}.csh
#\$ -S /bin/csh
#\$ -cwd
#\$ -q all.q
#\$ -o stdout_${splitfile}
#\$ -e stderr_${splitfile}

cd $pwd
hostname
date

#python $DOCKBASE/analysis/getposes_blazing_faster.py '' ${splitfile} ${number_per_file} poses_${splitfile}.mol2 test.mol2.gz
python $DOCKBASE/analysis/getposes_blazing_faster.py ${docking_dir} ${splitfile} ${number_per_file} poses_${splitfile}.mol2 test.mol2.gz

date

EOF

set name = `whoami`

#while ( `qstat -u $name | wc -l ` > 5 )
while ( `qstat -u $name | grep "par_getpos" | wc -l ` > 100 )
  sleep 10
end


qsub par_getposes_qsub_${splitfile}.csh

end
