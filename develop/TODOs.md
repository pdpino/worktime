# TODOs and Wishlist

## TODOs
* Further testing of json and layers implementation. Move `FileHandler` to engine module?
* Pasar options (start, stop, etc) a callbacks (en vez de ifs)
* dejar carpeta bin en worktime, agregar eso a PATH o usar link (se puede dejar un script que lo haga por uno, "work-init"). Considerar work-git y worktime
* agregar catch ctrl c (ver `SignalCatcher` en muse project)
* opcion de archivar trabajos
* opciones para importar
* set a state in an entry 'used', delete unused variables and close it (cant run the methods) # Use finished attribute

#### Json files
* ordenar keys en json, para que sea mas human-readable
* borrar attributes unused in json, for instance in closed entries


## Wishlist
* usar un archivo config, poder configurar carpeta donde se guardan jobs
* agregar aliases de bash (al hacer work start) "start", "stop", etc; llamada por consola es mas rapida
    # usar archivo bash_work aparte, agregar linea de "$ source .bash_work" en bash_aliases
    # usar archivo json para guardar aliases, reescribir bash_work cada vez
* connect readline to console, to use tab-completion
* add taskbar icon

### csv
* Opcion para exportar a csv # para hacer analisis # QUESTION: nuevo proyecto work-analyzer?
* Opcion para ingresar jobs con un csv
  + ademas, mantener los jobs en un csv, y asi poder editar su info basica de manera facil
  + ej: edito en csv, luego work actualize, listo

### delete
* Opcion 'delete' en tags, delete specific tags
* Opcion para eliminar entries. de manera interactiva es mas facil? se puede usar input_option()

### show
* busqueda avanzada

### stop
* agregar cuando hice stop tarde, opcion para poner hora de vdd en que pare

### start
* agregar opcion wait-for-me en start (con ingresar pause o stop) # con no-wait

### general
* agregar opciones de configuracion predeterminada (archivo que guarde opciones)
* opcion para hacer drop de una current run (por si se me olvido pararla)
  + opcion de estimar cuanto trabaje en vdd, poder cambiarlo a mano
* opcion para que te avise dps de cierto rato
  + ejemplo: quiero trabajar 1 hora, termina en 1 hora
  + no hay alarma en pc (en terminal), como hacerlo?

### create
* agregar opcion interactiva para create
* agregar timestamp de creacion a jobs?
