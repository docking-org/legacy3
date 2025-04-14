#! /bin/csh

# This script is written by Trent Balius, Shoichet lab in 2018. 

# this script will brack up the dirlist into subdirlists

set fileprefix = dirlist
#extact_all_${fileprefix}_split*

set energy_cap = 0.0

ls -ltr extact_all_${fileprefix}_split*.sort.uniq.txt 

cat  extact_all_${fileprefix}_split*.sort.uniq.txt >! extact_all_${fileprefix}_combined.ori.txt 

echo " run python program $DOCKBASE/analysis/extract_all_blazing_fast_combine.py" 

python $DOCKBASE/analysis/extract_all_blazing_fast_parallel_combine.py extact_all_${fileprefix}_combined.ori.txt extact_all_${fileprefix}_combined.txt ${energy_cap}

