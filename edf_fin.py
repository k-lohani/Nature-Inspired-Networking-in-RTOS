import math

def take_LCM(arr):
  lcm = arr[0]
  for i in range(1,len(arr)):
    lcm = lcm*arr[i]//math.gcd(lcm, arr[i])
  return lcm

def check_schedulability(tasks_dict):
	tasks=[v for v in tasks_dict.values()]
	listU=[(t[0]/t[1]) for t in tasks]
	U=round(sum(listU),2)
	if U<=1:
		return True,U
	else:
		return False,U

def calc_hyperperiod(tasks_dict):
	tasks=[v for v in tasks_dict.values()]
	periods=[task[1] for task in tasks]
	hp=take_LCM(periods)
	return hp


def calc_timeperiod(tasks_dict,hp):
	timeperiod={time:[] for time in range(hp+1)}
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
		# extracking deadline from task dictionary sorting stack basis the deadline i.e. assigning dynamic priority
		deads=[tasks_dict[task][3] for task in stack]
		sorted_stack=[x for _, x in sorted(zip(deads, stack), key=lambda pair: pair[0])]
		stack=sorted_stack
		# creating timeline and updating stack
		if len(stack)>0:
			sim.append(stack[0])
			stack.pop(0)
		else:
			sim.append("idle")
	return sim



def main_edf(tasks_dict):
	results={}
	res,U=check_schedulability(tasks_dict)
	if res==True:
		hp=calc_hyperperiod(tasks_dict)
		timeperiod=calc_timeperiod(tasks_dict,hp)
		sim_arr=simulate(tasks_dict,hp,timeperiod)
		results["Simulation"]=sim_arr
		results["Verdict"]="Sucess"
		return results
	else:
		results["Verdict"]="Failed"
		return results