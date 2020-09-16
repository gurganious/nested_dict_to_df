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

def _shortest_keys(keys):
    '''
        Maps keys to shorter form so they can be used for column names
        Based upon smallest key suffix that does not overlap with other keys
        suffix can be only separated at '_' boundaries in string (i.e. so on whole words)
    '''
    base_keys = _get_base_keys(keys)
  
    # Compute forward lookup
    forward_ = {}
    for k in base_keys:
        if "_" in k:
            arr = k.split('_')
            for i in range(1, len(arr)+1):
                # Going backwards thorugh k, find unique key which has not
                # been used yet in out dictionary
                suffix = '_'.join(arr[-i:])
                if not suffix in forward_:
                    forward_[suffix] = k
                    break
            
        else:
            forward_[k] = k
            
    # Form reverse lookup
    reverse_ = {v:k for k, v in forward_.items()}
    
    return forward_, reverse_

def _merge_keys(fd):
    '''
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
    
        Inputs:
          fd - Flattened dictionary (by _flatten_dict)
    '''
    
    # Find shortest key set for flattened keys (i.e. shortest names for compatible key set)
    forward_, reverse_ = _shortest_keys(fd.keys())
    
    # Aggregate items together based upon having the same key
    out = {}
    for k, value in fd.items():
        # Base key (skipping numbers i.e. )
        base = _get_base(k)  # i.e. 'Task_$1_Logs_$2_name' -> 'Task_Logs_name'
        
        suffix = reverse_[base]
        
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
    
def nested_dict_to_df(d):
    '''
        Converts a nested dictionary to dataframe
    '''
    # Convert nested dictionary to table form
    table = _repeat(_merge_keys(_flatten_dict(d)))
    
    return pd.DataFrame(table)
