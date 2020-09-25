import json
import pandas as pd
from pandas import DataFrame, merge
from itertools import groupby
import re

#################################################################################
# Constants
#################################################################################
Merge_Key = '_$mergekey'
Field_Separator = '.'  # can be set to other values such as "."

#################################################################################
# Helper functions
#################################################################################
def _get_base(k, pattern = re.compile(r'^\$\d+$')):
    '''
        Find key with numeric separators removed
    '''
    return Field_Separator.join(x for x in k.split(Field_Separator) if not pattern.match(x))

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
    arr = k.split(Field_Separator)
    for i in range(1, len(arr)+1):
        # Going backwards thorugh k, find unique key which has not
        # been used yet in out dictionary
        suffix = Field_Separator.join(arr[-i:])
        if not suffix in reverse_:
            break
            
    while suffix in reverse_:
        suffix += Field_Separator
   
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
    return len(_get_base(k).split(Field_Separator))

def _parent(k):
    '''
        Parent node based upon key
        i.e. Jobs_TASKS_TASKId -> Jobs_TASKS
    
    '''
    return Field_Separator.join(_get_base(k).split(Field_Separator)[:-1])  # Not including the last item
    
#################################################################################
# Core functions
#################################################################################
def _flatten_dict(d, max_depth = -1):
    '''
        Flattens dictionary to leaf nodes only
    '''
    def flatten(x, prefix = '', depth = 0):
        ' helper function to recursively flatten dictionary to leaf nodes only '
        if isinstance(x, dict):
            for a in x:
                if max_depth != -1 and depth >= max_depth:
                    my_prefix = prefix + a
                    out.append((_get_base(my_prefix), _seq_numbers(my_prefix), x[a]))
                else:
                    flatten(x[a], prefix + a + Field_Separator, depth + 1)
        elif isinstance(x, list):
            for i, k in enumerate(x):
                flatten(k, prefix + '$' + str(i) + Field_Separator, depth)
        else:
            # Place common leaf values in list
            my_prefix = prefix[:-1]
            out.append((_get_base(my_prefix), _seq_numbers(my_prefix), x))

    out = []
    flatten(d)
    
    # Sort keys in natural order
    return sorted(out, key = lambda kv: (_depth(kv[0]), kv[0].lower()))
   
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
        merge_key = Merge_Key
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

    merge_key = Merge_Key
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
    df_result = df_result.drop(Merge_Key, 1)
    
    # Minimize names
    rename_map = _minimize_names(df_result.columns)
    df_result.rename(columns = rename_map, inplace = True)
    
    return df_result
        
#################################################################################
# Main function
#################################################################################
def nested_dict_to_df(d, max_depth = -1):
    '''
        Converts a nested dictionary to dataframe
    '''
    # Convert nested dictionary to table form
    fd = _flatten_dict(d, max_depth)      # Flattened dictionaries
    return _group_fields(fd)                          # Merge dictionaries using DataFrame outer join and concat
 

