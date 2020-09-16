# nested_dict_to_df
Converts nested dictionary to pandas dataframe

CSV is easily obtained by converting the dataframe to CSV using Dataframe to_csv(...) function

**Usage**

    # To get DataFrame from dictionary d
    df = nested_dictionary_to_df(d)

    # To get CSV string:
    s = df.set_index(df.columns[0]).to_csv()

**Example 1**

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
    
 **Example 2**
 
 *Input Dictionary*
 
 ```
     d = {
            "job": 1,
            "name": "jobname",
            "status": "jobstatus",
            "Type": "jobtype",
            "Task": [
              {
                "Taskid": 100,
                "name": "Taskname",
                "status": "taskstatus",
                "Type": "Tasktype",
                "Logs": [
                  {
                    "name": "logname",
                    "error": "/errorlog/file"
                  },
                  {
                    "name": "logname1",
                    "error": "/errorlog/file1"
                  },
                  {
                    "name": "logname2",
                    "error": "/errorlog/file2"
                  }
                ],
              "statuscomment": "",
              "path": null
              },
              {
                "Taskid": 200,
                "name": "Taskname1",
                "status": "taskstatus1",
                "Type": "Tasktype1",
                "Logs": [
                  {
                    "name": "2logname",
                    "error": "/errorlog/file"
                  },
                  {
                    "name": "2logname1",
                    "error": "/errorlog/file1"
                  },
                  {
                    "name": "2logname2",
                    "error": "/errorlog/file2"
                  }
                ],
              "statuscomment": "",
              "path": null                
              }              
            ]
    }
 ```
 
*Output df*

```
	job	Type	name	status	Task_Type	Task_name	path	Task_path	Taskid	Task_status	Task_Taskid	Logs_name	error	statuscomment	Logs_error	Task_statuscomment
0	1	jobtype	jobname	jobstatus	Tasktype	Taskname	None	None	100	taskstatus	200	logname	/errorlog/file		/errorlog/file	
1	1	jobtype	jobname	jobstatus	Tasktype	Taskname	None	None	100	taskstatus	200	logname1	/errorlog/file		/errorlog/file	
2	1	jobtype	jobname	jobstatus	Tasktype	Taskname	None	None	100	taskstatus	200	logname2	/errorlog/file1		/errorlog/file1	
3	1	jobtype	jobname	jobstatus	Tasktype1	Taskname1	None	None	100	taskstatus1	200	2logname	/errorlog/file1		/errorlog/file1	
4	1	jobtype	jobname	jobstatus	Tasktype1	Taskname1	None	None	100	taskstatus1	200	2logname1	/errorlog/file2		/errorlog/file2	
5	1	jobtype	jobname	jobstatus	Tasktype1	Taskname1	None	None	100	taskstatus1	200	2logname2	/errorlog/file2		/errorlog/file2	
 ```
*Output CSV*

```
job,Type,name,status,Task_Type,Task_name,path,Task_path,Taskid,Task_status,Task_Taskid,Logs_name,error,statuscomment,Logs_error,Task_statuscomment
1,jobtype,jobname,jobstatus,Tasktype,Taskname,,,100,taskstatus,200,logname,/errorlog/file,,/errorlog/file,
1,jobtype,jobname,jobstatus,Tasktype,Taskname,,,100,taskstatus,200,logname1,/errorlog/file,,/errorlog/file,
1,jobtype,jobname,jobstatus,Tasktype,Taskname,,,100,taskstatus,200,logname2,/errorlog/file1,,/errorlog/file1,
1,jobtype,jobname,jobstatus,Tasktype1,Taskname1,,,100,taskstatus1,200,2logname,/errorlog/file1,,/errorlog/file1,
1,jobtype,jobname,jobstatus,Tasktype1,Taskname1,,,100,taskstatus1,200,2logname1,/errorlog/file2,,/errorlog/file2,
1,jobtype,jobname,jobstatus,Tasktype1,Taskname1,,,100,taskstatus1,200,2logname2,/errorlog/file2,,/errorlog/file2,
```
