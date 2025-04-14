#$ -S /bin/bash
#$ -cwd
#$ -q !gpu.q
#$ -N rundock
#$ -o /dev/shm
#$ -e /dev/shm
 
# req:
# EXPORT_DEST
# INPUT_SOURCE
# DOCKFILES
# DOCKEXEC
# SHRTCACHE
# LONGCACHE
# JOB_ID
# SGE_TASK_ID

function log {
	echo "[$(date +%X)]: $@"
}

if [ -z $SHRTCACHE_USE_ENV ]; then
	SHRTCACHE=${SHRTCACHE-/dev/shm}
else
	SHRTCACHE=${!SHRTCACHE_USE_ENV}
fi
LONGCACHE=${LONGCACHE-/scratch}

log host=$(hostname)
log user=$(whoami)
log SGE_TASK_ID=$SGE_TASK_ID
log JOB_ID=$JOB_ID
log EXPORT_DEST=$EXPORT_DEST

# initialize all our important variables & directories
JOB_DIR=${SHRTCACHE}/$(whoami)/${JOB_ID}_${SGE_TASK_ID}
INPUT_TARBALL=$(sed "${SGE_TASK_ID}q;d" $EXPORT_DEST/joblist | awk '{print $1}')
EXTRACT_DIR=$JOB_DIR/input/$(basename $INPUT_TARBALL)
COMMON_DIR=${LONGCACHE}/DOCK_common

log JOB_DIR=$JOB_DIR
log INPUT_TARBALL=$INPUT_TARBALL
log EXTRACT_DIR=$EXTRACT_DIR
log COMMON_DIR=$COMMON_DIR

# this is all to make sure the common directory is public writable
# if the common directory exists and is not publicly writable, either fix it or create a temp common directory for this job

if ! [ -f $DOCKFILES/.shasum ]; then
	dockfileshash=$(cat $DOCKFILES/* | sha1sum | awk '{print $1}')
	[ -w $DOCKFILES ] && echo $dockfileshash > $DOCKFILES/.shasum
else
	dockfileshash=$(cat $DOCKFILES/.shasum)
fi

if [ -d $COMMON_DIR ]; then
	common_owner=$(ls -ld $COMMON_DIR | awk '{print $3}')
	common_perms=$(find $COMMON_DIR -maxdepth 0 -printf "%m")
	dockfiles_lock_owner=$(ls -ld /dev/shm/dockfiles.${dockfileshash}.lock 2>/dev/null | awk '{print $3}')
	dockfiles_lock_perms=$(find /dev/shm/dockfiles.${dockfileshash}.lock -printf "%m" 2>/dev/null)

	if [ -d $COMMON_DIR ] && ! [ -w $COMMON_DIR ]; then
		cnd1="true"
		log "common files are not common! owned by $common_owner, set to permissions $common_perms"
	fi
	if [ -f "/dev/shm/dockfiles.${dockfileshash}.lock" ] && ! [ -w "/dev/shm/dockfiles.${dockfileshash}.lock" ]; then
		cnd2="true"
		log "dockfiles lock is not common! owned by $dockfiles_lock_owner, set to permissions $dockfiles_lock_perms"
	fi

	if ! [ -z $cnd1 ] || ! [ -z $cnd2 ]; then
		log "going to store dockfiles in temporary location this run"
		COMMON_DIR=${LONGCACHE}/DOCK_common_$(whoami)_${JOB_ID}_${SGE_TASK_ID}
		REMOVE_COMMON=TRUE
		mkdir -p $COMMON_DIR
		else
		if [ "$common_owner" = "$(whoami)" ] && ! [ "$common_perms" = "777" ]; then
					chmod 777 $COMMON_DIR
		fi
		# made an oopsie with the code, need to make sure locks are accessible by any user
		if [ -O "/dev/shm/dockfiles.${dockfileshash}.lock" ] && ! [ "$dockfiles_lock_perms" = "777" ]; then
			chmod 777 /dev/shm/dockfiles.${dockfileshash}.lock
		fi
	fi
else
    mkdir -p $COMMON_DIR
	chmod 777 $COMMON_DIR
fi

DOCKFILES_COMMON=$COMMON_DIR/dockfiles.$dockfileshash

OUTPUT=${EXPORT_DEST}/$(sed "${SGE_TASK_ID}q;d" $EXPORT_DEST/joblist | awk '{print $2}')
LOG_OUT=/dev/shm/rundock.o${JOB_ID}.${SGE_TASK_ID}
LOG_ERR=/dev/shm/rundock.e${JOB_ID}.${SGE_TASK_ID}

# bring directories into existence
mkdir -p $OUTPUT
mkdir -p $JOB_DIR/working
mkdir -p $EXTRACT_DIR

# failsafe: delete old jobs that failed to delete themselves
#n_old_jobs=$(find $SHRTCACHE/$(whoami) -maxdepth 1 -type d -mmin +240 | wc -l) # job directories older than 4 hours old to be removed
#if [ $n_old_jobs -gt 0 ]; then
(
	flock -x 9
	find $SHRTCACHE/$(whoami) -maxdepth 1 -type d -mmin +360 | xargs rm -r 2>/dev/null
	flock -u 9
)9>/dev/shm/rundock_purge_$(whoami).lock
#	synchronize_all_but_first "purge_old" "find $SHRTCACHE/$(whoami) -maxdepth 1 -type d -mmin +240 | xargs rm -r"
#fi

# synchronize copying of dockfiles/executable over, if necessary
if [ -z $REMOVE_COMMON ]; then
	(
		flock -x 9
		if ! [ -f $DOCKFILES_COMMON/INDOCK ]; then
			[ -d $DOCKFILES_COMMON ] && rm -r $DOCKFILES_COMMON
			cp -L -r $DOCKFILES $DOCKFILES_COMMON
		fi
		flock -u 9
	)9>/dev/shm/dockfiles.${dockfileshash}.lock
			
else
	cp -L -r $DOCKFILES $DOCKFILES_COMMON
fi

log "starting input extract"
tar -C $EXTRACT_DIR -xzf $INPUT_TARBALL
log "ending input extract"
#ln -s $DOCKFILES_COMMON $JOB_DIR/dockfiles > /dev/null 2>&1
mkdir $JOB_DIR/dockfiles
for f in $DOCKFILES_COMMON/*; do
	ln -s $f $JOB_DIR/dockfiles/$(basename $f) 
done
rm $JOB_DIR/dockfiles/INDOCK
find $EXTRACT_DIR -name '*.db2*' | sort > $JOB_DIR/working/split_database_index

# tells this script to ignore SIGUSR1 interrupts
#trap '' SIGUSR1

if [ -f $OUTPUT/restart ]; then
	cp $OUTPUT/restart $JOB_DIR/working/restart
fi

function fix_indock {
	in=$1
	out=$2
	if [ -f $out ]; then
		rm $out
	fi

	while read -r line; do
		isfileline=$(echo $line | grep _file | awk '{print $1}')

		if ! [ -z $isfileline ] && ! [ $isfileline = "ligand_atom_file" ] && ! [ $isfileline = "output_file_prefix" ]; then
			label=$(echo $line | awk '{print $1}')
			filepath=$(echo $line | awk '{print $2}')
			filename=$(basename $filepath)
			basepath=""
			while ! [[ "$(basename $filepath)" == dockfiles* ]] && ! [ $(basename $filepath) = . ]; do
				[ -z $basepath ] && basepath=$(basename $filepath) || basepath=$(basename $filepath)/$basepath
				filepath=$(dirname $filepath)
			done
			if [ $(basename $filepath) = . ]; then
				# if the file path does not include some variation of "dockfiles", then we leave it as is
				basepath=$(echo $line | awk '{print $2}')
			else
				basepath=../dockfiles/$basepath
			fi
			labelcharc=$(printf $label | wc -c)
			nspaces=$((30-labelcharc))
			spaces=$(printf %-${nspaces}s " ")
			echo -e "$label$spaces$basepath" >> $out
		else
			echo "$line" >> $out
		fi
			
	done < $in
}

# only need to fix the INDOCK file once- don't want jobs to go all nutty because multiple processes are trying to mess with the INDOCK file
#(
#	flock -x 9
fix_indock $DOCKFILES_COMMON/INDOCK $JOB_DIR/dockfiles/INDOCK
#        flock -u 9
#)9>/dev/shm/dockfiles.${dockfileshash}.lock

log "starting dock"
pushd $JOB_DIR/working > /dev/null 2>&1
$DOCKEXEC ../dockfiles/INDOCK &
dockpid=$!

function notify_dock {
	echo "notifying dock!"
	kill -10 $dockpid
}

trap notify_dock SIGUSR1

wait $dockpid
sleep 5 # bash script seems to jump the gun and start cleanup prematurely when DOCK is interrupted. This is stupid but effective at preventing this

# don't feel like editing DOCK src to change the exit code generated on interrupt, instead grep OUTDOCK for the telltale message
sigusr1=`tail OUTDOCK | grep "interrupt signal detected since last ligand- initiating clean exit & save" | wc -l`

log "finished! cleaning up"

# cleanup will:
# 1. remove extracted tarfiles
# 2. move results/restart marker to $OUTPUT (if no restart marker, remove it from $OUTPUT if present)
# 3. move logs to $OUTPUT
# 4. remove the working directory
function cleanup {
	rm -r $EXTRACT_DIR

	nout=$(ls $OUTPUT | grep OUTDOCK | wc -l)

	if [ $nout -ne 0 ] && ! [ -f $OUTPUT/restart ]; then
		log "Something seems wrong, my output is already full but has no restart marker. Removing items present in output and replacing with my results."
		rm $OUTPUT/*
		nout=0
		nlog=0
	fi

	mv $JOB_DIR/working/OUTDOCK $OUTPUT/OUTDOCK.$nout
	mv $JOB_DIR/working/test.mol2.gz $OUTPUT/test.mol2.gz.$nout

	mv $LOG_OUT $OUTPUT/$nout.out
	mv $LOG_ERR $OUTPUT/$nout.err

	if [ -f $JOB_DIR/working/restart ]; then
		mv $JOB_DIR/working/restart $OUTPUT/restart
	elif [ -f $OUTPUT/restart ]; then
		rm $OUTPUT/restart
	fi
	if ! [ -z $REMOVE_COMMON ]; then
		rm -r $COMMON_DIR
	fi
	rm -r $JOB_DIR
}

popd > /dev/null 2>&1

if [ $sigusr1 -ne 0 ]; then
	echo "s_rt limit reached!"
	[ -z $SKIP_CLEANUP ] && cleanup
	exit 0
	#exit 99
else
	[ -z $SKIP_CLEANUP ] && cleanup
	exit 0
fi

