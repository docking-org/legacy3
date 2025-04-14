#!/bin/csh -f

if ( $#argv != 1 ) then
    echo
    echo "Setup docking directories."
    echo
    echo "usage: setup_db2.csh <db_dir>"
    echo
    echo "db_dir: contains all the *.db2.gz input flexibases"
    echo
    exit 1
endif

/bin/ls -1d $1/*.db2.gz | sed -e "s#^$1/##" -e 's#.db2.gz$##' >! dirlist
foreach i ( `cat dirlist` )
    echo $i
    if ( -e $i ) /bin/rm -rf $i
    /bin/mkdir $i
    ln -s ../INDOCK $i/INDOCK
    echo $1/$i.db2.gz > $i/split_database_index
end

