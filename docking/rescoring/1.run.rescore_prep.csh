#!/bin/tcsh
## Writen by Trent Balius in the Shoichet Group
#rm poses.mol2.gz vdw.txt.gz amsol.txt.gz
#
#zcat test.mol2.gz >! poses.mol2

set ligs_mol2 = $1


#if $ligs_mol2:e == 'gz' then
#   echo $ligs_mol2 $ligs_mol2:r $ligs_mol2:e 

cp $ligs_mol2 poses.mol2

csh 2.rescore_get_parms_rerun_mod.csh poses.mol2 noamsol
#csh 2.rescore_get_parms_rerun_mod.csh poses.mol2 amsol
gzip -f poses.mol2
gzip -f vdw.txt
gzip -f amsol.txt
