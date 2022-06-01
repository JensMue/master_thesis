""" A package to create, solve, plot, and work with routing instances.

Author: Jens Mueller
Python Version: 3.9.7

MODULES:

    instance.py - Class to represent several types of routing problems (variants include TSP, CVRP, and CVRPTW).
    solve.py    - Solves a given routing problem (based on Google's open source project Operations Research Tools (ORTools)).
    plot.py     - Plots a given routing problem.
    save.py     - Saves a given routing problem or dataset (including benchmarks).
    load.py     - Loads a given routing problem or dataset (including benchmarks).
    utils.py    - Contains useful helper functions (e.g. computation of the distance matrix)
"""

from .instance import routingInstance
from .solve import solve_instance, solve_dataset
from .plot import plot_instance
from .save import save_instance
from .load import *
from .utils import *


