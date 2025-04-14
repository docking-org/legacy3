#!/bin/tcsh
## Writen by Trent Balius in the Shoichet Group

set mol2file = $1 
set ifamsol  = $2

set list = `awk '/  Name:/{print $3}' $mol2file`
rm vdw.txt amsol.txt
touch vdw.txt amsol.txt

# (1) braekup mol2 file.  
# 
  #python /nfs/home/tbalius/zzz.scripts/separate_mol2_more10000.py $mol2file mol 
  python $DOCKBASE/docking/rescoring/separate_mol2_more10000.py $mol2file mol 
# foreach molecule
  foreach mol2 (`ls mol*.mol2`)
    set name = $mol2:r
    echo $mol2
    rm -r $name 
    mkdir $name
    cd $name
    cp ../$mol2 .

# (2) mape vdw parms on to the atomtypes
    #python /nfs/home/tbalius/zzz.scripts/mol2toDOCK37type.py $mol2 vdw.txt
    python $DOCKBASE/docking/rescoring/mol2toDOCK37type.py $mol2 vdw.txt
    #ls -lt | head

# (3) run amsol
    if ($ifamsol == 'amsol') then 
       csh /nfs/home/tbalius/zzz.github/DOCK/ligand/amsol/calc_solvation.csh $mol2
       awk 'BEGIN{count=0}{if(count>0){printf"%s %s %s %s\n", $2, $4, $5, $3}; count=count+1}' output.solv >! output.solv2
    else if ($ifamsol == 'noamsol') then
       echo "amsol is not calculated."
    else 
       echo "ERROR. . . "
       exit
    endif  
    cd ../
    echo "########$name########" >> vdw.txt
    cat $name/vdw.txt >> vdw.txt 

    #paste $name/vdw.txt $name/output.solv2 | awk '{printf"%2s %3s %-6s %5s %5s %5s %5s\n", $1, $2, $3, $5, $6, $7, $8}' >> amsol.txt
    if ($ifamsol == 'amsol') then
       echo "########$name########" >> amsol.txt
       paste $name/vdw.txt $name/output.solv2 | awk '{printf"%2s %3s %5s %5s %5s %5s\n", $1, $2, $5, $6, $7, $8}' >> amsol.txt
    else
       cat vdw.txt | awk '{if(NF==1){print $0} else if(NF==4){printf ("%2d %3s %5.2f %5.2f %5.2f %5.2f\n", $1, $2, 0.0,0.0,0.0,0.0)}}' >! amsol.txt 
    endif 
#
  end
