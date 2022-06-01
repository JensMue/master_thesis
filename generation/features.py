""" A module to extract features for an instance or a whole dataset."""

import routing
import generation
import os
import time
import numpy as np
import pandas as pd
from scipy.spatial import ConvexHull
from scipy.stats import pearsonr, spearmanr
from scipy.spatial import distance


def extract_features_dataset(
    path,                 # (str) - path from where to load
    filetype='pickle',    # (str) - which filetype to load (pickle, json, or txt)
    num_instances='all',  # (str/int) - 'all': load all instances in path, int: how many instances to load
    verbose=10            # (int) - after how many instances report progress?
):  # -> Returns: pd.DataFrame
    """Loads a dataset of instances as pandas DataFrame."""
    t0 = time.time()
    filelist = os.listdir(path)
    if num_instances != 'all':
        filelist = filelist[:num_instances]
    rows = []
    loaded = 0
    # Loop through files
    for filename in filelist:
        if filename.endswith('.'+filetype):
            instance = routing.load_instance(path+filename)
            instance.compute_distance_matrix()
            features = extract_features_instance(instance)
            if hasattr(instance, 'solution_distance'):
                features['distance'] = instance.solution_distance
            rows.append(features)
            loaded += 1
            # Print loading progress
            if verbose:
                if loaded % verbose == 0:
                    print(f'{loaded} instances loaded ({round(time.time()-t0, 2)}s)')
    return pd.DataFrame(rows)


def extract_features_instance(instance):
    """Extract features from an instance."""
    
    # Create features dictionary.
    features = {}
    
    # Store instance name
    if hasattr(instance, 'name'):
        features['name'] = instance.name
        
    # Extract features about locations and distances (ignore orientation)
    if instance.variant in ['tsp', 'cvrp', 'cvrptw']:
        
        # num_customers
        features['NumCust'] = float(instance.locations.shape[0] - 1)
        
        # area (smallest convex and compact hull)
        hull = ConvexHull(instance.locations)
        features['AreaRoot'] = np.sqrt(hull.volume)
        features['Perimeter'] = hull.area
        bounding_box = generation.MinimumBoundingBox(instance.locations)
        MajorSide = max(bounding_box.length_parallel, bounding_box.length_orthogonal)
        MinorSide = min(bounding_box.length_parallel, bounding_box.length_orthogonal)
        features['SideRatio'] = MajorSide / MinorSide
        
        # Centrality
        avg_node = np.array([np.mean(instance.locations[:,0]), np.mean(instance.locations[:,1])])
        cent_dist = distance.cdist(instance.locations, np.reshape(avg_node, (-1, 2)), 'euclidean')
        cent_dist = cent_dist.flatten()
        relative_cent_dist = cent_dist / features['AreaRoot']
        features['CentDepot'] = relative_cent_dist[0]
        cent_dist = cent_dist[1:]
        features['CentCustAvg'] = np.mean(relative_cent_dist[1:])
        features['CentCustStd'] = np.std(relative_cent_dist[1:])
        
        # Spread/node dispersion
        features['Dispersion'] = np.sqrt(np.std(instance.locations[:,0]) * np.std(instance.locations[:,1])) / features['AreaRoot']
        # from other studies
        features['AvgFurthest'] = np.mean(np.max(instance.distance_matrix, axis=0)) / features['AreaRoot'] # avg of distances to the farthest neighbor of each node
        features['AvgNearest'] = np.mean(np.partition(instance.distance_matrix, 1, axis=1)[:,1]) / features['AreaRoot'] # avg of distances to the nearest neighbor of each node
        
        # depot-customer distances
        depot_cust  = instance.distance_matrix[0,1:]
        relative_depot_cust = depot_cust / features['AreaRoot']
        features['DepCustAvg'] = np.mean(relative_depot_cust)
        features['DepCustStd'] = np.std(relative_depot_cust)
        features['DepCustMin'] = np.min(relative_depot_cust)
        features['DepCustMed'] = np.median(relative_depot_cust)
        features['DepCustMax'] = np.max(relative_depot_cust)
        
        # inter-customer distances
        # delete depot connections from distance matrix
        inter_cust = np.delete(instance.distance_matrix, [0], 0)
        inter_cust = np.delete(inter_cust, [0], 1)
        # create boolean mask which inter cust links are possible
        condition = (((
            inter_cust 
            + np.vstack(instance.time_windows[1:,0])) 
            + np.vstack(instance.service_times[1:])) 
            - instance.time_windows[1:,1]
        ) <= 0
        # delete diagonal and make 1d array
        inter_cust = inter_cust[~np.eye(inter_cust.shape[0],dtype=bool)].reshape(inter_cust.shape[0],-1).ravel()
        condition = condition[~np.eye(condition.shape[0],dtype=bool)].reshape(condition.shape[0],-1).ravel()
        # make 1d array and apply boolean mask
        inter_cust = inter_cust[np.where(condition)]
        total_links = (instance.distance_matrix.shape[0] - 1) * (instance.distance_matrix.shape[1] - 2)
        possible_links = inter_cust.shape[0]
        relative_inter_cust = inter_cust / features['AreaRoot']
        features['IntCustLinks'] = float(possible_links / total_links)
        features['IntCustAvg'] = np.mean(relative_inter_cust)
        features['IntCustStd'] = np.std(relative_inter_cust)
        features['IntCustMin'] = np.min(relative_inter_cust)
        features['IntCustMed'] = np.median(relative_inter_cust)
        features['IntCustMax'] = np.max(relative_inter_cust)
        

    # Extract features about capacities and demands
    if instance.variant in ['cvrp', 'cvrptw']:
        
        relative_demands = instance.demands[1:] / instance.vehicle_capacities[0]
        
        # demand coverage
        features['CapRatio'] = instance.vehicle_capacities[0] / np.sum(instance.demands[1:])
        features['NumVehMin'] = np.sum(relative_demands) # Lower bound for number of vehicles used
        
        # demand characteristics
        features['DemAvg'] = np.mean(relative_demands)
        features['DemStd'] = np.std(relative_demands)
        features['DemMin'] = np.min(relative_demands)
        features['DemMed'] = np.median(relative_demands)
        features['DemMax'] = np.max(relative_demands)


    # Extract features about time windows and service times
    if instance.variant in ['cvrptw']:
        
        # time horizon
        TwDepot = instance.time_windows[0,1]
        features['PossRounds'] = TwDepot / features['Perimeter']
        
        # service times
        relative_service_times = instance.service_times[1:] / TwDepot
        features['StAvg'] = np.mean(relative_service_times)
        features['StStd'] = np.std(relative_service_times)
        features['StMin'] = np.min(relative_service_times)
        features['StMed'] = np.median(relative_service_times)
        features['StMax'] = np.max(relative_service_times)
        
        # share with time windows
        rel_time_windows = instance.time_windows / TwDepot
        rel_tw_constrained = np.array([tw for tw in rel_time_windows if (tw!=rel_time_windows[0]).any()])
        features['TwShare'] = rel_tw_constrained.shape[0] / features['NumCust']
        
        # time windows widths
        rel_tw_widths = rel_time_windows[1:,1] - rel_time_windows[1:,0]
        features['TwWidthAvg'] = np.mean(rel_tw_widths)
        features['TwWidthStd'] = np.std(rel_tw_widths)
        features['TwWidthMin'] = np.min(rel_tw_widths)
        features['TwWidthMed'] = np.median(rel_tw_widths)
        features['TwWidthMax'] = np.max(rel_tw_widths)
        
        # time windows centers
        rel_tw_centers = (rel_time_windows[1:,0] + rel_time_windows[1:,1]) / 2
        features['TwCentAvg'] = np.mean(rel_tw_centers)
        features['TwCentStd'] = np.std(rel_tw_centers)
        features['TwCentMin'] = np.min(rel_tw_centers)
        features['TwCentMed'] = np.median(rel_tw_centers)
        features['TwCentMax'] = np.max(rel_tw_centers)
        
    return features
        
