""" A module for generating the demands in a routing instance."""

import numpy as np
import random


def generate_demands(
    num_customers,     # (int) - number of demands to be generated
    dem_distr,         # (str) - demands distribution (options below)
    locations, lx, ly  # extra information (only needed for quadrant distribution)
):  # Returns: tuple of np.array with demands as well as generation parameters
    """Generates demands for a routing instance from one of several distributions."""
    
    # Demands distribution
    if not dem_distr:
        dem_distr = random.choice([
            'unitary', 
            'lowval_highcv', 
            'lowval_lowcv', 
            'highval_highcv', 
            'highval_lowcv', 
            'manysmall_fewlarge',
            'quadrant'
        ])
    
    if dem_distr == 'unitary': # equal demand
        demands = np.ones(num_customers).astype(int) * np.random.randint(low=1, high=100)
    
    elif dem_distr == 'lowval_highcv':
        demands = np.random.randint(low=1, high=10, size=num_customers)
        
    elif dem_distr == 'lowval_lowcv':
        demands = np.random.randint(low=5, high=10, size=num_customers)
    
    elif dem_distr == 'highval_highcv':
        demands = np.random.randint(low=1, high=100, size=num_customers)
    
    elif dem_distr == 'highval_lowcv':
        demands = np.random.randint(low=50, high=100, size=num_customers)
    
    elif dem_distr == 'manysmall_fewlarge':
        customers_small = int(np.random.uniform(0.7, 0.95) * num_customers)
        customers_large = num_customers - customers_small
        demands_small = np.random.randint(low=1, high=10, size=customers_small)
        demands_large = np.random.randint(low=50, high=100, size=customers_large)
        demands = np.concatenate((demands_small, demands_large))
        demands = np.take(demands,np.random.permutation(demands.shape[0]),axis=0,out=demands) # shuffle
        
    elif dem_distr == 'quadrant':
        high_demand = random.choice([0, 1]) # odd or even quadrant with high demands
        demands = []
        for i in range(1, num_customers+1):
            x_high = locations[i][0] >= lx/2
            y_high = locations[i][1] >= ly/2
            if not x_high and y_high:
                quadrant = 1
            elif x_high and y_high: 
                quadrant = 2
            elif x_high and not y_high: 
                quadrant = 3
            elif not x_high and not y_high: 
                quadrant = 4
            if quadrant % 2 == high_demand:
                demands.append(np.random.randint(low=1, high=50))
            else:
                demands.append(np.random.randint(low=51, high=100))         
        demands = np.array(demands)
    
    # Add depot demand
    dem_depot = np.array([0])
    demands = np.concatenate((dem_depot, demands))
    
    return demands, dem_distr
    
