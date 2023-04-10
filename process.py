# importing the custom dependencies
import global_scheduler as gs
import edf_fin as edf
import rm
import gen_network as gn
# importing the multiprocessing dependencies
import multiprocessing as mp
import concurrent.futures as cf
import pandas as pd 
import json

def calc_feasibility(tasks_dict,algo):
	if algo=='rm':
		res=rm.check_schedulability(tasks_dict)
	if algo=='edf':
		res=edf.check_schedulability(tasks_dict)
	return res

def compile_feasibility_values(Q,algo):
	processor_wise_load={}
	for proc in Q.keys():
		res=calc_feasibility(Q[proc],algo)
		processor_wise_load[proc]=res
	return processor_wise_load


def init_processor(n_processor,spc_t_dict):
	p_dict={}
	for r in range(n_processor):
		p_dict['Processor%d'%r]={'spc':spc_t_dict['Processor%d'%r]['spc'],'t':spc_t_dict['Processor%d'%r]['t'],'status':'unlocked'}
	return p_dict

def local_scheduler(q,name,load_dict,avbl_proc,algo):
	avbl_load=avbl_proc.copy()
	if avbl_load:
		overloaded_tasks={}
		if algo=='rm':
			res=rm.check_schedulability(q[name])
			while res[1]>res[2]:
				# calc the min priority task
				min_priority=min(q[name].values(),key=lambda x:x[1])
				for task_name,task_value in q[name].items():
					if task_value==min_priority:
						min_priority_task=task_name
				# calc the min U (least loaded processor)
				min_U=min(avbl_load.values(),key=lambda x:x[1])
				for processor_name,load in avbl_load.items():
					if load==min_U:
						min_U_processor=processor_name
				# placing the min priority task in the least loaded processor in the Q
				min_U_proc_dict=q[min_U_processor]
				min_U_proc_dict[min_priority_task]=q[name][min_priority_task]
				q[min_U_processor]=min_U_proc_dict
				# placing the min priority task in the overloaded tasks dict
				overloaded_tasks[min_priority_task]=q[name][min_priority_task]
				# deleting the min priority task from the current processor Q
				curr_proc=q[name]
				del curr_proc[min_priority_task]
				q[name]=curr_proc
				# updating the load_dict
				l=compile_feasibility_values(q,algo)
				for proc in l.keys():
					load_dict[proc]=l[proc]
				# updating the avbl_load dict
				avbl_load={k:load_dict[k] for k in avbl_load.keys()}
				# updating the res value
				res=rm.check_schedulability(q[name])
		if algo=='edf':
			res=edf.check_schedulability(q[name])
			while res[1]>float(1):
				# calc the min priority task
				min_priority=min(q[name].values(),key=lambda x:x[3])
				for task_name,task_value in q[name].items():
					if task_value==min_priority:
						min_priority_task=task_name
				# calc the min U (least loaded processor)
				min_U=min(avbl_load.values(),key=lambda x:x[1])
				for processor_name,load in avbl_load.items():
					if load==min_U:
						min_U_processor=processor_name
				# placing the min priority task in the least loaded processor in the Q
				min_U_proc_dict=q[min_U_processor]
				min_U_proc_dict[min_priority_task]=q[name][min_priority_task]
				q[min_U_processor]=min_U_proc_dict
				# placing the min priority task in the overloaded tasks dict
				overloaded_tasks[min_priority_task]=q[name][min_priority_task]
				# deleting the min priority task from the current processor Q
				curr_proc=q[name]
				del curr_proc[min_priority_task]
				q[name]=curr_proc
				# updating the load_dict
				l=compile_feasibility_values(q,algo)
				for proc in l.keys():
					load_dict[proc]=l[proc]
				# updating the avbl_load dict
				avbl_load={k:load_dict[k] for k in avbl_load.keys()}
				# updating the res value
				res=edf.check_schedulability(q[name])
	return overloaded_tasks

def init_process(proc_dict,q,load_dict,name,algo,task_list,conn):
	if q[name]:
		# locking the processor
		proc_dict[name]={'spc':proc_dict[name]['spc'],'t':proc_dict[name]['t'],'status':'locked'}
		print(name)
		# calculating unlocked processors for possible migration by local scheduler
		unlocked_proc={}
		for proc_name,proc_load in load_dict.items():
			if proc_dict[proc_name]['status']=='unlocked':
				unlocked_proc[proc_name]=proc_load
		# calculating the avbl processors for local scheduler migration given by the network connections
		avbl_proc={proc:unlocked_proc[proc] for proc in unlocked_proc.keys() if proc in conn[name]}
		# call the local scheduler
		overloaded_tasks=local_scheduler(q,name,load_dict,avbl_proc,algo)
		# save the initial data of migrated tasks
		df_migrated=pd.DataFrame({"Processor":name,"# Migrated Tasks":[len(overloaded_tasks)]})
		df_migrated.to_csv("migrated/"+name+".csv",mode='a',index=False)
		# save load in csv
		col_proc=[x for x in load_dict.keys()]
		col_U=[load_dict[x] for x in load_dict.keys()]
		df_load=pd.DataFrame({"Processor":col_proc,"U":col_U,"Algo":[algo for r in range(len(col_proc))]})
		df_load.to_csv("util/"+name+".csv",mode='a',index=False)
		# simulate
		if algo=='rm':
			# calc hp
			hp=rm.calc_hyperperiod(q[name])
			# check if the hp & task length is ok for the processor
			if (proc_dict[name]["t"]>=hp) and (proc_dict[name]["spc"]>=len(q[name].keys())):
				# call the main rm function
				results_dict=rm.main_rm(q[name])
				# save the simulation in df & csv
				df_sim=pd.DataFrame({"Processor":[name for r in range(hp)],"Simulation":results_dict["Simulation"],"Algo":[algo for r in range(hp)]})
				df_sim.to_csv("simulation/"+name+".csv",mode='a',header=False,index=False)
				# update the tasks_list (delete the scheduled tasks)
				for t_name in q[name].keys():
					if t_name in task_list:
						task_list.remove(t_name)
				# delete the scheduled tasks from Q
				current_proc_dict=q[name]
				for task_name in q[name].keys():
					if task_name in current_proc_dict:
						del current_proc_dict[task_name]
				q[name]=current_proc_dict
				# recalculate the load_dict
				l=compile_feasibility_values(q,algo)
				for p in l.keys():
					load_dict[p]=l[p]
				# unlock the processor
				proc_dict[name]={'spc':proc_dict[name]['spc'],'t':proc_dict[name]['t'],'status':'unlocked'}
		if algo=='edf':
			# calc hp
			hp=edf.calc_hyperperiod(q[name])
			# check if the hp & task length is ok for the processor
			if (proc_dict[name]["t"]>=hp) and (proc_dict[name]["spc"]>=len(q[name].keys())):
				# call the main edf function
				results_dict=edf.main_edf(q[name])
				# save the simulation in df & csv
				df_sim=pd.DataFrame({"Processor":[name for r in range(hp)],"Simulation":results_dict["Simulation"],"Algo":[algo for r in range(hp)]})
				df_sim.to_csv("simulation/"+name+".csv",mode='a',header=False,index=False)
				# update the tasks_list (delete the scheduled tasks)
				for t_name in q[name].keys():
					if t_name in task_list:
						task_list.remove(t_name)
				# delete the scheduled tasks from Q
				current_proc_dict=q[name]
				for task_name in q[name].keys():
					if task_name in current_proc_dict:
						del current_proc_dict[task_name]
				q[name]=current_proc_dict
				# recalculate the load_dict
				l=compile_feasibility_values(q,algo)
				for p in l.keys():
					load_dict[p]=l[p]
				# unlock the processor
				proc_dict[name]={'spc':proc_dict[name]['spc'],'t':proc_dict[name]['t'],'status':'unlocked'}


def exe(n_processor,algo,spc_t_dict,filename,net_file):
	manager=mp.Manager()
	task_dict_loaded=gs.load_json(filename)
	proc_dict=manager.dict(init_processor(n_processor,spc_t_dict))
	q=manager.dict(gs.main_gs(task_dict_loaded,n_processor))
	load_dict=manager.dict(compile_feasibility_values(q,algo))
	task_list=manager.list([x for x in task_dict_loaded.keys()])
	conn=gn.read_net(net_file)

	with cf.ProcessPoolExecutor() as exe:
		# //main 
		while len(task_list)>0:
			res=[exe.submit(init_process,proc_dict,q,load_dict,processor_name,algo,task_list,conn) for processor_name in q.keys() if bool(q[processor_name])==True]
			for p in cf.as_completed(res):
				p.result()
		# main//

if __name__=='__main__':
	# chenge the filename here
	filename="gen_tasks/tasks_dump_400_4t_555408.json"
	# change the number of processors here
	n_processor=10
	# change the space(spc) or time(t) for each processor here
	spc_t_dict={"Processor%d"%r:{"spc":555500,"t":555500} for r in range(n_processor)}
	# change the algorithm here EDF='edf' RM='rm'
	algo='edf'
	# pickle file for the network
	net_file="graph/Graph_scale.gpickle"
	# Function call for execution
	exe(n_processor,algo,spc_t_dict,filename,net_file)
