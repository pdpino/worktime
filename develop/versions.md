# Version history of Worktime

## Version 2
### 2.3: Backend structures changes
* Now `FileHandler` copy the files

### 2.2: Minor fixes
* Change names:
  + module `application/` to `backend/`
  + `data.py` to `fs.py` (filesystem)
  + delete `engine.py`: `application.py` has `Engine` class; `jobs.py` has `Job` and `Entry`
  + Rename class `Engine` to `Application`
* Change `backup` option: copy files instead of load and save with json

### 2.1: Order JSON
* Give a specific order and delete unused attributes in json files.
* Add `--version` option to `work`
* In `Entry` class, change `n_pausas` by `n_pauses`

### 2.0: JSON
* Change pickle by json when storing jobs.  
Each job has a json file stored, which holds the basic attributes of the job and its runs.
* Add `update` tool, used to update saved jobs from earlier versions.  
Developer note: edit the `udpate()` methods in `Job` and `Entry` classes to update older attributes from the objects.
* Separate the code in layers: `main` (front-end) and `application` (back-end). Also create the `basic` module.

## Version 1
* Uses a dictionary of Job objects, save it as binary file using pickle.
* Includes `start`, `stop`, `pause`, `show`, `create`, `delete`, `edit` and `backup` tools, only in command line.
