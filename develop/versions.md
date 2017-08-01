# Version history of Worktime

## Version 1.0
* Uses a dictionary of Job objects, save it as binary file using pickle.
* Includes `start`, `stop`, `pause`, `show`, `create`, `delete`, `edit` and `backup` tools, only in command line.


## Version 2
### 2.0: JSON
* Change pickle by json when storing jobs.  
Each job has a json file stored, which holds the basic attributes of the job and its runs.
* Add `update` tool, used to update saved jobs from earlier versions.  
Developer note: edit the `udpate()` methods in `Job` and `Entry` classes to update older attributes from the objects.
* Separate the code in layers: `main` (front-end) and `application` (back-end). Also create the `basic` module.


### 2.1:
* Give a specific order and delete unused attributes in json files.

### 2.1.1: ...
