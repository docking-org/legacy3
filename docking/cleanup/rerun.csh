#$ -S /bin/csh
#$ -cwd
#$ -j yes
#$ -o stderr
#$ -v DOCKBASE
#$ -q all.q

if ( $#argv > 1 ) then
    echo
    echo "Run a dock job for this subdirectory"
    echo
    echo "usage: runsingle.csh [optional: path/to/dock_executable]"
    echo
    exit 1
endif

# set dock location
if ( $#argv > 0 ) then
    set dock = "$1"
else
    set dock = "$DOCKBASE/docking/DOCK/bin/dock.csh"
endif

if ( ! -x "$dock" ) then
    echo "Error: Cannot find DOCK executable $dock!"
    echo "Exiting!"
    exit 1
endif

"$dock"
exit $status
