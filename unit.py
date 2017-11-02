import prettytable
import generator_env

MAX_HOUR= 24

LAMBDA_MAX = 1.0
E_MAX = 0.1
P_DEL_MAX = 1.0


class Generator:
	def __init__(self, index=0, p_max=0, p_min=0, a=0, b=0, c=0, startup_cost=0, curr_generation=0):
		self.index = index
		self.p_max = p_max
		self.p_min = p_min
		self.a = a
		self.b = b
		self.c = c
		self.flapc = 0
		self.startup_cost = startup_cost
		self.curr_generation = curr_generation

	def Cost(self, power):
		return self.a+self.b*power+self.c*power*power

class State:
	def __init__(self, p_cost=0, f_cost=0, prev_state=None, is_feasible=False, avl_generators={}):
		self.p_cost = p_cost
		self.f_cost = f_cost
		self.prev_state = prev_state
		self.is_feasible = False
		self.avl_generators = {}


def EconomicDispatch(gvn_gens, p_demand):
	lmb=LAMBDA_MAX 
	error=E_MAX
	p_del=P_DEL_MAX
	p_total=0
	sum_c=0
	_generators = gvn_gens
	
	while p_del > error:
		p_total = 0.0
		sum_c = 0.0
		for i, generator in enumerate(gvn_gens):
			
			_generators[i].curr_generation = (lmb-generator.b)/(2*generator.c)
			
			if _generators[i].curr_generation > generator.p_max:
				_generators[i].curr_generation = generator.p_max
			
			if _generators[i].curr_generation < generator.p_min:
				_generators[i].curr_generation = generator.p_min
			
			p_total = _generators[i].curr_generation + p_total
			sum_c = sum_c+1.0/(2.0*generator.c)
			
		p_del = p_demand-p_total
		lmb = lmb + p_del/sum_c

	_state = State(p_cost=0, f_cost=0, prev_state=None, is_feasible=None, avl_generators={})
	_state.load = p_demand
	for i, generator in enumerate(_generators):
		_state.p_cost = _state.p_cost+gvn_gens[i].Cost(generator.curr_generation)
		_state.avl_generators[i] = generator.curr_generation
	return _state

# read the generators from the input file
gens = generator_env.generators
MAX_GEN = len(gens)

generators = []
for i in range(MAX_GEN):
	generators.append(Generator(
								index=gens[i]['index'],
								p_max=gens[i]['p_max'],
								p_min=gens[i]['p_min'],
								a=gens[i]['a'], 
								b=gens[i]['b'], 
								c=gens[i]['c'], 
								startup_cost=gens[i]['startup_cost']))



#input the load for 24 hours
load = generator_env.loads

# for i in range(MAX_HOUR):
# 	 load.append(random.randint(100,650))

#calculate flapc for all generators using in-built cost function
for generator in generators:
	generator.flapc = generator.Cost(generator.p_max)/generator.p_max

#sort generators using the flapc attribute
generators.sort(key=lambda x:x.flapc)
gen_index = [el.index for el in generators]


all_states = [[State(is_feasible=False) for x in range(MAX_HOUR)] for y in range(MAX_GEN)]  
s_costs = [[0 for x in range(MAX_GEN)] for y in range(MAX_GEN)]

#calculating the p_cost of each state and the generator's generating values
for hour in range(MAX_HOUR):
	for i, gen in enumerate(generators):
		max_capacity =  sum(x.p_max for x in generators[0:(i+1)])
		if load[hour] <= max_capacity:
			all_states[i][hour] = EconomicDispatch(generators[0:(i+1)], load[hour])
			all_states[i][hour].is_feasible = True


#finding the transition cost
for i in range(MAX_GEN):
	for j in range(MAX_GEN):
		if i >= j:
			s_costs[i][j] = 0
		else:
			for k in range(i+1,j):
				s_costs[i][j] = s_costs[i][j]+generators[k].startup_cost


#finding the F cost for the first hour
for i in range(MAX_GEN):
	all_states[i][0].f_cost = all_states[i][0].p_cost
	for k in range(0,i):
		all_states[i][0].f_cost = all_states[i][0].f_cost + generators[i].startup_cost



for hour in range(1,MAX_HOUR):

	for i in range(MAX_GEN):
		
		#finding the first feasible state in the previous hour
		first_feasible = 0
		for first_feasible in range(MAX_GEN):
			if all_states[first_feasible][hour-1].is_feasible == True:
				break
		
		min_cost = all_states[first_feasible][hour-1].f_cost + s_costs[first_feasible][i]
		min_index = first_feasible

		#finding the minimum of all the feasible states
		for next_feasible in range(min_index, MAX_GEN):
			if all_states[next_feasible][hour-1].is_feasible and min_cost > all_states[next_feasible][hour-1].f_cost+s_costs[next_feasible][i]: 
				min_cost = all_states[next_feasible][hour-1].f_cost+s_costs[next_feasible][i]
				min_index = next_feasible

		all_states[i][hour].f_cost = all_states[i][hour].p_cost + min_cost
		all_states[i][hour].prev_state = min_index


#find first feasible state at 24th hour
feasible_state = 0;
for feasible_state in range(MAX_GEN):
	if all_states[first_feasible][MAX_HOUR-1].is_feasible == True:
		feasible_state = first_feasible

#Store the final state for 24th hr by finding minimum of all states
final_states = [State() for x in range(MAX_HOUR)]
final_states[MAX_HOUR-1] = all_states[feasible_state][MAX_HOUR-1];	

for i in range(feasible_state, MAX_GEN):
	if final_states[MAX_HOUR-1].f_cost > all_states[i][MAX_HOUR-1].f_cost and all_states[i][MAX_HOUR-1].is_feasible:
			final_states[MAX_HOUR-1] = all_states[i][MAX_HOUR-1]

#backtracking the states for the previous hours
for i in range(MAX_HOUR-2, -1, -1):
	final_states[i] = all_states[final_states[i+1].prev_state][i]

columns = ['Hour','load','P cost','F cost']
for i in range(0,MAX_GEN):
	columns.append("Generator - " + str(gen_index[i]))
table = prettytable.PrettyTable(columns)

for i, state in enumerate(final_states):
	row = [i+1,state.load,state.p_cost,state.f_cost]
	for j in range(MAX_GEN):
		if j in state.avl_generators:
			row.append(state.avl_generators[j])
		else:
			row.append(0) 
	table.add_row(row)

print table