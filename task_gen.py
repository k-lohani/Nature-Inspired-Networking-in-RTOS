import random
import json
import migrate_task as mt
import global_scheduler as gs 
import rm
import edf_fin as edf

def task_gen(n):
	task=[]
	while True:
		if len(task)==n:
			break
		else:
			temp=[]
			a=random.randint(0,20)
			# print("a",a)
			d=random.randint(10,50)
			# print("d",d)
			while True:
				temp_p=random.randint(10,d+1)
				if temp_p<=d:
					p=temp_p
					# print("p",p)
					break
			while True:
				temp_e=random.randint(1,p)
				if (temp_e<p):
					e=temp_e
					# print("e",e)
					break
				else:
					continue 
			temp.append(e)
			temp.append(p)
			temp.append(a)
			temp.append(d)
			if temp not in task:
				task.append(temp)
	keys=["Task%d"%r for r in range(n)]
	task_dict=dict(zip(keys,task))
	return task,task_dict,n


def task_gen_2(n,n_proc):
	tasks=[]
	while len(tasks)<n:
		temp=[]
		# random.seed(0)
		a=random.randint(0,100)
		d=random.randint(400,500)
		p=random.choice([x for x in range(334,350) if (x%2==0) and (x%3==0)]) 
		e=random.randint(1,p-250)
		if (p<=d) and (e<p) and ((e/p)<=0.05):
			temp.append(e)
			temp.append(p)
			temp.append(a)
			temp.append(d)
			if temp not in tasks:
				tasks.append(temp)
	keys=["Task%d"%r for r in range(n)]
	tasks_dict=dict(zip(keys,tasks))
	q=gs.main_gs(tasks_dict,n_proc)
	load=mt.compile_feasibility_values(n_proc,q,'edf')
	hp={proc_name:edf.calc_hyperperiod(q[proc_name]) for proc_name in q.keys()}
	return tasks_dict,load,q,hp

# def task_gen_3(n,n_proc):
	# tasks=[]
	



# GENERATE AND TEST TASKS
n_proc=10
tasks_dict,load,q,hp=task_gen_2(400,n_proc)
# print(tasks_dict)
for k,v in load.items():
	if (v[0]==True):
		print("\t",k,v,"------->")
	else:
		print(k,v)
print(hp)



# print(q)
# tasks,tasks_dict,n=task_gen(1000)
# q=gs.main_gs_reassign(tasks_dict,10)
# load=mt.compile_feasibility_values(10,q,'rm')
# print(load)


# task_dump=json.dumps(tasks_dict, indent=5)
# with open("gen_tasks/tasks_dump_na.json",'w') as f:
# 	f.write(task_dump)
# print(tasks_dict)

# task_dict_loaded=gs.load_json("gen_tasks/tasks_dump_na.json")
# shared_dict=gs.main_gs(task_dict_loaded,n_proc)
# # q=gs.main_gs_reassign(tasks_dict,10)
# # print(q)
# load=mt.compile_feasibility_values(n_proc,shared_dict,'rm')
# hp={proc_name:rm.calc_hyperperiod(shared_dict[proc_name]) for proc_name in shared_dict.keys()}

# for k,v in load.items():
# 	if (v[0]==True):
# 		print("\t",k,v,"------->")
# 	else:
# 		print(k,v)
# print(hp)
