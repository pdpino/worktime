# Version history of Worktime

## Version 1.0
* Uses a dictionary of Job objects, save the dictionary using pickle
* Includes `start`, `stop`, `pause`, `show`, `create`, `delete`, `edit` and `backup` tools, only in command line.


## Version 2
### 2.0: JSON comes in
* When storing jobs change pickle by json. Each job has a json file stored. The json file holds all the attributes of the classes.
* Add `update` tool, used to update saved jobs from earlier versions.
Developer note: edit the `udpate()` methods in `Job` and `Entry` classes to update older attributes from the objects.
