# TODOs and Wishlist

## TODOs

* Deprecate `work-git`, because of branches
* Finish `tests.txt` file

### Version 2.4: Application structure changes
* Create `ConsoleApplication`, which inherits from `Application`.
* Create `ResultWrapper` to wrap the behavior when using `Result`.
  + has methods `subscribe_ERROR()`, where <ERROR> is one of the possible errors. Each of these methods receives a function that is called when that error is found. In the case of the `ConsoleApplication`, the functions should be a print to stdout.
  + has a method `eval_result()`, which receives a function to call in case the result is OK, else use the functions saved previously.
  + add a `bool` `exit_after`? to exit after `eval_result`.

### Version 2.5:
* Create `filesys.AdminFileHandler` and `application.AdminData` to be able to load and save important data.


### Version 3: Status enums (not backwards compatible)
* use enum for entry life status (non created, created, finished) instead of bools `_is_created` and `is_finished`
* use enum for entry status (running, stopped, paused) instead of bools. Merge with the 'life status'?
* reverse order in entries, so newer entries are first and older ones are bottom. (when adding them use append_left)



### Script layer
* Catch ctrl-c (ver `SignalCatcher` en muse project)
* Pasar options (start, stop, etc) a callbacks (en vez de ifs)

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

### Other
* Change `basic.perror` by raise? Cases with `force_continue=True` use logging module?
* Change obs attribute in Entry: from string to list.
* Review: instead of saving the entries as json, save them as csv (the format allows it). The basic info of the job may still be json, also the current entry?


## Wishlist

### New options
* Option 'select', to mark a job as the used one and just do `work start`
* Archive jobs
* Import jobs
* opcion para que te avise dps de cierto rato
  + ejemplo: quiero trabajar 1 hora, termina en 1 hora
  + no hay alarma en pc (en terminal), como hacerlo?


### General
* Review architecture: just one job can be running at the time?
* Add subjobs, for example tts has lexicon-expander and lexicon-comparator (and more); in one course a subjob could be one particular homework; etc. Useful to timing an specific task inside a job.
* Separate pauses in short, medium, long.
* Add categories. Could separate the json files in `files/`. Categories would be exclusive (one job has only one category), while tags could be inclusive (one job may have multiple tags with no restriction).
* Opcion para sincronizar con google drive (asi despues poder usar celular)
* usar un archivo config, poder configurar carpeta donde se guardan jobs
* agregar aliases de bash (al hacer work start) "start", "stop", etc; llamada por consola es mas rapida
  + usar archivo bash_work aparte, agregar linea de "$ source .bash_work" en bash_aliases
  + usar archivo json para guardar aliases, reescribir bash_work cada vez
* connect readline to console, to use tab-completion
* add taskbar icon
* add keyboard shortcuts, to the aliases, e.g. 'ctrl+alt+1' == work pause, 'ctrl+alt+2' == work stop, etc.

### csv
* Opcion para exportar a csv (para hacer analisis).
* Opcion para ingresar jobs con un csv
  + ademas, mantener los jobs en un csv, y asi poder editar su info basica de manera facil
  + ej: edito en csv, luego work actualize, listo


### Improve current tools
#### show
* option to show only the run status and its name. Review: change argparse by exclusive options (full, status, info, etc)
* busqueda avanzada

#### pause
* discard option

#### stop
* agregar cuando hice stop tarde, opcion para poner hora de vdd en que pare

#### create
* agregar opcion interactiva para create
* agregar timestamp de creacion a jobs?

#### delete
* Opcion 'delete' en tags, delete specific tags
* Opcion para eliminar entries. de manera interactiva es mas facil? se puede usar input_option()
