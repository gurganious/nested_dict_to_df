# nested_dict_to_df
Converts nested dictionary to pandas dataframe

CSV is easily obtained by converting the dataframe to CSV using Dataframe to_csv(...) function

**Usage**

    # Output Dataframe from dictionary d
    # mod_map is modifications of default column name mappings (optional)
    df = nested_dictionary_to_df(d, leaf1, leafe2, ...)

    leaf1, leaf2, ... is optional names of nodes not to expand in recursion in determining the leaf nodes
    
    # Output CSV string:
    s = df.set_index(df.columns[0]).to_csv()

**Simple Example**

d = {
    "a": 1,
    "b": 2,
    "c":[1, 2]
}

*Run*

     df = nested_dictionary_to_df(d)
     
*Output*

```
	a	b	c
0	1	2	1
1	1	2	2
```

**Example**

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

*Run*

    df = nested_dict_to_df(d, 'Logs')  # not expanding "Logs" nodes
    note for csv string: csv = df.set_index(df.columns[0]).to_csv()
    
*Output*

```
	job	name	status	Type	Logs	Task_name	path	Task_status	statuscomment	Taskid	Task_Type
0	1	jobname	jobstatus	jobtype	[{'name': 'logname', 'error': '/errorlog/file'...	Taskname	None	taskstatus		100	Tasktype
1	1	jobname	jobstatus	jobtype	[{'name': '2logname', 'error': '/errorlog/file...	Taskname1	None	taskstatus1		200	Tasktype1
```

*Run (expanding Logs nodes)*

    df = nested_dict_to_df(d)
    
 *Output*
 
 ```
 	job	name	status	Type	Task_name	path	Task_status	statuscomment	Taskid	Task_Type	error	Logs_name
0	1	jobname	jobstatus	jobtype	Taskname	None	taskstatus		100	Tasktype	/errorlog/file	logname
1	1	jobname	jobstatus	jobtype	Taskname	None	taskstatus		100	Tasktype	/errorlog/file1	logname1
2	1	jobname	jobstatus	jobtype	Taskname	None	taskstatus		100	Tasktype	/errorlog/file2	logname2
3	1	jobname	jobstatus	jobtype	Taskname	None	taskstatus		100	Tasktype	/errorlog/file	2logname
4	1	jobname	jobstatus	jobtype	Taskname	None	taskstatus		100	Tasktype	/errorlog/file1	2logname1
5	1	jobname	jobstatus	jobtype	Taskname	None	taskstatus		100	Tasktype	/errorlog/file2	2logname2
6	1	jobname	jobstatus	jobtype	Taskname1	None	taskstatus1		200	Tasktype1	/errorlog/file	logname
7	1	jobname	jobstatus	jobtype	Taskname1	None	taskstatus1		200	Tasktype1	/errorlog/file1	logname1
8	1	jobname	jobstatus	jobtype	Taskname1	None	taskstatus1		200	Tasktype1	/errorlog/file2	logname2
9	1	jobname	jobstatus	jobtype	Taskname1	None	taskstatus1		200	Tasktype1	/errorlog/file	2logname
10	1	jobname	jobstatus	jobtype	Taskname1	None	taskstatus1		200	Tasktype1	/errorlog/file1	2logname1
11	1	jobname	jobstatus	jobtype	Taskname1	None	taskstatus1		200	Tasktype1	/errorlog/file2	2logname2
```
