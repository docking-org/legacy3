#!/bin/bash

#BINDIR=$(dirname $0)
#BINDIR=${BINDIR-.}

INPUT=$1
STAGING=$2
#BATCH_SIZE=${3-1000}
BATCH_SIZE=${BATCH_SIZE-1000}
ARGS=${@:3}


if [ -f $STAGING/batch_size ] && [ $(cat $STAGING/batch_size) -ne $BATCH_SIZE ]; then
	echo "batch size from previous run not compatible with batch size for this run!"
	echo "prev: " $(cat $STAGING/batch_size) ", curr" $BATCH_SIZE
	return
fi

echo $BATCH_SIZE > $STAGING/batch_size

mkdir -p $STAGING

STAGING_INPUT_ALL=$STAGING/input_all

if [ -d $INPUT ]; then
	if [ -z $FIND_POSES_ARGS ]; then
		find $INPUT -type f -name 'test.mol2.gz*' > $STAGING_INPUT_ALL
	else
		find $INPUT $FIND_POSES_ARGS > $STAGING_INPUT_ALL
	fi
else
	ln -s $INPUT $STAGING_INPUT_ALL
fi

STAGING_INPUT_SPLIT=$STAGING/input
mkdir -p $STAGING_INPUT_SPLIT
mkdir -p $STAGING/output
mkdir -p $STAGING/log

split --lines=$BATCH_SIZE $STAGING_INPUT_ALL $STAGING_INPUT_SPLIT/

ALL_POSES=$STAGING/output_final.poses.mol2.gz
ALL_OUTPUT=$STAGING/output_all

[ -f $ALL_OUTPUT ] && rm $ALL_OUTPUT
[ -f $ALL_POSES ] && echo $ALL_POSES >> $ALL_OUTPUT

for split_file in $(ls $STAGING_INPUT_SPLIT/*); do
	echo $split_file
	STAGING_OUTPUT=$STAGING/output/$(basename $split_file).poses
	# if this job has already run before
	if [ -f ${STAGING_OUTPUT}.mol2.gz ] && [ -f $ALL_OUTPUT ]; then
		continue
	fi
	echo ${STAGING_OUTPUT}.mol2.gz >> $ALL_OUTPUT

	jobid=$(qsub -terse -e $STAGING/log/$(basename $split_file).err -o $STAGING/log/$(basename $split_file).log -wd $PWD run_top_poses.bash $split_file $STAGING_OUTPUT $ARGS)
	echo $jobid
	#echo $jobid >> $ALL_JOBIDS
	[ -z $ALL_JOBIDS ] && ALL_JOBIDS=$jobid || ALL_JOBIDS=$ALL_JOBIDS,$jobid
done

prev_attempts=$(ls $STAGING/jobids_worker* | wc -l)
echo $ALL_JOBIDS > $STAGING/jobids_worker_$prev_attempts

# final job will combine all outputs from other jobs into a final top poses list
jobid=$(qsub -terse -wd $PWD -hold_jid $ALL_JOBIDS -e $STAGING/log/all.err -o $STAGING/log/all.out run_top_poses.bash $ALL_OUTPUT $STAGING/output_final.poses $ARGS)

echo $jobid > $STAGING/jobid_final_$prev_attempts
