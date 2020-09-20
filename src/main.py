from itertools import groupby
from pandas import DataFrame, merge
import re

#################################################################################
# Helper functions
#################################################################################
def _natural_sort_key(s, pattern = re.compile(r'[^\d]+|\d+')):
    '''
        Sort key for strings based upon number of digits and
        ordering.
        Splits with numbers and non-numbers into list sublists
        of numbers only and non-numbers only
        (i.e. s = "Jobs_$0_Task_$0_Logs
              returns [5, 'Jobs_$', 0, '_Task_$', 0, '_Logs']")
    '''
    t = [int(x) if x.isnumeric() else x for x in pattern.findall(s)] 
    return [_get_base(s), ] + t

def _get_base(k):
    '''
        Find key with numeric separators removed
    '''
    if "$" in k:
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
    for i in range(1, len(arr)+1):
        # Going backwards thorugh k, find unique key which has not
        # been used yet in out dictionary
        suffix = '_'.join(arr[-i:])
        if not suffix in reverse_:
            break
            
    while suffix in reverse_:
        suffix += '_'
   
    forward_[k] = suffix
    reverse_[suffix] = k
                   
    return forward_, reverse_

#################################################################################
# Core functions
#################################################################################
def _flatten_dict(d, no_expansion_columns):
    '''
        Flattens dictionary to leaf nodes only
    '''
    def flatten(x, prefix = ''):
        ' helper function to recursively flatten dictionary to leaf nodes only '
        if isinstance(x, dict):
            for a in x:
                if a in no_expansion_columns:
                    out.setdefault(_get_base(prefix + a), []).append(x[a])
                else:
                    flatten(x[a], prefix + a + '_')
        elif isinstance(x, list):
            for i, k in enumerate(x):
                flatten(k, prefix + '$' + str(i) + '_')
        else:
            # Place common leaf values in list
            out.setdefault(_get_base(prefix[:-1]), []).append(x)

    out = {}
    flatten(d)
    
    # Sort keys in natural order
    out = dict(sorted(out.items(), key=lambda kv: _natural_sort_key(kv[0].lower())))
    
    return out

def _form_dictionaries(fd):
    '''
        Forms dictionaries of similar keys from flattened dictionary
    
    '''
    # Find forward lookup table for unique names that base_keys (i.e. path to leaf name) can be shorted too
    # Maps base name to shorter name i.e. Jobs_job - > job
    base_keys = _get_base_keys(fd.keys())
    forward_ = {}
    reverse_ = {}
    for k in base_keys:
        _update_maps(k, forward_, reverse_)
        
    # Group keys by number of separators (i.e. length of path to leaf)
    sorted_fd = sorted(fd.items(), key = lambda kv: len(kv[1]))
    g = groupby(sorted_fd, lambda kv: len(kv[1]))
    # groups of (2, [('Jobs_job', [1, 2]), ('Jobs_jobname', ['jobname', 'jobname']), etc.

    out = {}
    for cnt, subgroup in g:
        # Outer dictionary is just the length of path for group i.e. 'Jobs_job' has path length 2
        out[cnt] = {'_$mergekey': [1]*cnt}   # inject a merge key for use by DataFrame join in _form_dataframes
        for v in subgroup:
            v = list(v)
            out[cnt][forward_[v[0]]] = v[1]
    
    return out

def _form_dataframes(groups_by_count):
    '''
        Forms Dataframes of items with similar number of values in item (by count)
    
    '''
    def _join(df1, df2):
        return merge(df1, df2, on = '_$mergekey')
    
    def _reduce(function, iterable, initializer=None):
        ' code equivalent of functools reduces'
        # In case you don't have functools.reduce
        it = iter(iterable)
        if initializer is None:
            value = next(it)
        else:
            value = initializer
        for element in it:
            value = function(value, element)
        return value

    # Convert each dictionary to DataFrame which have the same lenght
    dfs = (DataFrame(dic) for cnt, dic in  groups_by_count.items())
   
    # Perform outer join on DataFrame (i.e. merging different lengths)
    df = _reduce(_join, dfs)
    
    # Drop merge key column
    df = df.drop('_$mergekey', axis = 1)

    return df
    
#################################################################################
# Main function
#################################################################################
def nested_dict_to_df(d, *no_expansion_columns):
    '''
        Converts a nested dictionary to dataframe
    '''
    # Convert nested dictionary to table form
    fd = _flatten_dict(d, no_expansion_columns)            # Flattened dictionaries
    dics = _form_dictionaries(fd)                          # Merge based upon path length to leaf nodes
    return _form_dataframes(dics)                          # Merge dictionaries using DataFrame outer join
   
