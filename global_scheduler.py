import json

def load_json(filename):
	with open(filename,'r') as f:
		tasks_dict=json.load(f)
	# n=len(tasks_dict.keys())
	# tasks=[task for task in tasks_dict.values()]
	return tasks_dict

def global_scheduler_assign_priority(tasks_dict):
	# taking out arrival times for each task from tasks_dict alon with tasks names
	tasks_arrival=[[k,v[2]] for k,v in tasks_dict.items()]
	# sorting the arrival times from least to highest
	tasks_arrival_sorted=list(sorted(tasks_arrival,key=lambda x:x[1]))
	# taking out the tasks names from the sorted list above for making them as dict keys 
	tasks_keys_sorted=[l[0] for l in tasks_arrival_sorted]
	# taking out the tasks data for each key in the above sorted list
	tasks_values=[tasks_dict[k] for k in tasks_keys_sorted]
	# combining the key value pairs to form a dict that is to be returned for spliting into n processors
	tasks_dict_sorted=dict(zip(tasks_keys_sorted,tasks_values))
	return tasks_dict_sorted

def divide_tasks_in_processor(n_processor,tasks_dict):
	# taking out the names of tasks from dict
	tasks_names=[k for k in tasks_dict.keys()]
	# initializing the processor queues for each processor basis the given number of processors
	processor_queue={"Processor%d"%r:{} for r in range(n_processor)}
	# initializing the division list which will contain groups of tasks that are sliced below
	division=[]
	# slice the tasks in n_processor/len(tasks) groups each containing n_processor number of entries 
	i=0
	while i+n_processor<=len(tasks_names):
		div_temp=list(tasks_names[i:i+n_processor])
		division.append(div_temp)
		i=i+n_processor
	# assigning the tasks in groups to processor 
	for task_list in division:
		for p in range(n_processor):
			processor_queue["Processor%d"%p][task_list[p]]=tasks_dict[task_list[p]]
	return processor_queue

# def main_gs_init(filename,n_processor):
# 	# loading json into dict
# 	tasks,tasks_dict,n=load_json(filename)
# 	# sorting the tasks on first come first serve basis
# 	tasks_dict_sorted=global_scheduler_assign_priority(tasks_dict)
# 	# divinding the tasks onto each processor
# 	processor_queue=divide_tasks_in_processor(n_processor,tasks_dict_sorted)
# 	return processor_queue

def main_gs(tasks_dict,n_processor):
	# sorting the tasks on first come first serve basis
	tasks_dict_sorted=global_scheduler_assign_priority(tasks_dict)
	# divinding the tasks onto each processor
	processor_queue=divide_tasks_in_processor(n_processor,tasks_dict_sorted)
	return processor_queue


