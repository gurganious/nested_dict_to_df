# nested_dict_to_df
Converts nested dictionary to pandas dataframe

CSV is easily obtained by converting the dataframe to CSV using Dataframe to_csv(...) function

**Usage**

    # Output Dataframe from dictionary d
    # max_depth max depth to recursive (option - -1 which is unlimited)
    df = nested_dict_to_df(d, max_depth)

    max_depth to expand in recursion in determining the leaf nodes
    
    # Output CSV string:
    s = df.set_index(df.columns[0]).to_csv()

**Simple Example**

 ```d = { "a": [1, 2], "b": [3, 4], "c": [5, 6]}```

*Run*

     df = nested_dictionary_to_df(d)
     
*Output*

```
	a	b	c
0	1	3	5
1	2	4	6
```

**Example**

```
# JSON String
s = {
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

    # Convert json string to dictionary
    d = json.loads(s)
    
    # Generate DataFrame
    df = nested_dict_to_df(d, 1)  # only expand to depth 1
    note for csv string: csv = df.set_index(df.columns[0]).to_csv()
    
*Output*

```
	job	name	status	Type	Logs	Task.name	path	Task.status	statuscomment	Taskid	Task.Type
0	1	jobname	jobstatus	jobtype	[{'name': 'logname', 'error': '/errorlog/file'...	Taskname	None	taskstatus		100	Tasktype
1	1	jobname	jobstatus	jobtype	[{'name': '2logname', 'error': '/errorlog/file...	Taskname1	None	taskstatus1		200	Tasktype1
```

*Run (expand unlimited depth)*

    df = nested_dict_to_df(d)
    
 *Output*
 
 ```
	job	name	status	Type	Task.name	path	Task.status	statuscomment	Taskid	Task.Type	error	Logs.name
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
