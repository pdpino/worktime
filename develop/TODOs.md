# TODOs and Wishlist

## TODOs

### URGENT: Full redesign
* Design concerns
  - model handles work-actions. Start by creating model that handles basic CRUD and session actions
  - controller handles calls from console, calls model and show results to view
  - include indicator and notifications
  - include OSEvents

* ORM to handle database. sqlite? psql?
* somewhat MVC pattern
* Command pattern for actions!!
  - export option (for later!)

### install script (pending!) (use setuptools!!)
  - set alias, add folder to `PATH` or create symlink
  - add alias or symlink to `work-indicator`
  - run `work-indicator` on boot
  - create `$HOME/.worktime` location (or other suitable one)
  - configure keyboard shortcuts (https://askubuntu.com/questions/597395/how-to-set-custom-keyboard-shortcuts-from-terminal). See `display_help()` for detail on the added shortcuts.

### Jobs module: re-design is needed
* use enum for entry life status (non created, created, finished) instead of bools `_is_created` and `is_finished`
* use enum for entry status (running, stopped, paused) instead of bools. Merge with the 'life status'?
* reverse order in entries, so newer entries are first and older ones are bottom. (when adding them use append_left)

* More ideas:
  - configurable stuff:
    + when using `start` and `stop` also do `select` and `unselect`
    + directory to save stuff
    + `work-indicator` is run at boot

### Refactor
* Use `logging` module or `raise`, delete `basic.perror`

### Other
* Make a fix when time changes from summer to winter

## Wishlist

### New options
* Backup jobs (save them somewhere safe!)
* Export actions (or jobs?) to send/sync to other devices
  - sync to google drive?, syncthing?, optional!
* Export jobs to other formats (csv, excel, json, etc)
* Import jobs (specially from old versions)
* Notify after certain amount of time

### General
* Separate pauses in short, medium, long.
* connect readline to console, to use tab-completion

### Work-analyzer
* Ideas: Option to show
  + amount of work in a day
  + in a week
  + filtering by job
  + base function that receives start and end date.

### Improve current tools
* advanced search for `show`
* discard entry option in `pause`
