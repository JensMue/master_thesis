""" A module containing the routingInstance class and its methods."""

import routing
import numpy as np
from deepdiff import DeepDiff


class routingInstance:
    """A class to represent a routing instance."""
    
    @classmethod
    def fromdict(cls, d):
        """Constructs a routing instance from a dictionary."""
        return cls(**d)
    
    def __init__(self, **kwargs):
        """Initializes a routing instance from a list of allowed attributes."""
        allowed_kwargs = {
            'name',                 # (str)      - can be used as an identifier 
            'variant',              # (str)      - type of routing problem (tsp, cvrp, or cvrptw)
            'locations',            # (np.array) - array of 2D locations
            'distance_metric',      # (str)      - distance metric (euclidean or manhattan)
            'distance_matrix',      # (np.array) - matrix of distances between the locations
            'demands',              # (np.array) - demands at each location
            'vehicle_capacities',   # (np.array) - available capacities for each vehicle
            'service_times',        # (np.array) - service times at each location
            'time_windows',         # (np.array) - time window start- and end-points at each location
            'max_time',             # (float)    - maximum solution time (usually the depot time window)
            'wait_time',            # (float)    - maximum wait time at each location
            'solution_distance',    # (float)    - total distance of all routes in the solution
            'solution_routes',      # (list)     - routes that were found to minimize the solution distance
            'solution_times',       # (list)     - possible start times at each location in the solution
            'solution_loads',       # (list)     - accumulated vehicle loads in the solution routes
            'solution_distances',   # (list)     - accumulated vehicle distances in the solution routes
            'gen_params',           # (dict)     - generation parameters (automatically generated)
            'num_vehicles',         # (int)      - number of vehicles available to the solver
            'first_solution',       # (str)      - initial solution strategy (all options in routing/solve.py)
            'local_search',         # (str)      - local search strategy (all options in routing/solve.py)
            'time_limit_m'          # (int)      - search time limit multiplier per customer in instance
        }
        self.__dict__.update((k, v) for k, v in kwargs.items() if k in allowed_kwargs)
        self.depot = 0
        if hasattr(self, 'variant'):
            if self.variant == 'cvrptw':
                self.determine_max_time()
                self.determine_wait_time() 
    
    def __eq__(self, other, verbose=False):
        """Checks if two routing instances are equal."""
        if self.__class__ != other.__class__:
            if verbose: print('Different class')
            return False
        eq = DeepDiff(self.__dict__, other.__dict__)
        if eq != {}:
            if verbose: print(eq)
            return False
        return True
    
    
    def solve(self, first_solution='AUTOMATIC', local_search=None, time_limit=1, scaling=True, verbose=1):
        """Solves the routing instance (for details see solve.py)."""
        return routing.solve_instance(self, first_solution, local_search, time_limit, scaling, verbose)
    
    
    def save(self, path, filename, filetype='pickle', reduce_size=False):
        """Saves the routing instance (for details see save.py)."""
        return routing.save_instance(self, path, filename, filetype, reduce_size)
    
    
    def plot(self, title=None, solved=False, details=None, scaled=False, 
             fig_size=(4, 4), node_size=50, font_size=5, c_depot='darkgreen', c_cust='cornflowerblue'):
        """Plots the routing instance (for details see plot.py)."""
        return routing.plot_instance(self, title, solved, details, scaled, fig_size, node_size, font_size, c_depot, c_cust)
    
    
    def compute_distance_matrix(self, distance_metric=None):
        """Computes the distance matrix for the instance (for details see utils.py)."""
        if distance_metric:
            self.distance_metric = distance_metric
        self.distance_matrix = routing.compute_distance_matrix(self.locations, self.distance_metric)
        return self.distance_matrix
    
    
    def compute_num_vehicles(self):
        """Computes the number of vehicles for the instance."""
        if self.variant == 'tsp':
            self.num_vehicles = 1
        elif hasattr(self, 'vehicle_capacities'):
            self.num_vehicles = len(self.vehicle_capacities)
        else:
            self.num_vehicles = 0
        return self.num_vehicles
    
    
    def determine_max_time(self):
        """Determines the maximum time horizon."""
        if hasattr(self, 'max_time'):
            return self.max_time
        elif hasattr(self, 'time_windows'):
            self.max_time = self.time_windows[0][1] # depot time window
            return self.max_time
        else:
            return None
        
        
    def determine_wait_time(self):
        """Determines the maximum waiting time."""
        if hasattr(self, 'wait_time'):
            return self.wait_time
        elif hasattr(self, 'max_time'):
            self.wait_time = self.max_time.copy()
            return self.wait_time
        else:
            return None
