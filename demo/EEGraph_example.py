
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import eegraph
import os

#1) Read EEG files and transform into NetworkX graphs with EEGRAPH
#============================================================================================================================================================================

def search(values, searchFor):
    for k in values:
        if (searchFor == k):
            return (values[k])

    
def search_key(values, searchFor):
    for key, value in values.items():
        if value[0] == searchFor:
            return key
          
    
def test_empty(graphs, conn_empty_values, conn):
    conn_empty_aux = [0] * len(conn_empty_values)
    for i in range(len(graphs)):
        if(nx.is_empty(graphs[i])):
            conn_empty_aux[conn] += 1
    
    conn_empty_values[conn] = conn_empty_values[conn] + conn_empty_aux[conn]
    print('Empty:',conn_empty_values,'\n')
    return conn_empty_values   
    
    
def modelate_with_different_connectivity(window_size, label, connectivity_number_total, G, conn_empty_values):
    total_graphs_class_0, total_graphs_class_1  = [], []
    for i in range(connectivity_number_total):
        conn = search_key(connectivity_measures, i)
        bands = search(connectivity_measures, conn)[1]
        
        # The threshold can be omited to use the default one
        graphs, _ = G.modelate(window_size = window_size, connectivity = conn, bands = bands, threshold = 0.8)  

        conn_empty_values = test_empty(graphs, conn_empty_values, i)
        
        if(int(label)):
            total_graphs_class_1 = total_graphs_class_1 + list(graphs.values())    
        
        else:
            total_graphs_class_0 = total_graphs_class_0 + list(graphs.values())
            

    return total_graphs_class_0, total_graphs_class_1, conn_empty_values


def open_data_directories(path, window_size_class_0, window_size_class_1, connectivity_number_total, exclude=[None]):
    conn_empty_values = [0] * connectivity_number_total
    graphs_class_0, graphs_class_1 = [], []
    class_files = os.listdir(path)
    for entry in class_files:
        eeg_files = os.listdir(path + '/' + entry)
        for eeg in eeg_files:
            eeg_path = (path + '/' + entry + '/' + eeg)
            print(eeg_path, entry)
            G = eegraph.Graph() 
            G.load_data(path= eeg_path, exclude = exclude)
            
            if(entry == '1'):     # Number 1 corresponds to "espasmo" data
                window_size = window_size_class_1
            elif (entry == '0'):  # Number 0 corresponds to "presalva" data
                window_size = window_size_class_0
            
            print('\n=========================================')
            final_graphs_class_0, final_graphs_class_1 , conn_empty_values = modelate_with_different_connectivity(window_size=window_size,
                                                                                                                label=entry,
                                                                                                                connectivity_number_total=con_number_total, 
                                                                                                                G=G, 
                                                                                                                conn_empty_values=conn_empty_values)
            
            graphs_class_0 = graphs_class_0 + final_graphs_class_0
            graphs_class_1 = graphs_class_1 + final_graphs_class_1
        
    return graphs_class_0, graphs_class_1


"""   
connectivity_measures = {'cross_correlation': (0, [None]), 'pearson_correlation': (1, [None]), 'squared_coherence': (2, ['delta', 'theta', 'alpha', 'beta']),
                         'imag_coherence': (3, ['delta', 'theta', 'alpha', 'beta']), 'corr_cross_correlation': (4, [None]), 'wpli': (5, ['delta', 'theta', 'alpha', 'beta']), 
                         'plv': (6, ['delta', 'theta', 'alpha', 'beta']), 'pli': (7, [None]),
                         'power_spectrum': (8, ['delta', 'theta', 'alpha', 'beta']), 'spectral_entropy': (9, ['delta', 'theta', 'alpha', 'beta']), 
                         'shannon_entropy': (10, [None])}     

"""
 
connectivity_measures = {'pearson_correlation': (0, [None])}   #CONNECTIVITY MEASURES USED


path = 'data'                                                         #<--------------- PATH TO FOLDER CONTAINING EEGs
window_size_class_0 = 1                                               #<--------------- CLASS 0 WINDOW SIZE
window_size_class_1 = 1                                               #<--------------- CLASS 1 WINDOW SIZE
con_number_total = 1                                                  #<--------------- NUMBER OF CONNECTIVITY MEASURES USED, MUST BE THE SAME AS LENGTH OF DICTIONARY 'connectivity_measures'
graphs_class_0, graphs_class_1 = open_data_directories(path, window_size_class_0, window_size_class_1, con_number_total) 
print('\n=========================================')
print('Total graphs Generated for class 0: ', len(graphs_class_0))
print('Total graphs Generated for class 1: ', len(graphs_class_1))
graphs = [graphs_class_0, graphs_class_1]


#2) Visualize graphs
#============================================================================================================================================================================

def visualize_graphs(graphs, selected):
    G = eegraph.Graph() 
    for i in range(selected[0], selected[1]+1):
        G.visualize(graphs[i])
    
    
wanted = [0, 0]   # Graph position  
visualize_graphs(graphs_class_1, wanted)


#3)Histogram
#============================================================================================================================================================================

def edges_histogram(graphs, label):
    total_edges, edges_dict = [], {}
    for i in range(len(graphs)):
        edges = [e for e in graphs[i].edges]
        edges_dict[str(i+1)] = len(edges)
        
    keys = edges_dict.keys()
    values = edges_dict.values()
    plt.figure(figsize=(30,15))
    plt.title('Histogram: Edges per Graph. Class ' + str(label), fontsize=20)
    plt.hist(values, bins=max(values)+1-min(values))
    plt.xlabel('Number of edges')
    plt.ylabel('Count')
    #plt.bar(keys, values, align='center')
    plt.show()

    
print('\n=====================================================================')       
for j in range(2):
    edges_histogram(graphs[j], j)
        
    
#4)Empty graphs
#============================================================================================================================================================================

def empty_graphs(graphs):
    empty_graphs, empty_dict = 0, {}
    for i in range(len(graphs)):
        if(nx.is_empty(graphs[i])):
            empty_dict[i] = True
            empty_graphs += 1
        else:
            empty_dict[i] = False
    
    return empty_graphs, empty_dict
    
print('\n=====================================================================') 
empty_amount, graphs_dict = [None]*2, [None]*2
for j in range(2):
    empty_amount[j], graphs_dict[j] = empty_graphs(graphs[j])
    print('\nNumber of Empty graphs. Class ' + str(j) + ': ' , empty_amount[j])
    print('Empty graphs (True).', graphs_dict[j])
    
    
#5)Erase Empty Graphs
#============================================================================================================================================================================

def delete_graphs(graphs, graphs_dict):
    for key,value in reversed(graphs_dict.items()):
        if(value):
            print('Deleting graph in index:', str(key))
            del graphs[key]
    return graphs


print('\n=====================================================================') 
print('Deleting empty graphs.')
for j in range(2):
    if (empty_amount[j]):
        print('\nGraphs in Class', j, ':')
        graphs[j] = delete_graphs(graphs[j], graphs_dict[j])

        
print('\nTotal graphs for class 0: ', len(graphs[0]))
print('Total graphs for class 1: ', len(graphs[1]))
    
    
#6)Mean value and Standard Deviation for graphs
#============================================================================================================================================================================
def mean_std(graphs):
    edges_weights, edges_dict = [], {}
    for i in range(len(graphs)):
        edges = [d.get('weight') for e1,e2,d in graphs[i].edges(data=True)]
        edges_weights = edges_weights + edges

    print('Mean:', round(np.mean(edges_weights),5))
    print('STD:', round(np.std(edges_weights),5))
    
    
print('\n=====================================================================')
print('Mean values and Standar Deviation for edges in the graphs.')
for j in range(2):
    print('\nClass', j, ':')
    mean_std(graphs[j])