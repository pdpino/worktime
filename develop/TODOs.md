# TODOs and Wishlist

## TODOs
### Version 2.1
* Json files
  + ordenar keys en json, para que sea mas human-readable y para que archivos solo cambien cuando el contenido de vdd cambie
  + delete (don't save) attributes unused in json, for instance in closed entries

### Main layer
* Catch ctrl-c (ver `SignalCatcher` en muse project)
* Pasar options (start, stop, etc) a callbacks (en vez de ifs)

### Application layer
* use enum for entry life status (non created, created, finished) instead of bools `_is_created` and `is_finished`
* use enum for entry status (running, stopped, paused) instead of bools. Merge with the 'life status'?

### Folder structure
* change worktime.py name by main.py (update links)
* dejar carpeta bin en worktime, agregar eso a PATH o usar link (se puede dejar un script que lo haga por uno, "work-init"). Considerar work-git y worktime

### Other
* None



## Wishlist

### New options
* Archive jobs
* Import jobs
* opcion para que te avise dps de cierto rato
  + ejemplo: quiero trabajar 1 hora, termina en 1 hora
  + no hay alarma en pc (en terminal), como hacerlo?


### General
* usar un archivo config, poder configurar carpeta donde se guardan jobs
* agregar aliases de bash (al hacer work start) "start", "stop", etc; llamada por consola es mas rapida
  + usar archivo bash_work aparte, agregar linea de "$ source .bash_work" en bash_aliases
  + usar archivo json para guardar aliases, reescribir bash_work cada vez
* connect readline to console, to use tab-completion
* add taskbar icon

### csv
* Opcion para exportar a csv # para hacer analisis # QUESTION: nuevo proyecto work-analyzer?
* Opcion para ingresar jobs con un csv
  + ademas, mantener los jobs en un csv, y asi poder editar su info basica de manera facil
  + ej: edito en csv, luego work actualize, listo


### Improve current tools
#### show
* busqueda avanzada

#### start
* agregar opcion wait-for-me en start (con ingresar pause o stop). ademas de un no-wait

#### stop
* agregar cuando hice stop tarde, opcion para poner hora de vdd en que pare

#### create
* agregar opcion interactiva para create
* agregar timestamp de creacion a jobs?

#### delete
* Opcion 'delete' en tags, delete specific tags
* Opcion para eliminar entries. de manera interactiva es mas facil? se puede usar input_option()
