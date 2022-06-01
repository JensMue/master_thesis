""" A module for plotting routing instances."""

import routing
import os
import pickle
import json
import numpy as np
import pandas as pd
import time


def load_instance(path):
    """Loads a routing instance from a file."""
    # Load pickle.
    if path[-7:] == '.pickle':
        with open(path, 'rb') as f:
            instance = pickle.load(f)
        return instance
    # Load json or txt.
    elif path[-5:] == '.json' or path[-4:] == '.txt':
        with open(path, 'r') as f:
            instance_dict = json.load(f)
        instance_dict = undo_json_serializable(instance_dict)
        return routing.routingInstance.fromdict(instance_dict)
    else:
        print('File-type not recognized.')
        

def undo_json_serializable(instance_dict):
    """Restores the original instance attribute types which have been changed to be json-serializable."""
    for key in instance_dict.keys():
        if (isinstance(instance_dict[key], list) 
            and key not in ['solution_distance', 'solution_routes', 'solution_times', 
                            'solution_distances', 'solution_loads']):
            instance_dict[key] = np.array(instance_dict[key])
        if key in ['max_time', 'wait_time']:
            instance_dict[key] = np.float64(instance_dict[key])
        # if key == 'gen_params':
        #     instance_dict[key]['avg_route_size'] = np.float64(instance_dict[key]['avg_route_size'])
    return instance_dict


def load_dataset(
    path,                 # (str) - path from where to load
    filetype,             # (str) - which filetype to load (pickle, json, or txt)
    num_instances='all',  # (str/int) - 'all': load all instances in path, int: how many instances to load
    info='instance',      # (str) - which information to load (instance, gen_params, or combined)
    verbose=10            # (int) - after how many instances report progress?
):  # -> Returns: pd.DataFrame
    """Loads a dataset of instances as pandas DataFrame."""
    t0 = time.time()
    # Loop through files
    filelist = os.listdir(path)
    if num_instances != 'all':
        filelist = filelist[:num_instances]
    rows = []
    loaded = 0
    for filename in filelist:
        # Load instance
        if filename.endswith('.'+filetype):
            instance = routing.load_instance(path+filename)
            # Load instance characteristics
            if info=='instance':
                rows.append(instance.__dict__)
            # Load generation parameters
            elif info == 'gen_params':
                rows.append(instance.__dict__['gen_params'])
            # Load instance characteristics and generation parameters
            elif info == 'combined':
                dict_instance = instance.__dict__
                dict_gen_params = dict_instance['gen_params'].copy()
                del dict_instance['gen_params']
                rows.append({**dict_instance, **dict_gen_params})
            loaded += 1
            # Print loading progress
            if verbose:
                if loaded % verbose == 0:
                    print(f'{loaded} instances loaded ({round(time.time()-t0, 2)}s)')
    return pd.DataFrame(rows)



################################### LOAD BENCHMARKS ################################################



def load_benchmark_instance(filename, num_customers=25, path='data/benchmarks/solomon_instances/'):
    """Loads a single benchmark instance (Solomon or Gehring-Homberger)."""
    # Create an empty instance dictionary
    d = {'variant': 'cvrptw', 'locations': [], 'demands': [], 'time_windows': [], 'service_times': []}
    # Read the file and fill the instance dictionary
    with open (path+filename+'.txt', 'r') as f:
        for i, line in enumerate(f):
            row = line.split() # Split on any whitespace (including tabs)
            if i == 0: # get title
                d['name'] = str(row[0])+'.'+str(num_customers)
            elif i == 4: # get num_vehicles and capacities
                num_vehicles = int(row[0])
                d['vehicle_capacities'] = np.array([int(row[1])] * num_vehicles)
            elif i > 8 and i < 10 + num_customers: # get locations, time-windows, demands, service time
                d['locations'].append((int(row[1]), int(row[2])))
                d['demands'].append(int(row[3]))
                d['time_windows'].append((int(row[4]), int(row[5])))
                d['service_times'].append(int(row[6]))
    # Convert lists to arrays
    for k, v in d.items():
        if isinstance(v, list):
            d[k] = np.array(v)
    # Create and return instance
    instance = routing.routingInstance.fromdict(d)
    instance.compute_distance_matrix('euclidean')
    # instance.depot = 0
    return(instance)


def load_solomon_solutions(solution_accuracy='best_known'):
    """Loads the solutions to the benchmarks by Solomon (1987)."""
    if solution_accuracy == 'best_known':
        return mix_solomon_solutions()
    elif solution_accuracy == 'optimal' or solution_accuracy == 'heuristic':
        # set correct path
        path = f'data/benchmarks/solomon_solutions/solomon_{solution_accuracy}/'
        # Create dict
        sol_dict = {'name': [], 'sol_vehicles': [], 'sol_distance': [], 'sol_authors': []}
        # Loop through files and read lines
        filelist = os.listdir(path)
        for f in filelist:
            if f.endswith(".txt"):
                with open (path+f, 'r') as f:
                    for i, line in enumerate(f):
                        if i > 15:
                            row = line.strip()
                            if i % 8 == 0:
                                if solution_accuracy == 'optimal':
                                    sol_dict['name'].append(row)
                                elif solution_accuracy == 'heuristic':
                                    sol_dict['name'].append(row+'.100')
                            elif i % 8 == 2:
                                sol_dict['sol_vehicles'].append(row)
                            elif i % 8 == 4:
                                sol_dict['sol_distance'].append(row)
                            elif i % 8 == 6:
                                sol_dict['sol_authors'].append(row)
        # Return as DataFrame
        sol_df = pd.DataFrame.from_dict(sol_dict)
        sol_df = sol_df[(sol_df['name'] != '')]
        sol_df = sol_df[(sol_df['name'] != '.100')]
        abr = solution_accuracy[:3]
        sol_df.columns = ['name', f'sol_{abr}_vehicles', f'sol_{abr}_distance', f'sol_{abr}_authors']
        return sol_df
    
    
def mix_solomon_solutions():
    """Combines the known optimal and best heuristic solutions for the benchmarks by Solomon (1987)."""
    sol_opt_df = load_solomon_solutions(solution_accuracy='optimal')
    sol_heu_df = load_solomon_solutions(solution_accuracy='heuristic')
    sol_comb_df = pd.merge(sol_opt_df, sol_heu_df, on='name', how='outer')
    sol_best_df = pd.DataFrame({'name': [], 'sol_best_vehicles': [], 'sol_best_distance': [], 'sol_best_authors': []})
    for i in range(sol_comb_df.shape[0]):
        sol_best_df.loc[i, 'name'] = sol_comb_df.loc[i, 'name']
        if sol_comb_df.loc[i, 'sol_opt_distance'] !='':#if not pd.isnull(solomon_df.loc[i, 'sol_opt_distance']):
            sol_best_df.loc[i, 'sol_best_vehicles'] = sol_comb_df.loc[i, 'sol_opt_vehicles']
            sol_best_df.loc[i, 'sol_best_distance'] = sol_comb_df.loc[i, 'sol_opt_distance']
            sol_best_df.loc[i, 'sol_best_authors'] = sol_comb_df.loc[i, 'sol_opt_authors']
        else:
            sol_best_df.loc[i, 'sol_best_vehicles'] = sol_comb_df.loc[i, 'sol_heu_vehicles']
            sol_best_df.loc[i, 'sol_best_distance'] = sol_comb_df.loc[i, 'sol_heu_distance']
            sol_best_df.loc[i, 'sol_best_authors'] = sol_comb_df.loc[i, 'sol_heu_authors']
    return sol_best_df