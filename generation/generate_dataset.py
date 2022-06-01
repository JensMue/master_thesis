""" A module for generating a full dataset of routing instances."""

import generation


def generate_dataset(
    path,                # (str)  - path to save generated instances to
    num_instances,       # (int)  - number of instances to be generated
    start_count=1,       # (int)  - number to start naming instances with
    variant='cvrptw',    # (str)  - routing variant (tsp, vcrp, or cvrptw)
    verbose=True,        # (bool) - print generation progress to console
    solved=True          # (bool) - solve the generated instances
):  # -> Returns None, but saves the generated instances to path
    """Generate a full dataset of routing instances from a variety of distributions."""
    
    # continue until desired number of instances was generated
    for i in range(num_instances):
        
        #generate instance
        instance = generation.generate_instance(variant=variant)
        instance.name = variant+'%06d' % (start_count + i)
        instance.gen_params['name'] = instance.name
        
        # solve instance
        if solved:
            instance.solve(
                first_solution='PATH_CHEAPEST_ARC',
                local_search='GUIDED_LOCAL_SEARCH',
                time_limit=int(instance.gen_params['num_customers'] * 3),
                verbose=0)
            instance.gen_params['has_solution'] = hasattr(instance, 'solution_distance')
            if instance.gen_params['has_solution']:
                instance.gen_params['num_vehicles_used'] = sum([1 for route in instance.solution_routes if len(route) > 2])

        # Save instance.
        instance.save(path, instance.name, filetype='pickle', reduce_size=True)
        instance.save(path, instance.name, filetype='txt', reduce_size=True)

        # print progress
        if verbose:
            print(f"Saved: {instance.name}")
    
    return None