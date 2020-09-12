import re

def _flatten_dictionary(d):
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

def _merge(d):
    '''
        Merge fields by name of leaf node (i.e. last element in "_" delimited key)
        (e.g. 'Task_$0_Logs_$0_Name' -> 'Name')
        Input:
            d - flattened dictionary (i.e. leaf nodes only)
        Output:
            Aggregate leaf nodes which same suffix
    '''
    # get natural ordering of leaf nodes (i.e. want to append values by natural ordering)
    ordered = dict(sorted(fd.items(), key = lambda x: tuple(re.split(r'(\d+)', x[0])), reverse=False))
    result = {}
    for k, v in ordered.items():
        result.setdefault(k.split("_")[-1], []).append(v)
    return result

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
    table = _repeat(_merge(_flatten_dictionary(d)))
    
    return pd.DataFrame(table)
