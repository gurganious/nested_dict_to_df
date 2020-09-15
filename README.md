# nested_dict_to_df
Converts nested dictionary to pandas dataframe

CSV is easily obtained by converting the dataframe to CSV using Dataframe to_csv(...) function

**Usage**

    # To get DataFrame from dictionary d
    df = nested_dictionary_to_df(d)

    # To get CSV string:
    s = df.set_index(df.columns[0]).to_csv()

**Example:**

*Input Dictionary:*

    d = {'Task': [{'Logs': [{'Name': 'log1', 'error': 'errorname1'},
                    {'Name': 'log2', 'error': 'errorname2'}],
           'Name': 'Taskname1',
           'Taskid': 1},
          {'Logs': [{'Name': 'log1', 'error': 'errorname1'},
                    {'Name': 'log2', 'error': 'errorname2'}],
           'TaskName': 'Taskname2',
           'Taskid': 2}],
 'job': 1,
 'jobname': 'name'}
 
    df = nested_dict_to_df(d)
    
 *Output DataFrame:*
 
         job jobname       Name  Taskid   TaskName Logs_Name       error
    0    1    name  Taskname1       1  Taskname2      log1  errorname1
    1    1    name  Taskname1       1  Taskname2      log2  errorname2
    2    1    name  Taskname1       2  Taskname2      log1  errorname1
    3    1    name  Taskname1       2  Taskname2      log2  errorname2

*Output CSV*

    job,jobname,Name,Taskid,TaskName,Logs_Name,error
    1,name,Taskname1,1,Taskname2,log1,errorname1
    1,name,Taskname1,1,Taskname2,log2,errorname2
    1,name,Taskname1,2,Taskname2,log1,errorname1
    1,name,Taskname1,2,Taskname2,log2,errorname2
