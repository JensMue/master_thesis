""" A module containing useful helper functions for the routing module."""

import routing
import numpy as np


def compute_distance_matrix(locations, distance_metric='euclidean'):
    """Computes the distance matrix given some locations and a distance metric."""
    if distance_metric == 'euclidean':
        distance_matrix = np.linalg.norm(locations[:, None, :] - locations[None, :, :], axis=-1)
    elif distance_metric == 'manhattan':
        distance_matrix = np.sum(np.abs(locations[:, None, :] - locations[None, :, :]), axis=-1)
    distance_matrix = np.around(distance_matrix, decimals=2, out=None)
    return distance_matrix
    
    
def get_route_distances(routes, distance_matrix):
    """Extracts the accumulated distances over the nodes in each solution route."""
    distances = []
    for route in routes:
        route_distances = []
        current_stop = route[0]
        route_distance = 0
        route_distances.append(route_distance)
        for i in range(1,len(route)):
            next_stop = route[i]
            current_distance = distance_matrix[current_stop][next_stop]
            route_distance += current_distance
            route_distances.append(route_distance)
            current_stop = next_stop
        distances.append(route_distances)
    return distances


def get_route_loads(routes, demands):
    """Extracts the accumulated vehcile loads over the nodes in each solution route."""
    loads = []
    for route in routes:
        route_loads = []
        route_load = 0
        for stop in route:
            route_load += demands[stop]
            route_loads.append(route_load)
        loads.append(route_loads)
    return loads


def print_solution(instance, verbose=1): # verbose: (0=Nothing, 1=solution distance, 2=detailed solution)
    """Prints solution to a routing instance on the console."""
    if verbose >= 1:
        num_vehicles_used = sum([1 for route in instance.solution_routes if len(route) > 2])
        print(f'Solution distance: {round(instance.solution_distance, 2)} (vehicles used: {num_vehicles_used})\n')
    if verbose == 2:
        # tsp
        if instance.variant == 'tsp':
            output = 'Route:\n'
            for stop in instance.solution_routes[0][:-1]:
                output += f' {stop} ->'
            output += f' {instance.solution_routes[0][-1]}\n'
            print(output)
        # cvrp
        elif instance.variant == 'cvrp':
            if not hasattr(instance, 'distance_matrix'):
                instance.compute_distance_matrix(instance.variant)
            instance.solution_distances = get_route_distances(instance.solution_routes, instance.distance_matrix)
            instance.solution_loads = get_route_loads(instance.solution_routes, instance.demands)
            for vehicle_id in range(len(instance.solution_routes)):
                output = 'Route for vehicle {0} (distance: {1}, load: {2}):\n'.format(
                    vehicle_id, 
                    instance.solution_distances[vehicle_id][-1], 
                    instance.solution_loads[vehicle_id][-1])
                for num_stop in range(len(instance.solution_routes[vehicle_id][:-1])):
                    output += ' {0} Load({1}) -> '.format(
                        instance.solution_routes[vehicle_id][num_stop], 
                        instance.solution_loads[vehicle_id][num_stop])
                output += ' {0} Load({1})\n'.format(
                    instance.solution_routes[vehicle_id][-1],
                    instance.solution_loads[vehicle_id][-1])
                if instance.solution_distances[vehicle_id][-1] > 0:
                    print(output)
        # cvrptw
        elif instance.variant == 'cvrptw':
            if not hasattr(instance, 'distance_matrix'):
                instance.compute_distance_matrix(instance.variant)
            instance.solution_distances = get_route_distances(instance.solution_routes, instance.distance_matrix)
            instance.solution_loads = get_route_loads(instance.solution_routes, instance.demands)
            for vehicle_id in range(len(instance.solution_routes)):
                output = 'Route for vehicle {0} (distance={1}, load={2}, time={3}):\n'.format(
                    vehicle_id, 
                    round(instance.solution_distances[vehicle_id][-1], 2),
                    instance.solution_loads[vehicle_id][-1], 
                    instance.solution_times[vehicle_id][-1][1])
                for num_stop in range(len(instance.solution_routes[vehicle_id][:-1])):
                    output += ' {0} (d{1},l{2},t{3}) ->'.format(
                        instance.solution_routes[vehicle_id][num_stop],
                        int(instance.solution_distances[vehicle_id][num_stop]),
                        int(instance.solution_loads[vehicle_id][num_stop]),
                        int(instance.solution_times[vehicle_id][num_stop][0]))
                output += ' {0} (d{1},l{2},t{3})\n'.format(
                    instance.solution_routes[vehicle_id][-1],
                    int(instance.solution_distances[vehicle_id][-1]),
                    int(instance.solution_loads[vehicle_id][-1]),
                    int(instance.solution_times[vehicle_id][-1][1]))
                if instance.solution_distances[vehicle_id][-1] > 0:
                    print(output)
    return None


def find_connections(locations, routes):
    """Creates a connections matrix for each route (1=connected, o=not connected)."""
    connections = np.zeros((len(routes), locations.shape[0], locations.shape[0]))
    for k in range(len(routes)):
        for i in range(len(routes[k])-1):
            connections[k][routes[k][i]][routes[k][i+1]] = 1
    return connections


