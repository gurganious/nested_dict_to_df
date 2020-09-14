def _get_leaves(item, key = None, out = None):
    '''
        Aggregate into a flattened dictionary based leaves of elements in nested dictionary
        
        Inputs:
            item - item currently looping over
            key - key to use in flattened dictionary
        Output:
            out - flattened dictionary
    '''
    if out is None:
        out = {}
        
    if isinstance(item, dict):
        for k, v in item.items():
            _get_leaves(v, k, out)
        return out
    elif isinstance(item, list):
        for i in item:
            _get_leaves(i, key, out)
        return out
    else:
        out.setdefault(key, []).append(item)
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
    table = _repeat((_get_leaves(d)))
    
    return pd.DataFrame(table)

