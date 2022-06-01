""" A module for saving routing instances."""

import numpy as np
import pickle
import json
import copy


def save_instance(
    instance,           # (object) - routingInstance object
    path,               # (str)    - path to save to
    filename,           # (str)    - name to save as
    filetype='pickle',  # (str)    - file-type to save as (pickle, json, or txt)
    reduce_size=False   # (bool)   - reduce file-size by ignoring distance_matrix and more
):  # -> Returns None, but saves intance to a file
    """Saves a routing instance to a file."""
    
    # Create a copy to modify without changing the original instance.
    inst_tosave = copy.deepcopy(instance)
    
    # Reduce instance size.
    if reduce_size:
        unwanted_attr = ['distance_matrix', 'solution_distances', 'solution_loads']
        for attr in unwanted_attr:
            if hasattr(inst_tosave, attr):
                delattr(inst_tosave, attr)
    
    # Save as pickle.
    if filetype == 'pickle':
        with open(path+filename+'.pickle', 'wb') as f:
            pickle.dump(inst_tosave, f)
    
    # Save as json.
    elif filetype == 'json':
        instance_dict = make_json_serializable(inst_tosave.__dict__)
        with open(path+filename+'.json', 'w', encoding='utf-8') as f:
            json.dump(instance_dict, f, ensure_ascii=False, indent=4)

    # Save as txt.
    elif filetype == 'txt':
        instance_dict = make_json_serializable(inst_tosave.__dict__)
        with open(path+filename+'.txt', 'w') as f:
            json.dump(instance_dict, f)
            
    return None


def make_json_serializable(instance_dict):
    """Makes the attributes of a routing instance json-serializable (mainly numpy objects)."""
    for key in instance_dict.keys():
        if isinstance(instance_dict[key], np.ndarray):
            instance_dict[key] = instance_dict[key].tolist()
        elif isinstance(instance_dict[key], np.int32):
            instance_dict[key] = float(instance_dict[key])
        elif isinstance(instance_dict[key], np.int64):
            instance_dict[key] = float(instance_dict[key])
    return instance_dict