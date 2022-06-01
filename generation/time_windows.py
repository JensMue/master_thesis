""" A module for generating the time windows in a routing instance."""

import numpy as np
import random


def generate_time_windows(
    num_customers,   # (int)   - number of time windows to be generated
    tw_center_distr, # (str)   - time windows center distribution (options below)    
    tw_width_distr,  # (str)   - time windows width distribution (options below)
    tw_width_depot,  # (float) - maximum route duration
    tw_share,        # (float) - share of customers with time windows
    depot_dist,      # (np.array) - distances between customers and the depot (1st row in distance matrix)
    service_times     # (np.array) - service times
):  # Returns: tuple of np.array with time windows as well as generation parameters
    """Generates a set of time windows for an instance following one of several distributions."""

    # Time window center distributions
    if not tw_center_distr:
        tw_center_distr = random.choice([
            'uniform', 'uniform', 'uniform', 
            'one_peak', 
            'two_peaks', 
            'three_peaks', 
            'discrete'
        ])    
    # Time window width distributions
    if not tw_width_distr:
        tw_width_distr = random.choice([
            'uniform', 
            'short', 
            'medium', 
            'long',                                           
            'unitary',
        ])
    # Set depot time window
    tw_depot = np.around(np.array([0, tw_width_depot]), 4)

    # Generate tw centers and widths for customers with time windows
    num_discrete = np.random.randint(2, 10) # only relevant for discrete distribution
    tw_centers = generate_tw_centers(
        tw_depot, tw_center_distr, num_customers, depot_dist, service_times, num_discrete)
    tw_widths = generate_tw_widths(
        tw_depot, tw_width_distr, num_customers, tw_center_distr, num_discrete)    
     
    # Compute time windows
    time_windows = [
        [round(tw_centers[i]-tw_widths[i]/2, 4), 
         round(tw_centers[i]+tw_widths[i]/2, 4)] 
        for i in range(num_customers)]
    
    # Remove customers without time windows
    for i in range(num_customers):
        threshold = np.random.random()
        if tw_share < threshold:
            time_windows[i] = list(tw_depot)
    
    # Add depot time window
    time_windows = np.array(time_windows)
    time_windows = np.concatenate((np.array([tw_depot]), time_windows))
    
    return time_windows, tw_center_distr, tw_width_distr
    
    
    
def generate_tw_centers(tw_depot, tw_center_distr, num_customers, depot_dist, service_times, num_discrete):
    """Generates time window centers."""
    
    if tw_center_distr in ['uniform', 'one_peak', 'two_peaks', 'three_peaks']:
        
        tw_centers = []
        for i in range(num_customers):
            
            earliest = tw_depot[0] + depot_dist[i]
            latest = max(tw_depot[1] - depot_dist[i] - service_times[i], earliest+1)
            # Explanation: - In very few specific cases, latest might be lower than earlierst.
            #              - This makes the instance infeasible to solve.
            #              - The above maximum just ensures the sampling procedure works anyways.
            tw_center_range = latest - earliest

            if tw_center_distr == 'uniform':
                tw_centers.append(np.random.uniform(earliest, latest))

            elif tw_center_distr == 'one_peak':
                tw_centers.append(np.random.default_rng().triangular(earliest, (earliest+latest)/2, latest))

            elif tw_center_distr == 'two_peaks':
                peaks = 2
                tw_centers.append(earliest + np.random.randint(0, peaks) * tw_center_range/peaks 
                    + np.random.default_rng().triangular(0, tw_center_range/2, tw_center_range)/peaks)

            elif tw_center_distr == 'three_peaks':
                peaks = 3
                tw_centers.append(earliest + np.random.randint(0, peaks) * tw_center_range/peaks 
                    + np.random.default_rng().triangular(0, tw_center_range/2, tw_center_range)/peaks)
                
    elif tw_center_distr == 'discrete':
        tw_centers = [(tw_depot[0] + (np.random.randint(0, num_discrete) + 0.5) * (tw_depot[1]-tw_depot[0])/num_discrete) 
                      for i in range(num_customers)]
        
    return np.array(tw_centers)
    

    
def generate_tw_widths(tw_depot, tw_width_distr, num_customers, tw_center_distr, num_discrete):
    """Chooses time window lengths for a number of customers."""
    tw_width_depot = tw_depot[1]-tw_depot[0]
    
    if tw_width_distr == 'uniform':
        tw_widths = np.random.default_rng().uniform(
            0*tw_width_depot, 0.6*tw_width_depot, num_customers)
    
    elif tw_width_distr == 'short':
        tw_widths = np.random.default_rng().triangular(
            0*tw_width_depot, 0.1*tw_width_depot, 0.2*tw_width_depot, num_customers)

    elif tw_width_distr == 'medium':
        tw_widths = np.random.default_rng().triangular(
            0.2*tw_width_depot, 0.3*tw_width_depot, 0.4*tw_width_depot, num_customers)
    
    elif tw_width_distr == 'long':
        tw_widths = np.random.default_rng().triangular(
            0.4*tw_width_depot, 0.5*tw_width_depot, 0.6*tw_width_depot, num_customers)
        
    elif tw_width_distr == 'unitary':
        if tw_center_distr == 'discrete': 
            tw_widths = np.ones(num_customers) * tw_width_depot/num_discrete
        else:
            tw_widths = np.ones(num_customers) * np.random.uniform(0.01, 0.6) * tw_width_depot
        
    return tw_widths
