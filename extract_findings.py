import os
import pandas as pd
import json
# custom dependency
import global_scheduler as gs

def save_as_json(dicts,filename):
	task_dump=json.dumps(dicts, indent=5)
	with open(filename,'w') as f:
		f.write(task_dump)

def extract_ratios(sim_file,tasks_file):
	# load the json task file
	tasks=gs.load_json(tasks_file)
	# load the sim_file in dataframe
	df=pd.read_csv(sim_file,header=None)
	# load the second column as a list of sim array
	sim_arr=df[1].to_list()
	# filter the sim_arr and create a tasks list to include just the unique tasks names
	tasks_list=set([x for x in sim_arr if x!='idle']) 
	# extract occurances
	occ={task:[] for task in tasks_list}
	for index,task in enumerate(sim_arr):
		if (task!='idle') and (index not in occ[task]):
			occ[task].append(index)
	# save the occurances in json
	save_as_json(occ,"results_calc/occ_"+sim_file[11:-15]+"_"+sim_file[-14:-4]+".json")
	# init ratios
	success=0
	fails=0
	# calc ratios
	for task in tasks_list:
		d=tasks[task][3]
		e=tasks[task][0]
		temp_occ=list(filter(lambda x:x<d,occ[task]))
		if len(temp_occ)>=e:
			success+=1
		else:
			fails+=1
	# return
	return success/len(tasks_list),fails/len(tasks_list)

def get_files(path):
	list_of_files = []
	for root, dirs, files in os.walk(path):
		for file in files:
			if file[-4:-1]=='.cs':
				list_of_files.append(path+"/"+file)
	return list_of_files

def temp(sim_file,tasks_file):
	tasks=gs.load_json(tasks_file)
	# load the sim_file in dataframe
	df=pd.read_csv(sim_file,header=None)
	# load the second column as a list of sim array
	sim_arr=df[1].to_list()
	# filter the sim_arr and create a tasks list to include just the unique tasks names
	tasks_list=set([x for x in sim_arr if x!='idle']) 
	return len(tasks_list)

files=get_files("simulation/rm_grid_400_4t_555408")

d={"P":[],"le":[]}
for fi in files:
	l=temp(fi,"gen_tasks/tasks_dump_400_4t_555408.json")
	d["P"].append(fi[-14:-4])
	d["le"].append(l)
print(d)
# df_dict={"Processor":[] ,"Sucess Ratio":[],"Failure Ratio":[]}

# for fi in files:
# 	s,f=extract_ratios(fi,"gen_tasks/tasks_dump_400_4t_555408.json")
# 	df_dict["Processor"].append(fi[-14:-4])
# 	df_dict["Sucess Ratio"].append(s)
# 	df_dict["Failure Ratio"].append(f)
# df=pd.DataFrame(df_dict)
# df.to_csv("results_calc/res_rm_grid_400_4t_555408.csv")