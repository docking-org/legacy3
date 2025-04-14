import sys, mol2

## Writen by Trent Balius in the Shoichet Group
## converts a mol2 sybyl atom types to dock3.7 vdw atom types. 

def main():
  if len(sys.argv) != 3: # if no input
     print("ERORR")
     return
  namemol2 = sys.argv[1]
  namedocktype = sys.argv[2]
  file = open(namedocktype,'w')
  mol  = mol2.read_Mol2_file(namemol2)[0]
  dt   = mol2.convert_sybyl_to_dock(mol)
  for i in range(len(mol.atom_list)):
      print((i+1, mol.atom_list[i].type, dt[i]))
      file.write('%2d %4s %-6s %2s\n' % (i+1, mol.atom_list[i].name, mol.atom_list[i].type, dt[i]))
main()


