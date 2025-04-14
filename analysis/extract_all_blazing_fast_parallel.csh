#! /bin/csh

# This script is written by Trent Balius, Shoichet lab in 2018. 

# this script will brack up the dirlist into subdirlists

set file = dirlist
set fileprefix = dirlist
#set number_per_dirlist = 10000
set number_per_dirlist = 1000
#set energy_cap         = 1000.0
#set energy_cap         = -30.0
set energy_cap         = 0.0

set pwd = `pwd`

cd $pwd

#ln -s ../${file} .

if !($?TMPDIR) then 
  echo "define TMPDIR in ~/.cshrc or equivalent. "
  exit
endif

echo "split --lines=$number_per_dirlist --suffix-length=6  ${file} ${fileprefix}_split"

split --lines=$number_per_dirlist --suffix-length=6  ${file} ${fileprefix}_split


foreach splitfile ( ` ls ${fileprefix}_split* ` ) 
echo ${splitfile}

# make sure that the link is pointing to something.  
#set lsoutput = `ls -l sgejob_*/${splitfile}.db2.gz`
#echo "WHAT:: $lsoutput"
#if ("$lsoutput" == "") then
#    rm ${splitfile}.db2.gz
#endif

if (-e extact_all_${splitfile}.txt) then
#   echo "I AM HERE(2)"
   echo "${splitfile} has been submited extact_all generation" 
   continue
endif


#rm stdout_${splitfile} stderr_${splitfile} script_qsub_${splitfile}.csh 
#echo "I AM HERE(3)"

#\$ -S /bin/csh
#\$ -cwd
#\$ -q all.q
#if ! (\$?TMPDIR) then 
#  echo "OhOh.  TMPDIR is not defined. "
#  exit
#endif
#mkdir -p \$TMPDIR

cat << EOF >! script_qsub_${splitfile}.csh
#\$ -S /bin/csh
#\$ -cwd
#\$ -q jk.q
#\$ -P extract_parallel
#\$ -o stdout_${splitfile}
#\$ -e stderr_${splitfile}

cd $pwd
hostname
date

if ! (\$?TMPDIR) then 
  echo "OhOh.  TMPDIR is not defined. "
  exit
endif

mkdir -p \$TMPDIR

python $DOCKBASE/analysis/extract_all_blazing_fast.py ${splitfile} extact_all_${splitfile}.txt ${energy_cap}

date

EOF

#echo "I AM HERE"
set name = `whoami`

# this is not needed because of extract_parallel group
#while ( `qstat -u $name | wc -l ` > 5 )
#  sleep 10
#end

qsub script_qsub_${splitfile}.csh

end
