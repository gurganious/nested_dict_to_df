# 9/17/2020
# Add default mapping

import pandas as pd

def _flatten_dict(d):
    '''
        Flattens dictionary to leaf nodes only
    '''
    def flatten(x, prefix = ''):
        ' helper function to recursively flatten dictionary to leaf nodes only '
        if isinstance(x, dict):
            for a in x:
                flatten(x[a], prefix + a + '_')
        elif isinstance(x, list):
            for i, k in enumerate(x):
                flatten(k, prefix + '$' + str(i) + '_')
        else:
            out[prefix[:-1]] = x

    out = {}
    flatten(d)
    return out


def _get_base(k):
    '''
        Find key with numeric separators removed
    '''
    if "_" in k:
        s = '_'.join(k.split('_')[::2])  # even indexes (i.e. 'Task_$0_Name -> 'Task_Name')
    else:
        s = k
    return s

def _get_base_keys(keys):
    '''
        Set of keys with numeric separators removed
        (use set since not unique without numeric separators)
    '''
    # Find keys with numeric separators removed
    basekeys = set(_get_base(k) for k in keys)
        
    return sorted(basekeys, key=lambda t: (len(t), t.lower()))

def _update_maps(k, forward_, reverse_):
    '''
       :param k   - key
       :forward_  - forward mapping of current name to new name
       :reverse_  - reverse key mapping
       
       Used by _shortest_keys to update mapping of keys to new names
        Set of keys with numeric separators removed
        (use set since not unique without numeric separators)
    '''
    arr = k.split('_')
    ok = False
    for i in range(1, len(arr)+1):
        # Going backwards thorugh k, find unique key which has not
        # been used yet in out dictionary
        suffix = '_'.join(arr[-i:])
        if not suffix in forward_:
            break
            
    while suffix in reverse_:
        suffix += '_'
   
    forward_[k] = suffix
    reverse_[suffix] = k
                   
    return forward_, reverse_

def _shortest_keys(keys, default_map = None):
    '''
        :param keys        - keys from flattened dictionary
        :param default_map - default mapping of base key name to new names
        
        Maps keys to shorter form so they can be used for column names
        Based upon smallest key suffix that does not overlap with other keys
        suffix can be only separated at '_' boundaries in string (i.e. so on whole words)
    '''
    if default_map is None:
        default_map = {}
        
    # Convert flattened key names to basic names by removing 
    # numeric sepators such as
    # 'Task_$1_Logs_$0_name' -> 'Task_Logs_name'
    base_keys = _get_base_keys(keys)
  
    # Init forward and reverse lookup
    forward_ = {k:v for k, v in default_map.items()}
    reverse_ = {v:k for k, v in forward_.items()}
    
    # Compute keys
    for k in base_keys:
        if k not in default_map:
            _update_maps(k, forward_, reverse_)
            
    return forward_, reverse_

def _merge_keys(fd, default_map = None):
    '''
        :param fd     - flattened dictionary
        :default_map - default map of base keys to new key words
        :return      - dictionary with items aggregated by key
        
        Merges compatible keys in flattened dictionary
        Example:
           {
             'Task_$0_Name': 1,
             'Task_$1_Name' : 2
           }
        becomes:
            {
             'Name': [1, 2]
           }
        where 'Name' is the shortest unique suffix name (ignore _$d_)
    '''
    
    # Find shortest key set for flattened keys (i.e. shortest names for compatible key set)
    forward_, reverse_ = _shortest_keys(fd.keys(), default_map)
    
    # Aggregate items together based upon having the same key
    out = {}
    for k, value in fd.items():
        # Base key (skipping numbers i.e. )
        base = _get_base(k)  # i.e. 'Task_$1_Logs_$2_name' -> 'Task_Logs_name'
        
        suffix = forward_[base]
        
        # Add to column values for shortened key
        out.setdefault(suffix, []).append(value)
            
    return out

def _repeat(d):
    '''
        Repeats elements in dictionary list values to all have the same length (assume fixed multiple)
        Inputs:
            d - dictionary containing keys and values (each a list)
        Output:
            dictionary with values updated
    '''
    # determine length of largest list
    max_ = max(len(v) for k, v in d.items())
    
    # Repeat each item in list (i.e. [item for item in v for _ in range(max_//len(v))] )
    return {k:[item for item in v for _ in range(max_//len(v))] for k, v in d.items()}
    
def nested_dict_to_df(d, default_map = None):
    '''
        Converts a nested dictionary to dataframe
    '''
    # Convert nested dictionary to table form
    table = _repeat(_merge_keys(_flatten_dict(d), default_map))
    
    return pd.DataFrame(table)
   
def show_default_name_map(d):
    '''
        Shows the default mapping of names for dictionary
    '''
    fd = _flatten_dict(d)
    
    forward, _ = _shortest_keys(fd)
    
    for k, v in forward.items():
        print(f'{k} : {v}')
        
