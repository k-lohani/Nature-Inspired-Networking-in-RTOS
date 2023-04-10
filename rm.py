import math

def take_LCM(arr):
  lcm = arr[0]
  for i in range(1,len(arr)):
    lcm = lcm*arr[i]//math.gcd(lcm, arr[i])
  return lcm

# def take_input():
# 	n=int(input("Enter number of tasks: "))
# 	task=[]
# 	print("Instructions: Enter the details in the order of Execution Time, Period, Arrival Time then press enter for inserting another task detail")
# 	print("Enter Execution time, Period, and Arrival Time of each Tasks")
# 	for i in range(0,n):
# 		pair=[]
# 		inp1=input()
# 		c,t,a=map(int,inp1.split(','))
# 		pair.append(int(c))
# 		pair.append(int(t))
# 		pair.append(int(a))
# 		task.append(pair)
# 	task_dict_keys=["Task%d"%r for r in range(n)]
# 	task_dict=dict(zip(task_dict_keys,task))
# 	return task,task_dict,n
# e p a d


def check_schedulability(tasks_dict):
	tasks=[v for v in tasks_dict.values()]
	n=len(tasks)
	listU=[(t[0]/t[1]) for t in tasks]
	U=round(sum(listU),2)
	if n==0:
		form=1
	else:
		form=round((n)*((2**(1/n))-1),2)
	if U<=form:
		return True,U,form
	if U>form:
		return False,U,form

def calc_hyperperiod(tasks_dict):
	tasks=[v for v in tasks_dict.values()]
	periods=[task[1] for task in tasks]
	hp=take_LCM(periods)
	return hp

def assign_priority(tasks_dict):
	tasks_name=[t for t in tasks_dict.keys()]
	period=[tasks_dict[t][1] for t in tasks_name]
	arrival=[tasks_dict[t][2] for t in tasks_name]
	priority_dict=[x for _,_, x in sorted(zip(arrival, period, tasks_name), key=lambda pair: (pair[0],pair[1]))]
	return priority_dict


def calc_timeperiod(tasks_dict,hp):
	timeperiod={time:[] for time in range(hp+1)}
	# print(timeperiod)
	for k,t in tasks_dict.items():
		p=t[1] #extracting period from each task one by one
		a=t[2] #extracting arrival time from each task one by one
		d=int((hp-a)/(p))
		for r in range(d+1):
			time=p+(p*r)+a
			if time>hp:
				break
			else:
				timeperiod[time].append(k)
		timeperiod[a].append(k)
	return timeperiod


def simulate(tasks_dict,hp,periodmarkings):
	sim=[]
	stack=[]
	for t in range(hp):
		temp_stack=periodmarkings[t]
		for avbl in temp_stack:
			exe=tasks_dict[avbl][0]
			for e in range(exe):
				stack.append(avbl)
		# extracting period for each task in stack and sorting the tasks in the order of lowest to highest period i.e. assigning priorities
		period=[tasks_dict[task][1] for task in stack]
		arrival=[tasks_dict[task][2] for task in stack]
		sorted_stack=[x for _,_, x in sorted(zip(arrival, period, stack), key=lambda pair: (pair[0],pair[1]))]
		stack=sorted_stack
		if len(stack)>0:
			sim.append(stack[0])
			stack.pop(0)
		else:
			sim.append("idle")
	return sim

def main_rm(tasks_dict):
	results={}
	res,U,form=check_schedulability(tasks_dict)
	if res==True:
		hp=calc_hyperperiod(tasks_dict)
		periodmarkings=calc_timeperiod(tasks_dict,hp)
		sim_arr=simulate(tasks_dict,hp,periodmarkings)
		results["Simulation"]=sim_arr
		results["Verdict"]="Sucess"
		return results
	else:
		results["Verdict"]="Failed"
		return results
