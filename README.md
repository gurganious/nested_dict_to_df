# nested_dict_to_df
Converts nested dictionary to pandas dataframe

CSV is easily obtained by converting the dataframe to CSV using Dataframe to_csv(...) function

**Usage**

    # To get DataFrame
    df = nested_dictionary_to_df(d)

    # To get CSV use:
    df.set_index(df.columns[0]).to_csv()

**Example:**

*Input Dictionary:*

    d = {'Task': [{'Logs': [{'Name': 'log1', 'error': 'errorname1'},
                        {'Name': 'log2', 'error': 'errorname2'}],
               'TaskName': 'Taskname1',
               'Taskid': 1},
              {'Logs': [{'Name': 'log1', 'error': 'errorname1'},
                        {'Name': 'log2', 'error': 'errorname2'}],
               'TaskName': 'Taskname2',
               'Taskid': 2}],
     'job': 1,
     'jobname': 'name'}
 
    df = nested_dictionary_to_df(d)
    
 *Output DataFrame:*
 
        Name       error   TaskName  Taskid  job jobname
    0  log1  errorname1  Taskname1       1    1    name
    1  log2  errorname2  Taskname1       1    1    name
    2  log1  errorname1  Taskname2       2    1    name
    3  log2  errorname2  Taskname2       2    1    name

*Output CSV*

    job,jobname,Taskid,TaskName,Name,error
    1,name,1,Taskname1,log1,errorname1
    1,name,1,Taskname1,log2,errorname2
    1,name,2,Taskname2,log1,errorname1
    1,name,2,Taskname2,log2,errorname2
