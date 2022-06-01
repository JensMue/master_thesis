""" A module for plotting routing instances."""

import routing
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import seaborn as sns

    
def plot_instance(
    instance,        # (object) - routing instance to be plotted
    title=None,      # (str)    - plot title (optional)
    solved=False,    # (bool)   - include the solution in the plot
    details=None,    # (str)    - 'loc_ids': plot node ids, 'all': plot loads and times
    scaled=False,    # (bool)   - orignal area shape (True) or square area (False)
    fig_size=(4, 4), # (tuple)  - figure size
    node_size=50,    # (int)    - location node size
    font_size=5,     # (int)    - details font size
    c_depot='darkgreen',        # (str) - depot node color (good: 'darkgreen', 'red')
    c_cust='cornflowerblue'     # (str) - customer node color (good: 'cornflowerblue', 'darkorange')
):  # -> Returns None, but shows the plot.
    """Plots a routing instance."""
    
    # Check if locations are given.
    if not hasattr(instance, 'locations'):
        print('\nNo locations are given for plotting.')
        return None
    elif instance.locations is None:
        print('\nNo locations are given for plotting.')
        return None
    
    # Set color scheme.
    cmap = cm.get_cmap('Set1') # route colors
    alpha_depot = 1.0
    alpha_cust = 0.85
    ec_depot = 'black'
    ec_cust = 'black'
    
    # Setup the plot.
    fig = plt.figure(figsize=fig_size)
    if title:
        plt.title(title)
    if scaled:
        plt.axis('equal')
    
    # Plot location nodes.
    locs = instance.locations
    num_locs = instance.locations.shape[0]
    for i in range(num_locs):    
        if i == instance.depot:
            plt.scatter(locs[i][0], locs[i][1], c=c_depot, s=3*node_size, alpha=alpha_depot, ec=ec_depot)
            plt.text(locs[i][0], locs[i][1], "Depot", fontsize=2*font_size)
        else:
            plt.scatter(locs[i][0], locs[i][1], c=c_cust, s=node_size, alpha=alpha_cust, ec=ec_cust)

    # Plot details like ids, demands, and/or time windows.
    if details:
        if instance.variant == 'tsp':
            for i in range(num_locs):    
                if i != instance.depot:
                    plt.text(locs[i][0], locs[i][1], i, fontsize=font_size)
        elif instance.variant == 'cvrp':
            for i in range(num_locs):    
                if i != instance.depot:
                    if details == 'loc_ids':
                        plt.text(locs[i][0], locs[i][1], i, fontsize=font_size)
                    elif details == 'all':
                        plt.text(locs[i][0], locs[i][1], f'id: {i}, dem: {instance.demands[i]}', fontsize=font_size)
        elif instance.variant == 'cvrptw':
            tws = instance.time_windows
            for i in range(num_locs):    
                if i != instance.depot:
                    if details == 'loc_ids':
                        plt.text(locs[i][0], locs[i][1], i, fontsize=font_size)
                    elif details == 'all':
                        plt.text(locs[i][0], locs[i][1], 
                                 f'{i}:[{instance.demands[i]},{instance.service_times[i]},\n{int(tws[i][0])}-{int(tws[i][1])}]',
                                 fontsize=font_size)

    # Plot routes.
    if not solved or not hasattr(instance, 'solution_routes'):
        plt.show()
        return
    connections = routing.find_connections(locs, instance.solution_routes)        
    num_used_vehicles = -1
    for k in range(instance.compute_num_vehicles()):
        if len(instance.solution_routes[k]) > 2:
            num_used_vehicles += 1
        for i in range(num_locs):
            for j in range(num_locs):
                if i != j and connections[k][i][j] == 1:
                    plt.plot([locs[i][0], locs[j][0]], [locs[i][1], locs[j][1]], c=cmap(num_used_vehicles))
    
    # Show plot.
    plt.show()
    return None
