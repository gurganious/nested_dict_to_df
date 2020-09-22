# 9/22/2020
from itertools import groupby
import pandas as pd
from pandas import DataFrame, merge
import re

#################################################################################
# Constants
#################################################################################
Merge_Key = '_$mergekey'

#################################################################################
# Helper functions
#################################################################################
def _get_iters(s, pattern = re.compile(r'[^\d]+|\d+')):
    '''
        List of numerical list iterations in field name
        i.e. a_$1_x_$2 -> [1, 2]
    '''
    return [int(x) if x.isnumeric() else x for x in pattern.findall(s)] 
    
def _first_iter(k):
    '''
        First number in key token i.e. a_$1_b_$0 -> 1
    '''
    return _get_iters(k)[1]

def _natural_sort_key(s):
    '''
        Sort key for strings based upon number of digits and
        ordering.
        Splits with numbers and non-numbers into list sublists
        of numbers only and non-numbers only
        (i.e. s = "Jobs_$0_Task_$0_Logs
              returns [5, 'Jobs_$', 0, '_Task_$', 0, '_Logs']")
    '''
    return [_depth(s), _get_base(s), ] + _get_iters(s)

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

def _minimize_names(names):
    '''
        Finds set of minimum width names by removing prefix as long as names don't collide
    '''
    # Init forward and reverse lookup
    forward_ = {}
    reverse_ = {}
    
    # Compute keys
    for k in names:
        _update_maps(k, forward_, reverse_)
            
    return forward_

def _depth(k):
    '''
        Depth measure by number of underscores in base name
    '''
    return len(_get_base(k).split('_'))

def _first_iter(k):
    '''
        First number in key token i.e. a_$1_b_$0 -> 1
    '''
    return _get_iters(k)[1]
    

def _sort_key(kv):
    '''
    Key function used to sort flattened dictionary
    '''
    t = _get_iters(kv[0])
    if len(t) <= 1:
        return (_depth(kv[0]),)
    else:
        t = t[1::2]  # list indexes only
        #t = t[:-1]   # leave out last element
        return  (_depth(kv[0]),) + tuple(t)
    
def _group_key(kv):
    '''
    Key function used to group flattened dictionary
    '''
    if isinstance(kv, list):
        kv = kv[0]
    t = _get_iters(kv[0])
    if len(t) <= 1:
        return (_depth(kv),)
    else:
        t = t[1::2]  # list indexes only
        t = t[:-1]   # leave out last element
        return  (_depth(kv[0]),) + tuple(t)
    
    
#################################################################################
# Core functions
#################################################################################
def _flatten_dict(d, *no_expansion_columns):
    '''
        Flattens dictionary to leaf nodes only
    '''
    def flatten(x, prefix = ''):
        ' helper function to recursively flatten dictionary to leaf nodes only '
        if isinstance(x, dict):
            for a in x:
                if a in no_expansion_columns:
                    #out.setdefault(_get_base(prefix + a), []).append(x[a])
                    out[prefix + a] = str(x[a])
                else:
                    flatten(x[a], prefix + a + '_')
        elif isinstance(x, list):
            for i, k in enumerate(x):
                flatten(k, prefix + '$' + str(i) + '_')
        else:
            # Place common leaf values in list
            #out.setdefault(prefix[:-1], []).append(x)
            out[prefix[:-1]] = x

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
    sorted_fd = sorted(fd.items(), key = _sort_key)
    g = groupby(sorted_fd, _group_key)
    # (2, 1) [('Jobs_$0_job', [1]), ('Jobs_$1_job', [2]), ('Jobs_$0_jobname', ['jobname']), ('Jobs_$1_jobname', ['jobname']), 

    out = {}
    for kval, subgroup in g:
        # Outer dictionary is just the length of path for group i.e. 'Jobs_job' has path length 2
        out[kval] = {}   
            
        subgroup = list(subgroup)
        for v in subgroup:
            v = list(v)
            out[kval].setdefault(_get_base(v[0]), []).append(v[1])
        
        # Add merge key based upon first item in group
        first = set()
        for v in subgroup:
            v = list(v)
            base = _get_base(v[0])
            if not first or base in first:
                out[kval].setdefault(f'{Merge_Key}', []).append(_first_iter(v[0]))
                first.add(base)
           
    return out

def _form_dataframes(dics):
    '''
        Forms Dataframes of items with similar number of values in item (by count)
    
    '''
    def _join(df1, df2):
        '''
            Outer merge join of two dataframes
        '''
        if df1 is None:
            return df2
        if df2 is None:
            return df1
        return merge(df1, df2, on = Merge_Key)
    
    def _stack(df1, df2):
        '''
            vertically stack two data frames
        '''
        if df1 is None:
            return df2
        if df2 is None:
            return df1
        return pd.concat([df1, df2], ignore_index=True)


    # Group dics by depth
    k_lst, df_result, df_current, df_accum = None, None, None, None
    
    for i, (k, d) in enumerate(dics.items()):
        # Current dataframe from dictionary
        df_current = DataFrame(d)
        
        if not k_lst:
            k_lst = k[0]     # index of current group
            df_accum = df_current
        elif  k[0] == k_lst:
            # Vertical stack DataFrames in same group
            df_accum =_stack(df_accum, df_current)
            
        else:
            # Merge current group with previous merge groups
            df_result = _join(df_result, df_accum)
            
            # Reset accumulate of items in same group
            df_accum = df_current
            k_lst = k[0]
   
        if i == len(dics.items()) - 1:
            df_result = _join(df_result, df_accum)
            
    # Drop merge key column
    df_result = df_result.drop(f'{Merge_Key}', 1)
    
    # Minimize names
    rename_map = _minimize_names(df_result.columns)
    df_result.rename(columns = rename_map, inplace = True)
    
    return df_result
            
#################################################################################
# Main function
#################################################################################
def nested_dict_to_df(d, *no_expansion_columns):
    '''
        Converts a nested dictionary to dataframe
    '''
    # Convert nested dictionary to table form
    fd = _flatten_dict(d, *no_expansion_columns)            # Flattened dictionaries
    dics = _form_dictionaries(fd)                          # Aggregate nodes along same path based upon names
    return _form_dataframes(dics)                          # Merge dictionaries using DataFrame outer join and concat
 
