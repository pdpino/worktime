#!/usr/bin/env python
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


# Next TODOs:
# FIXME: cada vez que se accede a jobs.dat se cambia el archivo, hay que volver a hacer push. Cambiar por un json?
# TODO: arreglar lo de interpreters, que funcione en todos los computadores
# TODO: pasar a callbacks (en vez de ifs)
# TODO: dejar carpeta bin en worktime, agregar eso a PATH (se puede dejar un script que lo haga por uno, "work-init")
	# y ahi dejar work git y worktime

#### Nuevas opciones:
# csv
    # TODO: Opcion para exportar a csv # IDEA: hacer analisis del trabajo
    # TODO: Opcion para ingresar jobs con un csv
        # ademas, mantener los jobs en un csv, y asi poder editar su info basica de manera facil
        # ej: edito en csv, luego work actualize, listo
# delete
    # TODO: Opcion para eliminar entradas (instancias)
        # de manera interactiva es mas facil? se puede usar input_option()
    # TODO: Opcion 'delete' en tags, delete specific tags
# show
    # TODO: agregar opcion en show, mostrar los que estan corriendo
    # TODO: en show opcion mostrar solo nombres
    # TODO: busqueda avanzada en show
# start
    # TODO: agregar opcion wait-for-me en start (con ingresar pause o stop) # con no-wait
# general
    # TODO: agregar opciones de configuracion predeterminada (archivo que guarde opciones)
# create
    # TODO: agregar opcion interactiva para create
    # TODO: agregar timestamp de creacion a jobs?

# IDEAS:
    # IDEA: opcion para hacer drop de una current run (por si se me olvido pararla)
        # IDEA: opcion de estimar cuanto trabaje en vdd, poder cambiarlo a mano
    # IDEA: opcion para que te avise dps de cierto rato
        # ejemplo: quiero trabajar 1 hora, termina en 1 hora
        # QUESTION: no hay alarma en pc (en terminal), como hacerlo?

class Entry():
    def __init__(self, t, obs=""):
        """Constructor """
        self.obs = obs

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
        """ Toggle pause/unpause the entry"""
        if self.finished:
            perror("Can't pause a finished entry")

        if self.is_paused:
            # sacar de pausa
            pf = seconds(t) # pausa final
            p_time = pf - self._pi # pause time actual
            self.pause_time += p_time # sumar pause time al total de la entry

            self.is_paused = False
        else:
            # poner en pausa
            self._pi = seconds(t) # pausa init
            self.n_pausas += 1

            self.is_paused = True

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

class Job():
    def __init__(self, name, longname, info, tags):
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

    """ Basic operations methods (start/stop/pause)"""
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
        self._entry.pause(t)
        if self.is_paused: # sacar de pausa
            self._action("unpaused")
            self.is_paused = False
        else: # poner en pausa
            self._action("paused")
            self.is_paused = True

    def stop(self, t, discard=False, print_time=True, ign_error=False):
        """ Stop a running job"""
        if not self.is_running:
            if ign_error:
                return
            else:
                perror("Work '{}' is not running".format(self.name))



        self._entry.stop(t)
        ttime = self._entry.total_time # total time
        etime = self._entry.effective_time # effective time
        ptime = self._entry.pause_time # pause time

        # Preguntar si esta seguro que quiere descartar
        if discard and etime > 30*60: # etime > 30min
            if not input_y_n(question="You've been working more than half an hour. Are you sure you want to discard it"):
                discard = False

        # Añadir entrada
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

    """ Printing methods"""
    def _print_times(self, ttime, etime, ptime):
        """Print in screen the given times"""
        print("\t Runtime: total: {}, effective: {}, pause: {}".format(
                        sec2hr(ttime),
                        sec2hr(etime),
                        sec2hr(ptime)))

    def _action(self, action):
        print("{} {}".format(self.name, action))

    def all_entries(self):
        """ Return concat string of all entries"""
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

    def pprint(self, t=None, print_entries=False):
        """ Pretty print for a job"""
        lname = self.longname or "-"
        info = self.info or "-"

        status = self.get_status(t)

        w = """{}
        long name:  {}
        info:       {}
        tags:       {}
        status:     {}
        total runs: {}""".format(self.name, lname, info, self.tags, status, len(self.entries))

        if print_entries and len(self.entries) > 0:
            w += "\n"
            w += self.all_entries()

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

root_path = sys.path[0] + "/"
files_folder = "files/"
fname_jobs_dict = "jobs.dat"
fname_jobs_dict_backup = "jobs_backup.dat"

def assert_folder():
    """ Ensures the existence of the needed folders"""
    folder = root_path + files_folder
    if not os.path.exists(folder):
        try:
            os.mkdir(folder)
        except:
            perror("Can't assert folder: {}".format(folder), exception=e)

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


    # Pause
    parser_pause = subparser.add_parser('pause',
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

    # Create
    parser_edit = subparser.add_parser('edit',
                        help="Edit an existing work")
    parser_edit.add_argument('name', default=None, type=str,
                        help="Name or alias of the work to edit")
    parser_edit.add_argument('--new-name', default=None, type=str,
                        help="New name")
    parser_edit.add_argument('-l', '--longname', default=None, type=str,
                        help="New long name")
    parser_edit.add_argument('-i', '--info', default=None, type=str,
                        help="New info about the work")
    parser_edit.add_argument('--info-mode', choices=['add', 'replace', 'drop'], default='add', type=str,
                        help="Mode to edit the info. Drop means setting info as void")
    parser_edit.add_argument('-t', '--tags', nargs='+',
                        help="New tags of the work")
    parser_edit.add_argument('--tags-mode', choices=['add', 'replace', 'drop'], default='add', type=str,
                        help="Mode to edit the tags.")


    # Delete
    parser_delete = subparser.add_parser('delete',
                        help="Delete an existing work")
    parser_delete.add_argument('name', default=None, type=str,
                        help="Name of the work to delete")
    parser_delete.add_argument('-y', action="store_true",
                        help="Skip confirmation")

    # Show
    parser_show = subparser.add_parser('show',
                        help="Show existing works")
    parser_show.add_argument('name', nargs='?', type=str,
                        help="Name to lookup")
    parser_show.add_argument('-e', '--entries', action="store_true",
                        help="Show the entries (may be a lot)")

    # Bakcup
    parser_backup = subparser.add_parser('backup',
                        help="Backup existing works")


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
    assert_folder()

    # Nombre de archivo
    fname_dict = get_fname_dict()


    # Abrir diccionario
    try:
        d = load(fname_dict)
        # print("Dict loaded") # REVIEW: use logging
    except FileNotFoundError:
        d = dict()
        # print("Dict created") # REVIEW: use logging
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
                d[k].stop(t, ign_error=True)
            # return

        else:
            # tomar key del trabajo
            key = validate_workname(args.name, d)
            try:
                d[key].stop(t, discard=args.discard, print_time=(not args.quiet))
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
            j = Job(key, args.longname, args.info, args.tags)
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
            if args.y or input_y_n(question="Are you sure you want to drop '{}'".format(key)):
                d[key].delete()
                del d[key]
        else:
            perror("The work '{}' does not exists".format(key))

    elif args.option == "show":
        if len(d) == 0:
            print("No jobs to show")
            # return

        def match_regex(k, m):
            """ Return true if k matches with m using regex"""
            if search(m, k) is None:
                return False
            else:
                return True

        def dont_match(k, m):
            """ Return true always, i.e don't match"""
            return True

        name = validate_workname(args.name)

        if not args.name is None: # Hay nombre de input
            match = match_regex
        else: # No hay nombre de input
            match = dont_match

        for k in d:
            if match(k, name):
                d[k].pprint(t, print_entries=args.entries)

        save_after = False

    elif args.option == "backup":
        # Nombre de archivo
        fname_backup = get_fname_backup()
        dump(d, fname_backup)
        save_after = False

        print("Jobs backed up")

    if save_after:
        # Guardar de vuelta diccionario
        dump(d, fname_dict)
