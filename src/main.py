import pandas as pd
import re
from itertools import groupby

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

def _natural_sort_key(s, pattern = re.compile(r'[^\d]+|\d+')):
    '''
        Splits with numbers and non-numbers into list sublists
        of numbers only and non-numbers only
        (i.e. used for sort key to obtain for natural sorting string)
    '''
    return [int(x) if x.isnumeric() else x for x in pattern.findall(s)] 
    
def _groupby_key(kv):
    return re.split(r'_\$\d+_', kv[0])

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
    # Sort dictionary key, values based upon keys (approximate natural sort)
    fd_tups = sorted(fd.items(), key = lambda kv: (len(kv[0]),) + tuple(_natural_sort_key(kv[0])))

    # Group keys by placing keys together regardless of index into original list
    # i.e. splitting on r'_$\d+_'
    g = groupby(fd_tups, key = _groupby_key)
    
    # Aggregate items together based upon having the same key, ignoring list index
    out = {}
    for k, values in g:
        # k will be lists such as ['Task', 'TaskName']
        for i in range(1, len(k)+1):
            # Going backwards thorugh k, find unique key which has not
            # been used yet in out dictionary
            prefix = '_'.join(k[-i:])
            if not prefix in out:
                break
        else:
            raise Exception("Sorry, cold not find unique prefix for key")
            
        out[prefix] = [value[1] for value in values]
    
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
