# TODOs and Wishlist

## TODOs

* Add install script:
  + set alias or add to `PATH`
  + configure keyboard shortcuts (https://askubuntu.com/questions/597395/how-to-set-custom-keyboard-shortcuts-from-terminal)
    - `work --notify start`
    - `work --notify stop`
    - `work --notify pause`
    - `work --notify show -r -s` -- show running jobs, only status
    - `work --notify select -s` -- show selected job

### Version 3: Json files to other folder
* Move json files to another location (e.g. `home/.worktime`)

### Jobs module: re-design is needed
* use enum for entry life status (non created, created, finished) instead of bools `_is_created` and `is_finished`
* use enum for entry status (running, stopped, paused) instead of bools. Merge with the 'life status'?
* reverse order in entries, so newer entries are first and older ones are bottom. (when adding them use append_left)

### Script layer
* Catch ctrl-c (ver `SignalCatcher` en muse project)
* Pasar options (start, stop, etc) a callbacks (en vez de ifs)

### ShowResults
* Review: Change `ShowJob` and `EntryJob`, options:
  + remove them, the `show()` just return a dictionary with the info
  + leave them, but move them to `jobs`. `ShowJob` has as attribute a `Job`, exposes methods to get useful things. The API specifies those methods.

### Filesys module
* move `get_dict()` to be a static method?
* move `JsonFileHandler` to basic?
* Review whole architecture of this module, is the extension hardcoded somewhere? could there be another more basic class `FileHandler`? that receives the extension (if so, a `CsvFileHandler` could be easily created, which could be useful at some point)

### Folder structure
* Move `application.py` and `jobs.py` to an `application` folder?
* change `worktime.py` name by `main.py`? (update links)
* dejar carpeta `bin/` en worktime, agregar eso a PATH o usar link (se puede dejar un script que lo haga por uno, `work-init`). Considerar `work-git` y `worktime`

### Work-analyzer
* Start designing
* Ideas: Option to show
  + amount of work in a day
  + in a week
  + filtering by job
  + base function that receives start and end date.

### Re-design
* Whole architecture
* `Results` module. Several results must be able to be returned
  + like in `show`
  + when calling `start` you want to automatically call `select`
  + when deleting a job and its selected, you want to unselect it.
* argparse
  + show options, `name_only`, `status_only` and `show_entries` are all exclusive, use `choices` argument?

### Refactor
* Fix `work-git`, because of branches
* Create `ResultHandler` to wrap the behavior when using `Result`.
  + has methods `subscribe_ERROR()`, where <ERROR> is one of the possible errors. Each of these methods receives a function that is called when that error is found. In the case of the `ConsoleApplication`, the functions should be a print to stdout.
  + has a method `eval_result()`, which receives a function to call in case the result is OK, else use the functions saved previously.
  + add a `bool` `exit_after`? to exit after `eval_result`.
* Change `basic.perror` by raise? Cases with `force_continue=True` use logging module?

### Other
* Add options saved in file:
  + when using `start` and `stop` also do `select` and `unselect`; or leave this manual
  + directory to save files, by default `$HOME/.worktime/files` (or `/jobs`) (move configuration file `config/admin.json` to that location)
  + default behavior for `work select` (may be unselect or show), and for `work` (currently is `work show -r`)
* Make a fix when time changes? like summer to winter time
* Change `obs` attribute in `Entry`: from string to list.
* Change time of the notification pop-up


## Wishlist

### New options
* Archive jobs
* Import jobs
* opcion para que te avise dps de cierto rato
  + ejemplo: quiero trabajar 1 hora, termina en 1 hora
  + no hay alarma en pc (en terminal), como hacerlo?


### General
* add taskbar icon
* Add subjobs, for example tts has lexicon-expander and lexicon-comparator (and more); in one course a subjob could be one particular homework; etc. Useful to timing an specific task inside a job. REVIEW this depending on requirements
* Separate pauses in short, medium, long.
* Add categories. Could separate the json files in `files/`. Categories would be exclusive (one job has only one category), while tags could be inclusive (one job may have multiple tags with no restriction).
* Option to sincronize (google drive? syncthing?)
* connect readline to console, to use tab-completion

### Improve current tools
#### show
* advanced search

#### pause
* discard entry option

#### stop
* add option to add real stopping time, in case I forgot to run `work stop`

#### create
* add interactive option
* add creation timestamps to `Jobs`?

#### delete
* `remove` option for tags, remove specific tags from a Job
* Option to delete `entries`. Interactively?
