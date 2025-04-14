import os, sys

###
## written by Reed Stein
## re-written in blazing time again by Reed Stein 2/2020
'''            (  .      )
        )           (              )
              .  '   .   '  .  '  .
     (    , )       (.   )  (   ',    )
      .' ) ( . )    ,  ( ,     )   ( .
   ). , ( .   (  ) ( , ')  .' (  ,    )
  (_,) . ), ) _) _,')  (, ) '. )  ,. (' )
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ '''
## A script for collecting a subset of mol2 files from a larger mol2 file given
## a list of compound IDs, outputting them in the order of the compound list


def main():

	pwd = os.getcwd()+"/"
	if len(sys.argv) != 4:
		print("python collect_mol2.py good_file pose_file mol_out_name")
		sys.exit()

	good_file = sys.argv[1]
	pose_file = sys.argv[2]
	mol_out_name = sys.argv[3]

	### read in GOOD POSE molecules, put them into list so order is maintained
	open_good = open(good_file, 'r')
	read_good = open_good.readlines()
	open_good.close()
	
	good_list = [line.strip().split()[0] for line in read_good if len(line.strip().split()) > 0]

	### collect poses
	open_pose = open(pose_file, 'r')
	read_pose = open_pose.readlines()
	open_pose.close()

	line_num_list = [i for i in range(len(read_pose)) if (len(read_pose[i].strip().split()) > 1 and read_pose[i].strip().split()[1] == "Name:")]
	line_num_list.append(len(read_pose))

	### get the index pairs [start:end] of the mol2 file for molecules in good_list
	pair_dict = {read_pose[line_num_list[i]].strip().split()[2]:[line_num_list[i], line_num_list[i+1]] for i in range(len(line_num_list)-1) if read_pose[line_num_list[i]].strip().split()[2] in good_list}

	output = open(mol_out_name+".mol2", 'w')
	mol_count = 0
	missing_count = 0
	repeat_dict = {}
	for g in good_list:
		if g not in pair_dict:
			print((g+" not found in pose file."))
			missing_count += 1
			continue
		if g not in repeat_dict:
			mol_count += 1
			repeat_dict[g] = []
			idx_i, idx_j = pair_dict[g][0], pair_dict[g][1]
			#print(idx_i)
			#print(idx_j)
		
			for line in read_pose[idx_i:idx_j]:
				output.write(line)
	output.close()

	print(("MOL COUNT:", mol_count))
	print(("Missing count:", missing_count))


main()
