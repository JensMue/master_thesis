""" A module for generating the service times in a routing instance."""

import numpy as np
import random
    

def generate_service_times(
    num_customers,  # (int)      - number of service times to be generated (incl. depot)
    st_distr,       # (str)      - service times distribution (options below)
    tw_width_depot, # (float)    - maximum route duration
    demands         # (np.array) - customer demands (only required for proportional distribution)
):  # Returns: tuple of np.array with service times as well as generation parameters
    """Generate service times."""
    
    # Service times distributions
    if not st_distr:
        st_distr = random.choice([
            'unitary', 
            'uniform', 
            'proportional'
        ])
    
    if st_distr == 'unitary': # all customers have the same service time
        service_times = np.ones(num_customers) * np.random.uniform(0.001 * tw_width_depot, 0.1 * tw_width_depot)
        service_times = np.concatenate((np.array([0]), service_times)) # add depot
        
    elif st_distr == 'uniform': # all customers varying service times
        service_times = np.random.uniform(0.001 * tw_width_depot, 0.1 * tw_width_depot, num_customers)
        service_times = np.concatenate((np.array([0]), service_times)) # add depot
        
    elif st_distr == 'proportional': # all customers have a service time proportional to their demand
        service_times = (demands/np.max(demands)) * (np.random.uniform(0.001, 0.1)*tw_width_depot)
        
    return service_times.astype(int), st_distr