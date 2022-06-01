""" A module for generating a service area."""

import numpy as np
import random


def generate_area(
    min_size=10_000,    # (int) - minimum service area size
    max_size=1_000_000, # (int) - maximum service area size
    min_ratio=1,        # (int) - minimum service area side ratio
    max_ratio=5         # (int) - maximum service area side ratio
):  # -> Returns: tuple of area characteristics
    """Generates the service area for an instance."""

    # Service area (size): sampled uniformly between 10,000 and 100,000 (could be km2).
    area = np.random.uniform(low=min_size, high=max_size)

    # Side ratio: sampled from an exponential distribution.
    scale = 0.45 # chosen s.t. P[1<side_ratio<2]=90% (more square shaped) (<1.5=67%)
    side_ratio = np.minimum(np.random.exponential(scale=scale)+min_ratio, max_ratio)

    # Side lengths (can then be computed area size and side ratio)
    long_side = np.sqrt(area*side_ratio)
    short_side = np.sqrt(area/side_ratio)
    lx = random.choice([long_side, short_side])
    ly = area / lx
    
    return round(area, 4), round(float(side_ratio), 4), round(float(lx), 4), round(float(ly), 4)