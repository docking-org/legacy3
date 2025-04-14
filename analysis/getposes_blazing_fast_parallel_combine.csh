#! /bin/csh

# This script is written by Trent Balius, Shoichet lab in 2018. 

# this script will brack up the dirlist into subdirlists

set fileprefix = extract_for_getposes_parallel
#extact_all_${fileprefix}_split*

set energy_cap = 0.0

ls -ltr poses_${fileprefix}_split*.mol2 

cat poses_${fileprefix}_split*.mol2 >! poses_${fileprefix}_combined.ori.mol2 


echo " run python program $DOCKBASE/analysis/get_mol2_zinc_id_head.py to sort the mol2 file as follows" 
echo " \n   awk '{print $3}' ${fileprefix}_head.txt > ${fileprefix}_head_zincid.txt \n python $DOCKBASE/analysis/get_mol2_zinc_id_head.py poses_${fileprefix}_combined.ori.mol2 ${fileprefix}_head_zincid.txt poses_${fileprefix}_combined.sort.mol2
"
