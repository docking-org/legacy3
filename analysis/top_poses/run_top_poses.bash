#!/bin/bash
#$ -pe smp 8
#$ -l mem_free=2G

in=$1
out=$2
args=${@:3}

NSLOTS=${NSLOTS-8}

ncores=$(($NSLOTS-1))
tmploc=/scratch/${JOB_ID}_${SGE_TASK_ID}_poses

args="$in $args -o $tmploc -j $ncores"

echo $(hostname)
echo $(date)
echo $(whoami)
echo $ncores

# working directory should be set to the location of this script, which is expected to contain a (link to) a python3.8 executable
./python3.8 top_poses.py $args

mv ${tmploc}.mol2.gz ${out}.mol2.gz
mv ${tmploc}.scores ${out}.scores
