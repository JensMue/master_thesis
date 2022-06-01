""" A module for generating the locations for a routing instance."""

import numpy as np
import random


def generate_locations(
    num_locations,  # (int) - number of locations to be generated (first is the depot)
    depot_pos=None, # (str) - depot positions (options below)
    loc_distr=None, # (str) - locations distribution (options below)
    lx=1,       # (numeric) - side length x of service area
    ly=1        # (numeric) - side length y of service area
):  # Returns: tuple of np.array with 2D coordinates as well as generation parameters
    """Generates a set of locations for an instance."""
    # Depot position
    if not depot_pos:
        depot_pos = random.choice([
            'central', 'central', 
            'origin', 
            'uniform', 
            'loc_distr'
        ])
    # Location distribution
    if not loc_distr:
        loc_distr = random.choice([
            'uniform', 'uniform',
            'clustered', 'clustered',
            'uniform_clustered', 'uniform_clustered',
            'triangular', 
            'squeezed',
            'uniform_triangular',
            'triangular_squeezed', 
            'side_central', 
            'cavity_dispersion',
            'truncated_exponential'
        ])
    # Generate unit square locations (depot & customers)
    if depot_pos in ['central', 'origin', 'uniform']:
        if depot_pos == 'central':
            loc_depot = np.array([[0.5, 0.5]])
        elif depot_pos == 'origin':
            loc_depot = np.array([[0.0, 0.0]])
        elif depot_pos == 'uniform':
            loc_depot = np.array([np.random.random(2)])
        loc_cust = generate_customer_locations(num_locations-1, loc_distr)
        locations = np.concatenate((loc_depot, loc_cust))
    elif depot_pos == 'loc_distr':
        locations = generate_customer_locations(num_locations, loc_distr)
    # Account for area side lenghts
    locations[:,0] *= lx
    locations[:,1] *= ly
    return np.around(locations, 4), depot_pos, loc_distr    
    

def generate_customer_locations(num_customers, loc_distr=None):
    """Generates the customer locations of an instance following one of several distributions."""

    if loc_distr == 'uniform':
        locations = np.random.uniform(size=(num_customers,2))

    elif loc_distr == 'clustered':
        # determine number of seeds
        num_seeds = np.random.randint(max(int(num_customers/20),2), # min seeds
                                      max(int(num_customers/6),3))  # max seeds
        # determine center locations and spread around them (used in normal distribution)
        centers = np.array([np.random.random(2) for i in range(num_seeds)])
        scale = np.random.uniform(0.035, 0.07)
        # generate clustered locations
        locations = []
        for i in range(num_customers):
            center = random.choice(centers) # select center for customer
            # sample x location
            accept_x = False
            while not accept_x: 
                x = np.random.normal(loc=center[0], scale=scale)
                if x >= 0 and x <= 1:
                    accept_x = True
            # sample y location
            accept_y = False
            while not accept_y: 
                y = np.random.normal(loc=center[1], scale=scale)
                if y >= 0 and y <= 1:
                    accept_y = True
            locations.append([x, y])
        locations = np.array(locations)

    elif loc_distr == 'uniform_clustered':
        # split the customers
        num_cust_unif = int(num_customers / 2)
        num_cust_clust = num_customers - num_cust_unif
        # generate locations
        locations_uniform = generate_customer_locations(num_cust_unif, loc_distr='uniform')
        locations_clustered = generate_customer_locations(num_cust_clust, loc_distr='clustered')
        # combine customers
        locations = np.concatenate((locations_uniform, locations_clustered), axis=0)
  
    elif loc_distr == 'triangular':
        locations = np.random.default_rng().triangular(0, 0.5, 1, size=(num_customers,2))

    elif loc_distr == 'squeezed':
        locations = []
        for i in range(num_customers):
            accept = False
            while accept == False:
                loc_x = np.random.random()
                loc_y = np.random.random()
                threshold = np.random.random()
                if threshold < loc_x * loc_y:
                    locations.append([loc_x, loc_y])
                    accept = True
        locations = np.array(locations)
            
    elif loc_distr == 'uniform_triangular':
        loc_unif = np.random.random(num_customers)
        loc_tria = np.random.default_rng().triangular(0, 0.5, 1, num_customers)
        locations = np.vstack((loc_unif, loc_tria)).T

    elif loc_distr == 'triangular_squeezed':
        loc_tria = np.random.default_rng().triangular(0, 0.5, 1, num_customers)
        loc_sque = []
        for i in range(num_customers):
            accept = False
            while accept == False:
                loc = np.random.random()
                threshold = np.random.random()
                if threshold < loc:
                    loc_sque.append(loc)
                    accept = True
        loc_sque = np.array(loc_sque).flatten()
        locations = np.vstack((loc_tria, loc_sque)).T

    elif loc_distr == 'side_central':
        locations = []
        for i in range(num_customers):
            accept = False
            while accept == False:
                loc_x = np.random.random()
                loc_y = np.random.random()
                threshold = np.random.random()
                if threshold < (1 - abs(loc_x - 0.5) / (0.5)) * (abs(loc_y - 0.5) / (0.5)):
                    locations.append([loc_x, loc_y])
                    accept = True
        locations = np.array(locations)

    elif loc_distr == 'cavity_dispersion':
        locations = []
        for i in range(num_customers):
            accept = False
            while accept == False:
                loc_x = np.random.random()
                loc_y = np.random.random()
                threshold = np.random.random()
                if threshold < (abs(loc_x - 0.5) / (0.5)) * (abs(loc_y - 0.5) / (0.5)):
                    locations.append([loc_x, loc_y])
                    accept = True
        locations = np.array(locations)

    elif loc_distr == 'truncated_exponential':
        a = -np.log(np.random.random(num_customers))/1.5
        b = -np.log(np.random.random(num_customers))/1.5
        loc_x = (a - np.floor(a))
        loc_y = (b - np.floor(b))
        locations = np.vstack((loc_x, loc_y)).T
        
    # Rotate and shuffle location order to mix double distributions and x/y
    locations = rotate(locations, np.random.randint(4))
    locations = np.take(locations,np.random.permutation(locations.shape[0]),axis=0,out=locations)
    locations = np.take(locations,np.random.permutation(locations.shape[1]),axis=1,out=locations)
    return np.around(locations, 2)



################################ HELPER FUNCTIONS ###################################



def rotate(locations, num_rotations):
    """Rotates the locations in a the area (since some distribution focus on one side/corner)."""
    for i in range(num_rotations):
        x = locations[:,0].copy()
        y = locations[:,1].copy()
        locations[:,0] = y
        locations[:,1] = -1*x+1
    return locations