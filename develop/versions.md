# Version history of Worktime

## Version 1.0
* Uses a dictionary of Job objects, save it as binary file using pickle.
* Includes `start`, `stop`, `pause`, `show`, `create`, `delete`, `edit` and `backup` tools, only in command line.


## Version 2
### 2.0: JSON
* Change pickle by json when storing jobs.

Each job has a json file stored, which holds all the attributes of the object.

* Add `update` tool, used to update saved jobs from earlier versions.

Developer note: edit the `udpate()` methods in `Job` and `Entry` classes to update older attributes from the objects.