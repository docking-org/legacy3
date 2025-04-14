#!/bin/bash
USAGE="$0 [OPTIONS] [<REC_FILE> <XTAL_LIG_FILE>]
Positional Arguments:
	REC_FILE - Receptor PDB file [default: rec.pdb]
	XTAL_LIG_FILE - Crystal lig file [default: xtal-lig.pdb]
Parameters:
	-d, --working-dir - Working directory to do analysis in [default: ./xtal-pose-check]
"

set -e

export DOCKBASE="${DOCKBASE-$( dirname "$( dirname "$( readlink -f "$0" )" )" )}"

REC_FILE="${REC_FILE-rec.pdb}"
XTAL_LIG_FILE="${XTAL_LIG_FILE-xtal-lig.pdb}"
WORKING_DIR="${WORKING_DIR-./xtal-pose-check}"

POS=0
while [ "$#" -gt 0 ] ; do
	case "$1" in
		-d|--working-dir)
			WORKING_DIR="$2"
			shift 2
			;;
		*)
			POS=$(( $POS + 1 ))
			if [ "${POS}" == 1 ] ; then
				REC_FILE="$1"
				shift 1
			elif [ "${POS}" == 2 ] ; then
				XTAL_LIG_FILE="$1"
				shift 1
			else
				echo "Unexpected Argument $1 in position $POS!" 1>&2
				echo "${USAGE}" 1>&2
				exit -1
			fi
			
	esac
done

REC_FILE="$( readlink -f "${REC_FILE}" )"
XTAL_LIG_FILE="$( readlink -f "${XTAL_LIG_FILE}" )"
WORKING_DIR="$( readlink -f "${WORKING_DIR}" )"

mkdir -pv "${WORKING_DIR}"
pushd  "${WORKING_DIR}"
[ ! -e rec.pdb ] && cp -rv "${REC_FILE}" rec.pdb
[ ! -e xtal-lig.pdb ] && cp -rv "${XTAL_LIG_FILE}" xtal-lig.pdb
if [ ! -e dockfiles ] ; then
	echo "Preparing Receptor"
	$DOCKBASE/proteins/blastermaster/blastermaster.py -v
fi
if [ ! -e ligandfiles/finished ] ; then
	echo "Building xtal ligand"
	mkdir -pv ligandfiles
	pushd ligandfiles
	$DOCKBASE/ligand/generate/build_database_ligand.sh --debug --3d --single --name xtal-lig "${XTAL_LIG_FILE}"
	popd
fi
if [ ! -e noconf-ligandfiles/finished ] ; then
	echo "Building xtal ligand (No Sampling)"
	mkdir -pv noconf-ligandfiles
	pushd noconf-ligandfiles
	$DOCKBASE/ligand/generate/build_database_ligand.sh --no-conformations --3d --single --name noconf-xtal-lig "${XTAL_LIG_FILE}"
	popd
fi

if [ ! -e "test-xtal-ligand0" ] ; then
	echo "Running DB Setup"
	$DOCKBASE/docking/setup/setup_db2_lots.py 1 "test-xtal-ligand" "${WORKING_DIR}/ligandfiles/finished"
	mv dirlist dirlist.test
fi
if [ ! -e "check-xtal-ligand0" ] ; then
	echo "Running DB Setup"
	$DOCKBASE/docking/setup/setup_db2_lots.py 1 "check-xtal-ligand" "${WORKING_DIR}/noconf-ligandfiles/finished"
	mv dirlist dirlist.check
fi
cat dirlist.test dirlist.check > dirlist

for D in $( cat dirlist ); do
	pushd "$D"
	../dock.csh INDOCK
	tail OUTDOCK
	popd
done
