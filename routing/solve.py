""" A module for solving several variants of routing problems."""

import routing
import numpy as np
import copy
import time
import os
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2


def solve_instance(
    instance,                    # (object) - routing instance to be solved
    first_solution='AUTOMATIC',  # (str)    - initial solution strategy (all options below)
    local_search=None,           # (str)    - local search strategy (all options below)
    time_limit=1,                # (int)    - search time limit in seconds
    scaling=True,                # (bool)   - avoid inaccuracies from integer rounding by ortools
    verbose=1                    # (int)    - print solution to console (0=Nothing, 1=solution distance, 2=detailed solution)
):  # -> Returns None, but updates the instances solution attributes
    """Finds a solution for a given routing instance (minimizing the total distance)."""
    
    # If distance matrix is not available -> Compute it.
    if not hasattr(instance, 'distance_matrix'):
        instance.compute_distance_matrix()
    
    # Scale instances to avoid inaccuracies from integer rounding by ortools.
    distance_matrix, time_windows, service_times, max_time, wait_time = scale_instance(instance, scaling)
    
    # Create the routing index manager and routing model.
    manager = pywrapcp.RoutingIndexManager(instance.distance_matrix.shape[0], instance.compute_num_vehicles(), instance.depot)
    model = pywrapcp.RoutingModel(manager)
    
    # Create and register a callback function for distances from the distance matrix.
    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distance_matrix[from_node][to_node]
    distance_callback_index = model.RegisterTransitCallback(distance_callback)
    
    # Account for demands and vehicle capacities.
    if instance.variant in ['cvrp', 'cvrptw']:
        # Create and register a callback function for demands.
        def demand_callback(from_index):
            """Returns the demand of the node."""
            # Convert from routing variable Index to demands NodeIndex.
            from_node = manager.IndexToNode(from_index)
            return instance.demands[from_node]
        demand_callback_index = model.RegisterUnaryTransitCallback(demand_callback)
        # Add Capacity constraint.
        model.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,  # null capacity slack
            instance.vehicle_capacities,  # vehicle maximum capacities
            True,  # start cumul to zero
            'Capacity') # dimension name
    
    # Account for time windows and service times.
    if instance.variant in ['cvrptw']:
        # Create and register a callback function for total-times (transit-times + service-times).
        def transit_time_callback(from_index, to_index):
            """Returns the travel time between the two nodes."""
            # Convert from routing variable Index to time matrix NodeIndex.
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return distance_matrix[from_node][to_node] # previously: time_matrix
        #transit_time_callback_index = routing.RegisterTransitCallback(transit_time_callback)
        def service_time_callback(from_index, to_index):
            """Returns the service time of the node."""
            # Convert from routing variable Index to service_time NodeIndex.
            from_node = manager.IndexToNode(from_index)
            return service_times[from_node]
        #service_time_callback_index = routing.RegisterTransitCallback(service_time_callback)
        def total_time_callback(from_index, to_index):
            """The time function we want is both transit time and service time."""
            # Convert from routing variable Index to total time matrix NodeIndex.
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return int(transit_time_callback(from_node, to_node) + service_time_callback(from_node, to_node))
        total_time_callback_index = model.RegisterTransitCallback(total_time_callback)
        # Add Time Windows constraint.
        model.AddDimension(
            total_time_callback_index,
            int(wait_time),  # allow waiting time
            int(max_time),  # maximum time per vehicle
            False,  # Don't force start cumul to zero.
            'Time') # dimension name
        time_dimension = model.GetDimensionOrDie('Time')
        # Add time window constraints for each location except depot.
        for location_idx, time_window in enumerate(time_windows):
            if location_idx == instance.depot:
                continue
            index = manager.NodeToIndex(location_idx)
            time_dimension.CumulVar(index).SetRange(int(time_window[0]), int(time_window[1]))
        # Add time window constraints for each vehicle start node.
        depot_idx = instance.depot
        for vehicle_id in range(instance.num_vehicles):
            index = model.Start(vehicle_id)
            time_dimension.CumulVar(index).SetRange(
                int(time_windows[depot_idx][0]),
                int(time_windows[depot_idx][1]))
        # Instantiate route start and end times to produce feasible times.
        for i in range(instance.num_vehicles):
            model.AddVariableMinimizedByFinalizer(time_dimension.CumulVar(model.Start(i)))
            model.AddVariableMinimizedByFinalizer(time_dimension.CumulVar(model.End(i)))
    
    # Define cost (distance callback) of each arc, homogeneous for all vehicles.
    model.SetArcCostEvaluatorOfAllVehicles(distance_callback_index)
    
    # Set search strategy.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters = set_search_params(search_parameters, first_solution, local_search, time_limit)
    
    # Solve the problem.
    solution = model.SolveWithParameters(search_parameters)
    
    # Format the solution and update the instance.
    if solution == None:
        if verbose >= 1:
            print('No solution found')
        return instance
    instance.solution_distance = solution.ObjectiveValue() 
    instance.solution_routes = format_routes(solution, model, manager)
    if instance.variant in ['cvrptw']:
        instance.solution_times = format_times(solution, instance.solution_routes, time_dimension, distance_matrix)
    if scaling:
        instance = scale_back_solution(instance)
    
    # Print solution and return.
    routing.print_solution(instance, verbose)
    return None


def solve_dataset(
    path_from,      # (str) - path to load instances from
    path_to,        # (str) - path to save instances to
    filetype,       # (str) - file-type to load (also possible: 'solomon' to solve benchmark)
    first_solution, # (str) - initial solution strategy (all options below)
    local_search,   # (str) - local search strategy (all options below)
    time_limit_m,   # (int) - time limit multiplier depending on number of customers in instance
    verbose,        # (bool)- report progress 
    num_inst='all'  # (str/int) - 'all': solve all instances in path, int: how many instances to solve
):  # -> Returns None, but saves the solved instances to path_to
    """Loads a dataset, solves it, then saves it."""
    t0 = time.time()
    solved = 0
    # Loop through files
    filelist = os.listdir(path_from)
    for f in filelist:
        if num_inst != 'all':
            if solved >= num_inst:
                break
        # Load and solve Solomon
        if filetype == 'solomon':
            if f.endswith(".txt"):
                filename = f[:-4]
                for num in [25, 50, 100]:
                    instance = routing.load_benchmark_instance(filename, num_customers=num, path=path_from)
                    instance.solve(first_solution=first_solution, local_search=local_search, 
                                   time_limit=int(time_limit_m*num), verbose=0)
                    solved+=1
                    # save instance
                    instance.save(path_to, filename+'.'+str(num)+first_solution[:3]+local_search[:3]+str(time_limit_m), 
                                  filetype='pickle', reduce_size=True)
                    instance.save(path_to, filename+'.'+str(num)+first_solution[:3]+local_search[:3]+str(time_limit_m), 
                                  filetype='txt', reduce_size=True)
                    if verbose:
                        print(f"Saved: {filename+'.'+str(num)+first_solution[:3]+local_search[:3]+str(time_limit_m)}, time: {time.time()-t0}")  
        # Load and solve other
        elif f.endswith('.'+filetype):
            filename = f[:-len(filetype)-1]
            instance = routing.load_instance(path_from+f)
            instance.solve(first_solution=first_solution, local_search=local_search, 
                           time_limit=int(time_limit_m*instance.locations.shape[0]), verbose=0)
            instance.first_solution = first_solution
            instance.local_search = local_search
            instance.time_limit_m = time_limit_m
            solved+=1
            # save instance
            instance.save(path_to, filename+first_solution[:3]+local_search[:3]+str(time_limit_m), filetype='pickle', reduce_size=True)
            instance.save(path_to, filename+first_solution[:3]+local_search[:3]+str(time_limit_m), filetype='txt', reduce_size=True)
            if verbose:
                print(f'Saved: {filename+first_solution[:3]+local_search[:3]+str(time_limit_m)}, time: {time.time()-t0}')
    return None



############################### HELPER FUNCTIONS BELOW ##########################################



def scale_instance(instance_toscale, scaling):
    """Scales distance and time parameters to avoid inaccuracies from integer rounding by ortools."""
    # Create a copy to scale parameters for solving without changing the original instance.
    instance = copy.deepcopy(instance_toscale)
    # Scale distance matrix.
    distance_matrix = instance.distance_matrix
    if scaling:
        distance_matrix *= 100
    distance_matrix = distance_matrix.astype(int)
    # Scale time attributes.
    if instance.variant == 'cvrptw':
        time_windows = instance.time_windows
        service_times = instance.service_times
        max_time = instance.max_time
        wait_time = instance.wait_time
        if scaling:
            time_windows *= 100
            service_times *= 100
            max_time *= 100
            wait_time *= 100
        time_windows = time_windows.astype(int)
        service_times = service_times.astype(int)
        max_time = int(max_time)
        wait_time = int(wait_time)
        return distance_matrix, time_windows, service_times, max_time, wait_time
    else:
        return distance_matrix, None, None, None, None

    
def set_search_params(search_parameters, first_solution, local_search, time_limit, log=True):
    """Sets the initial solution strategy, the local search strategy, and the search time."""
    # first solution strategy
    if first_solution == 'PATH_CHEAPEST_ARC':
        search_parameters.first_solution_strategy = (routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    elif first_solution == 'SAVINGS':
        search_parameters.first_solution_strategy = (routing_enums_pb2.FirstSolutionStrategy.SAVINGS)
    elif first_solution == 'SWEEP':
        search_parameters.first_solution_strategy = (routing_enums_pb2.FirstSolutionStrategy.SWEEP)
    elif first_solution == 'CHRISTOFIDES':
        search_parameters.first_solution_strategy = (routing_enums_pb2.FirstSolutionStrategy.CHRISTOFIDES)
    elif first_solution == 'PARALLEL_CHEAPEST_INSERTION':
        search_parameters.first_solution_strategy = (routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION)
    else:
        search_parameters.first_solution_strategy = (routing_enums_pb2.FirstSolutionStrategy.AUTOMATIC)
    # local search strategy
    if local_search == 'AUTOMATIC':
        search_parameters.local_search_metaheuristic = (routing_enums_pb2.LocalSearchMetaheuristic.AUTOMATIC)
    elif local_search == 'GUIDED_LOCAL_SEARCH':
        search_parameters.local_search_metaheuristic = (routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    elif local_search == 'SIMULATED_ANNEALING':
        search_parameters.local_search_metaheuristic = (routing_enums_pb2.LocalSearchMetaheuristic.SIMULATED_ANNEALING)
    elif local_search == 'TABU_SEARCH':
        search_parameters.local_search_metaheuristic = (routing_enums_pb2.LocalSearchMetaheuristic.TABU_SEARCH)
    elif local_search == 'OBJECTIVE_TABU_SEARCH':
        search_parameters.local_search_metaheuristic = (routing_enums_pb2.LocalSearchMetaheuristic.OBJECTIVE_TABU_SEARCH)
    # time limit
    if time_limit:
        search_parameters.time_limit.seconds = time_limit
    # log
    search_parameters.log_search = log    
    #return search_parameters
    return search_parameters


def format_routes(solution, model, manager): 
    """Extracts vehicle routes from the solution object."""
    routes = []
    for vehicle_id in range(model.vehicles()):
        index = model.Start(vehicle_id)
        route = [manager.IndexToNode(index)]
        while not model.IsEnd(index):
            index = solution.Value(model.NextVar(index))
            route.append(manager.IndexToNode(index))
        routes.append(route)
    return routes # -> Returns 2d array whose i,j entry is the jth location visited by vehicle i.
    

def format_times(solution, routes, dimension, distance_matrix):
    """Extracts the possible start time range at each location in the solution."""
    solution_times = []
    for route in routes:
        route_times = []
        for stop in route[:-1]:
            dim_var = dimension.CumulVar(stop)
            route_times.append([solution.Min(dim_var), solution.Max(dim_var)])
        last_stop_time = solution.Max(dim_var) + float(distance_matrix[stop][route[-1]])
        route_times.append([last_stop_time, last_stop_time])
        solution_times.append(route_times)
    return solution_times # -> Returns 3d array ([i][j][0] is the earliest start time at node j on route i (latest=1)).
    

def scale_back_solution(instance):
    """Converts the solution distance- and time-parameters back to the original scale."""
    instance.solution_distance /= 100
    if instance.variant == 'cvrptw':
        solution_times_scaled = [[[start/100, end/100] for start, end in route] for route in instance.solution_times]
        instance.solution_times = solution_times_scaled
    return instance
