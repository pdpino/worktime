# Version history of Worktime

## Version 2
### 2.3: Backend structure changes
Release date: X, 2017
* If no option is selected (run just `work`), by default show running jobs (like `work show -r`).
* Backend changes:
  + Now `FileHandler` copy the files
  + Separate `basic` in different files
  + Delete `basic.usage_error()` (it wasn't used)
  + `Application` handles saving jobs, not `Job`

### 2.2: Minor fixes
Release date: Aug 5, 2017
* Change names:
  + module `application/` to `backend/`
  + `data.py` to `fs.py` (filesystem)
  + delete `engine.py`: `application.py` has `Engine` class; `jobs.py` has `Job` and `Entry`
  + Rename class `Engine` to `Application`
* Change `backup` option: copy files instead of load and save with json (this ensures a good backup, in case `save_job` and `load_job` have errors)

### 2.1: Order JSON
Release date: Aug 1, 2017
* Give a specific order and delete unused attributes in json files.
* Add `--version` option to `work`
* In `Entry` class, change `n_pausas` by `n_pauses`

### 2.0: JSON
Release date: July 4, 2017
* Change pickle by json when storing jobs.  
Each job has a json file stored, which holds the basic attributes of the job and its runs.
* Add `update` tool, used to update saved jobs from earlier versions.  
Developer note: edit the `udpate()` methods in `Job` and `Entry` classes to update older attributes from the objects.
* Separate the code in layers: `main` (front-end) and `application` (back-end). Also create the `basic` module.

## 1.0: Enters Worktime
Release date: May 8, 2017
* Uses a dictionary of Job objects, save it as binary file using pickle.
* Includes `start`, `stop`, `pause`, `show`, `create`, `delete`, `edit` and `backup` tools, only in command line.
