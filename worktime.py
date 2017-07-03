#!/usr/bin/env python3
""" WorkTime

Measure the time that you work on something, by calling start and stop functions
"""

import sys
import os
import argparse
from datetime import datetime
from re import search
# from timeit import default_timer as time
from basic import *
import json


##### Next TODOs:
# TODO: pasar jobs a json
# TODO: separar en capas, backend (class + basic)
# TODO: pasar a callbacks (en vez de ifs)
# TODO: dejar carpeta bin en worktime, agregar eso a PATH (se puede dejar un script que lo haga por uno, "work-init")
	# y ahi dejar work git y worktime
# TODO: agregar catch ctrl c (ver SignalCatcher, muse project)

## Formato json
    # TODO: opcion de archivar trabajos, depende de formato en json
    # TODO: opciones para importar, depende de formato en json


# IDEA: usar un archivo config, poder configurar carpeta donde se guardan jobs
# IDEA: agregar aliases de bash (al hacer work start) "start", "stop", etc; llamada por consola es mas rapida
    # usar archivo bash_work aparte, agregar linea de "$ source .bash_work" en bash_aliases
    # usar archivo json para guardar aliases, reescribir bash_work cada vez
# IDEA: conectar readline a consola, poder usar tab para completar
# IDEA: taskbar

#### Nuevas opciones:
# csv
    # IDEA: Opcion para exportar a csv # para hacer analisis # QUESTION: nuevo proyecto work-analyzer?
    # IDEA: Opcion para ingresar jobs con un csv
        # ademas, mantener los jobs en un csv, y asi poder editar su info basica de manera facil
        # ej: edito en csv, luego work actualize, listo
# delete
    # IDEA: Opcion 'delete' en tags, delete specific tags
    # IDEA: Opcion para eliminar entradas (instancias)
        # de manera interactiva es mas facil? se puede usar input_option()
# show
    # IDEA: busqueda avanzada
# stop
    # TODO: agregar cuando hice stop tarde, opcion para poner hora de vdd en que pare
# start
    # IDEA: agregar opcion wait-for-me en start (con ingresar pause o stop) # con no-wait
# general
    # IDEA: agregar opciones de configuracion predeterminada (archivo que guarde opciones)
    # IDEA: opcion para hacer drop de una current run (por si se me olvido pararla)
        # IDEA: opcion de estimar cuanto trabaje en vdd, poder cambiarlo a mano
    # IDEA: opcion para que te avise dps de cierto rato
        # ejemplo: quiero trabajar 1 hora, termina en 1 hora
        # QUESTION: no hay alarma en pc (en terminal), como hacerlo?
# create
    # IDEA: agregar opcion interactiva para create
    # IDEA: agregar timestamp de creacion a jobs?



class Entry():
    """Entry of a job, i.e. instance"""
    def __init__(self, t, obs=""):
        """Constructor """
        self.obs = ""
        self.add_obs(obs)

        # Fecha de inicio
        fecha = date(t)
        self.year = fecha[0]
        self.month = fecha[1]
        self.day = fecha[2]

        # Tiempo inicio
        self.hi = hour(t) # hora inicio: H:M
        self._ti = seconds(t) # tiempo inicio: segundos

        # Tiempo fin
        self.hf = 0
        self._tf = 0

        # Tiempo pausa
        self._pi = 0 # inicio pausa
        self.n_pausas = 0

        # Contadores
        self.total_time = 0
        self.effective_time = 0
        self.pause_time = 0

        # Booleans
        self.finished = False
        self.is_paused = False

    def stop(self, t):
        """ Stop working"""
        if self.finished:
            perror("Can't stop a finished entry")

        if self.is_paused:
            # Si es esta en pausa, unpause()
            self.pause(t)

        self.hf = hour(t) # hora termino
        self._tf = seconds(t) # segundos termino

        # calcular tiempos
        self.total_time = self._tf - self._ti
        self.effective_time = self.total_time - self.pause_time
        self.finished = True

    def pause(self, t):
        """Toggle pause/unpause the entry.

        If pausing, return number of pauses made
        else, return time paused"""
        if self.finished:
            perror("Can't pause a finished entry")

        if self.is_paused:
            # sacar de pausa
            pf = seconds(t) # pausa final
            p_time = pf - self._pi # pause time actual
            self.pause_time += p_time # sumar pause time al total de la entry

            self.is_paused = False

            return p_time
        else:
            # poner en pausa
            self._pi = seconds(t) # pausa init
            self.n_pausas += 1

            self.is_paused = True

            return self.n_pausas

    def pstr(self):
        """Pretty string"""
        if self.obs != "":
            obs = "\n\t\t{}".format(self.obs)
        else:
            obs = self.obs

        if self.finished:
            horas = "{} to {} -- total: {} -- pause: {} -- effective: {}".format(self.hi, self.hf, sec2hr(self.total_time), sec2hr(self.pause_time), sec2hr(self.effective_time))
        else:
            horas = "{}-present".format(self.hi)

        return "{}/{}/{} -- {} {}".format(self.year, self.month, self.day, horas, obs)

    def ctime_running(self, t):
        """ Current time running
        Get the total time for a running entry"""
        if t is None:
            return "unknown"
        return sec2hr(seconds(t)-self._ti)

    def ctime_effective(self, t):
        """ Current time effective.
        Get the effective time for a running entry"""
        if t is None:
            return "unknown"
        return sec2hr(seconds(t)-self._ti-self.pause_time)

    def ctime_paused(self, t):
        """ Current time paused
        Get the pause time for a running entry"""
        if t is None:
            return "unknown"
        return sec2hr(seconds(t)-self._pi)

    def add_obs(self, obs):
        """ Add observation for an entry"""
        if not obs is None:
            if len(self.obs) > 0:
                self.obs += ". "
            self.obs += str(obs)

class Job():
    """Job"""

    def __init__(self):
        self._is_created = False


    def create(self, name, longname, info, tags):
        self.name = name
        self.longname = longname
        self.info = info

        if tags is None:
            self.tags = list()
        else:
            self.tags = list(tags)

        self.entries = []

        self._entry = None # current entry
        self.is_running = False
        self.is_paused = False # solo valido si is_running=True, indica si esta en pause


        self._is_created = True

    """Basic operations methods (start/stop/pause)"""
    def start(self, t, obs=""):
        if self.is_running:
            perror("Work '{}' is already running".format(self.name))

        # Crear entrada de lista
        self._entry = Entry(t, obs)

        self._action("started")
        self.is_running = True
        self.is_paused = False

    def pause(self, t):
        if not self.is_running:
            perror("Work '{}' is not running".format(self.name))

        # Toggle pause
        r = self._entry.pause(t)
        if self.is_paused: # sacar de pausa
            self._action("unpaused", additional="Paused time: {}".format(sec2hr(r)))
            self.is_paused = False
        else: # poner en pausa
            self._action("paused")
            self.is_paused = True

    def stop(self, t, discard=False, print_time=True, ign_error=False, obs=None):
        """ Stop a running job"""
        if not self.is_running:
            if ign_error:
                return
            else:
                perror("Work '{}' is not running".format(self.name))


        self._entry.add_obs(obs)
        self._entry.stop(t)
        ttime = self._entry.total_time # total time
        etime = self._entry.effective_time # effective time
        ptime = self._entry.pause_time # pause time

        # Preguntar si esta seguro que quiere descartar
        if discard and etime > 30*60: # etime > 30min
            if not input_y_n(question="You've been working more than half an hour. Are you sure you want to discard it"):
                discard = False

        # Anadir entrada
        if not discard:
            self.entries.append(self._entry)
        self._entry = None # REVIEW: free()

        # Reportar accion al user
        action = "stopped"
        if discard:
            action += ", entry discarded"
        self._action(action)

        # Change
        self.is_running = False
        self.is_paused = False

        if print_time and not discard:
            self._print_times(ttime, etime, ptime)

    def delete(self):
        self._action("deleted")

    """Printing methods"""
    def _print_times(self, ttime, etime, ptime):
        """Print in screen the given times"""
        print("\t Runtime: total: {}, effective: {}, pause: {}".format(
                        sec2hr(ttime),
                        sec2hr(etime),
                        sec2hr(ptime)))

    def _action(self, action, additional=None):
        """Print to stdout an action."""
        w = "{} {}".format(self.name, action)
        if not additional is None:
            w += " -- {}".format(additional)
        print(w)

    def all_entries(self):
        """Concatenated string of all entries."""
        e = ""
        for s in self.entries:
            e += "\t" + s.pstr() + "\n"

        if not self._entry is None:
            e += "\t" + self._entry.pstr()
        return e

    def get_status(self, t):
        if self.is_running:
            if self.is_paused:
                status = "paused ({} in pause)".format(self._entry.ctime_paused(t))
            else:
                status = "running (total: {}, effective: {})".format(
                            self._entry.ctime_running(t),
                            self._entry.ctime_effective(t))
        else:
            status = "stopped"

        return status

    def pprint(self, t=None, name_only=False, show_entries=False):
        """Pretty print for a job."""
        # REVIEW: para que el parametro 't'?


        # Fix Nones
        lname = self.longname or "-"
        info = self.info or "-"

        # Status string
        status = self.get_status(t)

        # String to print
        if name_only:
            w = "{}".format(self.name)
        else:
            w = """{}
            long name:  {}
            info:       {}
            tags:       {}
            status:     {}
            total runs: {}""".format(self.name, lname, info, self.tags, status, len(self.entries))

        if show_entries:
            w += "\n\tEntries: "
            if len(self.entries) > 0:
                w += "\n"
                w += self.all_entries()
            else:
                w += "None\n"

        print(w)


    """Edit methods"""
    def add_tags(self, t):
        self.tags += t

    def replace_tags(self, t):
        self.tags = t # REVIEW: free las otras? se puede?

    def drop_tags(self):
        self.tags = list()
        self._action("dropped tags")

    def add_info(self, i):
        self.info += ". " + i

    def replace_info(self, i):
        self.info = i # REVIEW: free()

    def drop_info(self):
        self.info = ""
        self._action("dropped info")

    def change_longname(self, n):
        self.longname = n

    def change_name(self, n):
        self.name = n



    """JSON"""
    def toJSON(self):
        fname = "prueba.json"
        f = open(fname, "w")
        json.dump(self, f, default=lambda o: o.__dict__, sort_keys=True, indent=4)
        f.close()

def from_json():
    fname = "prueba.json"
    f = open(fname, "r")
    a = json.load(f)
    f.close()

    return a

root_path = sys.path[0] + "/"
files_folder = "files/"
fname_jobs_dict = "jobs.dat"
fname_jobs_dict_backup = "jobs_backup.dat"

def assure_folder():
    """Assure the existence of the needed folders."""
    folder = root_path + files_folder
    if not os.path.exists(folder):
        try:
            os.mkdir(folder)
        except:
            perror("Can't assure folder: {}".format(folder), exception=e)

def get_fname_dict():
    return root_path + files_folder + fname_jobs_dict

def get_fname_backup():
    return root_path + files_folder + fname_jobs_dict_backup

def create_parser():
    parser = argparse.ArgumentParser(description='Worktime', usage='%(prog)s [options]')

    # Subparsers
    subparser = parser.add_subparsers(dest='option')

    # Start
    parser_start = subparser.add_parser('start',
                        help="Start to work on something")
    parser_start.add_argument('name', default=None, type=str,
                        help="Name of the work to start")
    parser_start.add_argument('-i', '--info', default="", type=str,
                        help="Optional observations")

    # Stop
    parser_stop = subparser.add_parser('stop',
                        help="Stop a currently running work")
    parser_stop.add_argument('name', default=None, type=str,
                        help="Name of the work to stop")
    parser_stop.add_argument('-d', '--discard', action="store_true",
                        help="Discard this run")
    parser_stop.add_argument('-q', '--quiet', action="store_true",
                        help="Don't print the time when stopped")
    parser_stop.add_argument('-i', '--info', default=None, type=str,
                        help="Info about this run of the job")

    # Pause
    parser_pause = subparser.add_parser('pause', aliases=['unpause'],
                        help="Pause or unpause a running work. Useful when stopping for a short time")
    parser_pause.add_argument('name', default=None, type=str,
                        help="Name of the work to pause/unpause")
    parser_pause.add_argument('-w', '--wait', action="store_true",
                        help="Wait for me. Put the job in pause until you press enter")

    # Create
    parser_create = subparser.add_parser('create',
                        help="Create a new work")
    parser_create.add_argument('name', default=None, type=str,
                        help="Name or alias of the work to create. \
                        One word is recommended, don't use spaces for multiple words")
    parser_create.add_argument('-l', '--longname', default="", type=str,
                        help="Long name of the work to create")
    parser_create.add_argument('-i', '--info', default="", type=str,
                        help="Info about the work")
    parser_create.add_argument('-t', '--tags', nargs='+',
                        help="List of tags of the work")

    # edit
    parser_edit = subparser.add_parser('edit', help="Edit an existing work")
    parser_edit.add_argument('name', default=None, type=str,
                        help="Name or alias of the work to edit")
    parser_edit.add_argument('--new-name', default=None, type=str, help="New name")
    parser_edit.add_argument('-l', '--longname', default=None, type=str, help="New long name")
    parser_edit.add_argument('-i', '--info', default=None, type=str,
                        help="New info about the work")
    parser_edit.add_argument('--info-mode', choices=['add', 'replace', 'drop'], default='add', type=str,
                        help="Mode to edit the info. Drop means setting info as void")
    parser_edit.add_argument('-t', '--tags', nargs='+',help="New tags of the work")
    parser_edit.add_argument('--tags-mode', choices=['add', 'replace', 'drop'], default='add', type=str,
                        help="Mode to edit the tags.")


    # Delete
    parser_delete = subparser.add_parser('delete', help="Delete an existing work")
    parser_delete.add_argument('name', default=None, type=str, help="Name of the work to delete")
    parser_delete.add_argument('-y', action="store_true", help="Skip confirmation")

    # Show
    parser_show = subparser.add_parser('show', help="Show existing works")
    parser_show_filter = parser_show.add_argument_group(title="Filter options", description=None)
    parser_show_filter.add_argument('name', nargs='?', type=str, help="Name to lookup")
    parser_show_filter.add_argument('-r', '--running', action="store_true", help="Show only the running jobs")

    parser_show_opts = parser_show.add_argument_group(title="Show options", description=None)
    parser_show_opts.add_argument('-n', '--names', action="store_true", help="Show only the names of the jobs")
    parser_show_opts.add_argument('-e', '--entries', action="store_true", help="Show the entries (may be a lot)")

    ## FUTURE: use as callback
    # def foo():
    #     print("args function")
    # parser_show.set_defaults(func=foo)
    # args.func() # calling the callback, func must be defined in each subparser


    # Backup
    parser_backup = subparser.add_parser('backup', help="Backup existing works")


    return parser

def validate_workname(k, d=None):
    """Validates the name of the work

    If d is provided, assert that exists in the dict d. If isn't present in the dict exits.
    If d isn't provided, just normalize the name

    If exists return k, else exit.
    """

    # validar input
    if k is None:
        return None

    # Normalize key
    k = k.lower()

    if not d is None:
        if not k in d:
            perror("Can't find the work '{}', maybe you haven't created?".format(k))
    return k

if __name__ == "__main__":
    # Tomar tiempo
    t = datetime.now()

    # Parsear argumentos
    parser = create_parser()
    args = parser.parse_args()

    if(args.option == None):
        # REVIEW: parser no puede hacer esto automaticamente? (required=True, o algo asi)
        usage_error("No option selected. See --help")

    # Asegurarse de que existan carpetas
    assure_folder()

    # Nombre de archivo
    fname_dict = get_fname_dict()


    # Abrir diccionario
    try:
        d = load(fname_dict)
    except FileNotFoundError:
        d = dict()
    except Exception as e:
        perror("Can't load dict", exception=e)

    save_after = True

    if args.option == "start":
        # tomar key del trabajo
        key = validate_workname(args.name, d)
        d[key].start(t, args.info)

        # try:
        # except Exception as e:
        #     perror("Can't start the work '{}'".format(key), exception=e)

    elif args.option == "stop":

        # HACK
        if args.name == "all":
            for k in d:
                d[k].stop(t, ign_error=True, obs=args.info)
            # return

        else:
            # tomar key del trabajo
            key = validate_workname(args.name, d)
            try:
                d[key].stop(t, discard=args.discard, print_time=(not args.quiet), obs=args.info)
            except Exception as e:
                perror("Can't stop the work '{}'".format(key), exception=e)

    elif args.option == "pause":
        # tomar key del trabajo
        key = validate_workname(args.name, d)

        if args.wait:
            d[key].pause(t)
            input("Press enter to unpause the job ")
            d[key].pause(datetime.now())
        else:
            d[key].pause(t)

    elif args.option == "create":
        # tomar key del trabajo
        key = validate_workname(args.name)

        do_create = True # bool si crearlo o no
        if key in d:
            # Si es que ya existe work, preguntar al user
            if input_y_n(question="A previous work called '{}' exists. Do you want to override it".format(key)):
                del d[key]
            else:
                do_create = False

        # Crearlo
        if do_create:
            j = Job()
            j.create(key, args.longname, args.info, args.tags)
            d[key] = j

    elif args.option == "edit":
        # tomar key del trabajo
        key = validate_workname(args.name, d)

        job = d[key]

        # Cambiar nombre
        if not args.new_name is None:
            # cambiar key:
            d[args.new_name] = d.pop(key)
            job = d[args.new_name]

            # cambiar nombre interno:
            job.change_name(args.new_name)

        # Cambiar long name
        if not args.longname is None:
            job.change_longname(args.longname)

        # Cambiar info
        if not args.info is None:
            if args.info_mode == "add":
                job.add_info(args.info)
            elif args.info_mode == "replace":
                job.replace_info(args.info)
            elif args.info_mode == "drop":
                job.drop_info()

        # Cambiar tags
        if not args.tags is None:
            if args.tags_mode == "add":
                job.add_tags(args.tags)
            elif args.tags_mode == "replace":
                job.replace_tags(args.tags)
            elif args.tags_mode == "drop":
                job.drop_tags()

    elif args.option == "delete":
        # tomar key del trabajo
        key = validate_workname(args.name)

        if key in d:
            if args.y or input_y_n(default="n", question="Are you sure you want to drop '{}'".format(key)):
                d[key].delete()
                del d[key]
        else:
            perror("The work '{}' does not exists".format(key))

    elif args.option == "show":
        if len(d) == 0:
            pass
            # return

        def match_regex(k, m):
            """Boolean matching k with m, using regex."""
            return not search(m, k) is None

        def is_running(k):
            """Boolean, job is running."""
            return d[k].is_running

        def dont_match(dummy1=None, dummy2=None):
            """Return true always, i.e don't match."""
            return True

        name = validate_workname(args.name)

        if not args.name is None: # Hay nombre de input
            match = match_regex
        else: # No hay nombre de input
            match = dont_match

        if args.running:
            filter_running = is_running
        else:
            filter_running = dont_match

        shown = 0
        for k in d:
            if match(k, name) and filter_running(k):
                d[k].pprint(t, name_only=args.names, show_entries=args.entries)
                shown += 1

        if shown == 0:
            print("No jobs to show")

        save_after = False

    elif args.option == "backup":
        # Nombre de archivo
        fname_backup = get_fname_backup()
        dump(d, fname_backup)
        save_after = False

        print("Jobs backed up")


    # Guardar de vuelta diccionario
    if save_after:
        dump(d, fname_dict)
