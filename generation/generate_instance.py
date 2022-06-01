""" A module for generating single routing instances (variants include TSP, CVRP, and CVRPTW)."""

import routing
import generation
import numpy as np


def generate_instance(
    variant='cvrptw',            # (str)   - routing variant (tsp, vcrp, or cvrptw)
    distance_metric='euclidean', # (str)   - distance metric (euclidean or manhattan)
    num_customers=None,          # (int)   - number of locations
    depot_pos=None,              # (str)   - depot position (options in locations.py)
    loc_distr=None,              # (str)   - locations distribution (options in locations.py)
    dem_distr=None,              # (str)   - demands distribution (options in demands.py)
    cap_ratio=None,              # (float) - number of customers whose demand a vehcile can cover on average
    st_distr=None,               # (str)   - service times distribution (options in service_times.py)
    tw_share=None,               # (str)   - share of customers with time windows
    tw_center_distr=None,        # (str)   - time windows distribution (options in time_windows.py)
    tw_width_distr=None          # (str)   - time windows distribution (options in time_windows.py)
):  # -> Returns: routing instance object
    """Generates a single routing instance."""
    
    ### SETUP GENERATION
    instance = routing.routingInstance(variant=variant, distance_metric=distance_metric)
    gen_params = {}
    
    ### GENERATE TSP CHARACTERISTICS
    if instance.variant in ['tsp', 'cvrp', 'cvrptw']:
        # Service area
        area, side_ratio, lx, ly = generation.generate_area()
        # Number of customers
        if not num_customers:
            num_customers = np.random.randint(low=20, high=100)
        # Depot and customer locations
        instance.locations, depot_pos, loc_distr = generation.generate_locations(
            num_customers+1, depot_pos, loc_distr, lx, ly)
        # Distance matrix
        instance.compute_distance_matrix()
        # Save generation parameters
        for variable in ['area', 'side_ratio', 'lx', 'ly', 
                         'num_customers', 'depot_pos', 'loc_distr']:
            gen_params[variable] = eval(variable)
    
    ### GENERATE CVRP CHARACTERISTICS
    if variant in ['cvrp', 'cvrptw']:
        # Generate demands
        instance.demands, dem_distr = generation.generate_demands(
            num_customers, dem_distr, instance.locations, lx, ly)
        dem_avg = np.sum(instance.demands) / num_customers
        # How many customer demands can one vehicle cover on average
        if not cap_ratio:
            cap_ratio = round(np.random.default_rng().uniform(0.02, 0.8), 4)
        avg_route_size = round(max(
            np.max(instance.demands) / dem_avg, # lower bound (s.t. cap_avg>=dem_max) since cust. can only receive 1 vehicle.
            cap_ratio*num_customers), 4)
        cap_avg = np.ceil(avg_route_size * dem_avg)
        num_vehicles = num_customers # num_vehicles is assumed to be free to ensure feasibility. The solver reduces this.
        # Vehicle capacities
        capacities = np.ones(num_vehicles) * cap_avg
        instance.vehicle_capacities = capacities.astype(int)
        # Save generation parameters
        for variable in ['dem_distr', 'cap_ratio', 'avg_route_size']:
            gen_params[variable] = eval(variable)
        
    ### GENERATE CVRPTW CHARACTERISTICS
    if variant in ['cvrptw']:
        # Length of time horizon
        possible_rounds = round(np.random.default_rng().triangular(0.7071, 2, 8), 4) # lower bound: 2*np.sqrt(2)/4 (=2*diagonal)
        tw_width_depot = round(possible_rounds * (2*lx + 2*ly), 4)
        # Service times
        instance.service_times, st_distr = generation.generate_service_times(
            num_customers, st_distr, tw_width_depot, instance.demands)
        # Share of customers with time_windows
        if tw_share is None:
            tw_share = round(np.random.default_rng().triangular(0.25, 1, 1), 4)
        # Time windows
        instance.time_windows, tw_center_distr, tw_width_distr = generation.generate_time_windows(
            num_customers, tw_center_distr, tw_width_distr, tw_width_depot, 
            tw_share, instance.distance_matrix[0][1:], instance.service_times[1:])
        # Max and wait time
        instance.determine_max_time()
        instance.determine_wait_time()
        # Save generation parameters
        for variable in ['possible_rounds', 'st_distr', 'tw_share', 'tw_center_distr', 'tw_width_distr']:
            gen_params[variable] = eval(variable)
        
    ### INSTANTIATE AND RETURN
    instance.gen_params = gen_params
    return instance
