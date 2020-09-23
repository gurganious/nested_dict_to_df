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
def _get_base(k, pattern = re.compile(r'^\$\d+$')):
    '''
        Find key with numeric separators removed
    '''
    return '_'.join(x for x in k.split('_') if not pattern.match(x))

def _seq_numbers(k, pattern = re.compile(r'(?<=\$)\d+')):
    '''
        Gets numbers in key pattern associated with sequences 
        i.e. 'Task_$0_Name_$1 -> (0, 1)
    '''
    return tuple([int(x) for x in pattern.findall(k)])

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

def _parent(k):
    '''
        Parent node based upon key
        i.e. Jobs_TASKS_TASKId -> Jobs_TASKS
    
    '''
    return '_'.join(_get_base(k).split('_')[:-1])  # Not including the last item
    
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
                    my_prefix = prefix + a
                    out.append((_get_base(my_prefix), _seq_numbers(my_prefix), x[a]))
                else:
                    flatten(x[a], prefix + a + '_')
        elif isinstance(x, list):
            for i, k in enumerate(x):
                flatten(k, prefix + '$' + str(i) + '_')
        else:
            # Place common leaf values in list
            my_prefix = prefix[:-1]
            out.append((_get_base(my_prefix), _seq_numbers(my_prefix), x))

    out = []
    flatten(d)
    
    # Sort keys in natural order
    return sorted(out, key = lambda kv: (_depth(kv[0]), kv[0].lower()))


    
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
   
def _group_fields(fd):
    '''
        group fields from flattened dictioary which is a list of:
        (base_name, seq_number array, value)
    '''
    def _join(df1, df2):
        '''
            Outer merge join of two dataframes
        '''
        if df1 is None:
            return df2
        if df2 is None:
            return df1
        # Use merge based uopn the minimum of the two widths
        merge_key = f'{Merge_Key}'
        min1 = min(len(x) for x in df1[merge_key])
        min2 = min(len(x) for x in df2[merge_key])
        if min1 == min2:
            result = merge(df1, df2, on = merge_key)
        elif min1 < min2:
            # Merge key use the shorter of two tuples
            df2[Merge_Key] = df2[Merge_Key].apply(lambda x: x[:min1])
            result = merge(df1, df2, on = merge_key)
        else:
            # Merge key use the shorter of two tuples
            df1[Merge_Key] = df1[Merge_Key].apply(lambda x: x[:min2])
            result = merge(df1, df2, on = merge_key)
        return result
    
    def _stack(df1, df2):
        '''
            vertically stack two data frames
        '''
        if df1 is None:
            return df2
        if df2 is None:
            return df1
        return pd.concat([df1, df2], ignore_index=True)
    
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

    merge_key = f"{Merge_Key}"
    df_parents = []
    for k0, v0 in groupby(fd, lambda x: _parent(x[0])):
        df_series = []
        for k1, v1 in groupby(v0, lambda x: x[0]):
            # Create DataFrame of each Series and stack
            # Map triplets to DataFrames
            # Base, Seq, value
            # Tuples to Dictionary
            dics = [{base:[val], merge_key:[seq]} for base, seq, val in v1]
            
            # Dictionary to DataFrames
            # Stack dataframes for series
            df = _reduce(_stack, (DataFrame(d) for d in dics))
            
            df_series.append(df)
            
        # Join series
        df_parent = _reduce(_join, df_series)
        
        df_parents.append(df_parent)
    # Join parents
    df_result = _reduce(_join, df_parents)
    
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
    fd = _flatten_dict(d, *no_expansion_columns)      # Flattened dictionaries
    return _group_fields(fd)                          # Merge dictionaries using DataFrame outer join and concat
 
