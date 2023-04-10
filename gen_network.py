import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def gen_graph(n_processors,p,type,**kwargs):
	if type=='random':
		G=nx.erdos_renyi_graph(n_processors, p)
	if type=='grid':
		G=nx.erdos_renyi_graph(n_processors, 1)
	if type=='existing':
		G = nx.read_gpickle(kwargs['filename'])
	if type=='scale':
		G= nx.barabasi_albert_graph(n_processors,5)
	if type=='regular':
		G= nx.random_regular_graph(2,n_processors)
	return G

def get_net(n_processors,p,type,**kwargs):
	# create a relabling map basis number of processors
	relabel_map={r:"Processor%d"%r for r in range(n_processors)}
	# generate graph
	G=gen_graph(n_processors,p,type,filename=kwargs["filename"])
	# relabel nodes
	G=nx.relabel_nodes(G,relabel_map)
	# initialize the connections dictionary
	conn={}
	# calculate connections
	for proc in relabel_map.values():
		conn[proc]=[n for n in G.neighbors(proc)]
	# defining the condition so that a file is saved only if it is not existing
	if type!='existing':
		# defining figure size
		fig = plt.figure(figsize=(10, 15))
		# draw the graph that needs to be saved
		nx.draw(G, with_labels=True,node_color='#ffefdb')
		# save graph png in file
		plt.savefig("graph/Graph_"+type+".png", format="PNG")
		# saving the pickle file for graph
		nx.write_gpickle(G, "graph/Graph_"+type+".gpickle")
		# plt.show()
	return conn

def read_net(filename):
	# generate graph
	G=nx.read_gpickle(filename)
	# initialize the connections dictionary
	conn={}
	# implementing DFS
	for src in list(G.nodes):
		conn[src]=list(nx.dfs_tree(G, source=src))
	# updating the connections dict 
	for k,v in conn.items():
		if k in v:
			conn[k].remove(k)
	return conn

	
def graph_plot(filename,type, n):
	G=nx.read_gpickle(filename)
	relabel_map={"Processor%d"%r:r+1 for r in range(n)}
	G=nx.relabel_nodes(G,relabel_map)
	nx.draw(G, with_labels=True,node_color='#1F77B4', font_color="white")


	size=G.size()
	valency=G.degree()
	degree_freq=nx.degree_histogram(G)
	degrees = range(len(degree_freq))
	# plot
	sns.set_style("whitegrid")
	plt.figure(figsize=(12, 8)) 
	plt.bar(degrees, np.array(degree_freq)/10) 

	plt.title('Degree distribution of '+type+' Network', fontsize=25)
	plt.xlabel('Degree of Nodes', fontsize=18)
	plt.ylabel('Probability (Degree) on chosen nodes', fontsize=18)
	plt.xticks(degrees, fontsize=15)
	plt.yticks(fontsize=15)
	print(size, valency)
	print(degree_freq)
	plt.show()


c=read_net("graph/Graph_regular.gpickle")
# print(c)
graph_plot("graph/Graph_scale.gpickle","Scale-Free",10)

# c=get_net(10,0.5,"regular",filename="graph/Graph_random.gpickle")
# print(c)