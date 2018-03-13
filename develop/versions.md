# Version history of Worktime

## Version 2

### 2.9: Misc addings
Release date: X
* When showing jobs with entries the effective time gets added and displayed
* Add options to filter entries by date, and add shortcuts to show only entries from today, yesterday, or N days ago.
* Add option to archive (and unarchive) jobs, useful to hide old jobs.
* Add option to indicator to show selected job
* After starting a job, select it if it isn't selected already

### 2.8: Misc fixes
Release date: Jan 15, 2018
* Add `work-indicator`, menu with buttons in the ubuntu nav-bar; icon changes to events start, pause and stop-
* Add option to force the value worked when stopping `work stop --force <seconds>`
* Move files outside the repo `($HOME/.worktime)`

### 2.7: Interactive features
Release date: Sep 2, 2017
* Add option in `show` to show only the name and the status of the jobs. A shortcut and a notification may be used with this.
* Add `help` option to display the shortcuts.
* Add a interactive way of selecting a job

### 2.6: Notification pop-up
Release date: Sep 2, 2017
* Add an option `--notify` that makes the application let you know when did something correctly. Now you can add keyboard shortcuts (manually) to use `start`, `stop` and `pause` options and get a notification in the screen.

### 2.5: `Select` option
Release date: Sep 1, 2017
* Create submodule `application`
* Create classes `filesys.AdminFileHandler` and `application.AdminData`, that provide a way to load and save administrative and configuration data.
* Add `select` option. After selecting you can call `work start` and the selected job will start.

### 2.4: Application structure changes
Release date: Aug 13, 2017
* Deprecate `edit` option (it will return soon)
* Deprecate `--all` option in `work stop`.
* Create `Results` class, which holds the result of an action made
  + Create `StopResult`, `PauseResult`, `ShowResult`.
  + Now each action in `Job` returns a result, then the `Application` chooses what to do with it
* Create class `ConsoleApplication`, that inherits from `Application` and handles printing to stdout (`jobs` doesn't print anymore) and asking from stdin (`Application` does not use the console)

### 2.3: Backend structure changes
Release date: Aug 10, 2017
* If no option is selected (run just `work`), by default show running jobs (is like calling `work show -r`).
* Backend changes:
  + Now `FileHandler` copy the files
  + Separate `basic` in different files
  + Delete `basic.usage_error()` (it wasn't used)
  + `Application` handles saving jobs, not `Job`
  + Rename `FileHandler` to `JsonFileHandler`, and created class `JobFileHandler` who inherits from the first one.
  + `Application` delegates to `filesys.JobFileHandler` when saving jobs

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
