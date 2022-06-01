""" A package to generate routing instances.

Author: Jens Mueller
Python Version: 3.9.7

MODULES:

    generate_instance.py - Generate a single routing instance (variants include TSP, CVRP, and CVRPTW).
    generate_dataset.py  - Generate a full dataset of routing instances.
    area.py              - Generate a service area of varying size and shape.
    locations.py         - Generate a set of locations following one of several possible distributions.
    demands.py           - Generate a set of demands following one of several possible distributions.
    time_windows.py      - Generate a set of time windows following one of several possible distributions.
    service_times.py     - Generate a set of service times following one of several possible distributions.
    features.py		 - Extract features from routing instances
    third_party/	 - Third party scripts
"""

from .generate_instance import generate_instance
from .generate_dataset import generate_dataset
from .area import generate_area
from .locations import generate_locations
from .demands import generate_demands
from .time_windows import generate_time_windows
from .service_times import generate_service_times
from .features import *
from .third_party.MinimumBoundingBox import MinimumBoundingBox 