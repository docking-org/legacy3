import os, sys

###
## written by Reed Stein
## re-written in blazing time by Reed Stein 4/2019


def main():

	pwd = os.getcwd()+"/"
	if len(sys.argv) != 4:
		print("python collect_mol2.py good_file pose_file mol_out_name")
		sys.exit()

	good_file = sys.argv[1]
	pose_file = sys.argv[2]
	mol_out_name = sys.argv[3]

	### read in GOOD POSE molecules, put them into dictionary
	open_good = open(good_file, 'r')
	read_good = open_good.readlines()
	open_good.close()
	
	good_dict = {line.strip().split()[0]:[] for line in read_good if len(line.strip().split()) > 0}
	print((len(good_dict)))

	### collect poses
	open_pose = open(pose_file, 'r')
        read_pose = open_pose.readlines()
        open_pose.close()

	line_num_list = [i for i in range(len(read_pose)) if (len(read_pose[i].strip().split()) > 1 and read_pose[i].strip().split()[1] == "Name:")]
	line_num_list.append(len(read_pose))

	output = open(mol_out_name, 'w')
	mol_count = 0
	repeat_list = []
	for j in range(len(line_num_list)-1):
		m0 = line_num_list[j]
		zinc_name = read_pose[m0].strip().split()[2]
		if zinc_name in good_dict:
			repeat_list.append(zinc_name)
			m1 = line_num_list[j+1]
			for k in range(m0, m1):
				output.write(read_pose[k])
			mol_count += 1

	output.close()

	print(("MOL COUNT = "+str(mol_count)))
	if mol_count != len(good_dict):
		for g in good_dict:
			if g not in repeat_list:
				print((g+" missing")) 
		 
main()
