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
# TODO: Opcion edit, para cambiar nombres, info, o cualquier cosa de un Job
# TODO: Opcion stop all
# TODO: Opcion para exportar a csv # IDEA: hacer analisis del trabajo
# TODO: Opcion para eliminar entradas (instancias)
    # de manera interactiva es mas facil? se puede usar input_option()


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
            obs = "\n\t{}".format(self.obs)
        else:
            obs = self.obs

        if self.finished:
            horas = "{} to {} -- total: {:.1f}s -- pause: {:.1f}s -- effective: {:.1f}s".format(self.hi, self.hf, self.total_time, self.pause_time, self.effective_time)
        else:
            horas = "{}-present".format(self.hi)

        return "{}/{}/{} -- {} {}".format(self.year, self.month, self.day, horas, obs)

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

    def stop(self, t):
        if not self.is_running:
            perror("Work '{}' is not running".format(self.name))


        self._entry.stop(t)
        self.entries.append(self._entry)
        self._entry = None

        self._action("stopped")
        self.is_running = False
        self.is_paused = False

    def all_entries(self):
        """ Return concat string of all entries"""
        e = ""
        for s in self.entries:
            e += "\t" + s.pstr() + "\n"

        if not self._entry is None:
            e += "\t" + self._entry.pstr()
        return e

    def pprint(self, t=None):
        """ Pretty print for a job"""
        lname = self.longname or "-"
        info = self.info or "-"

        if self.is_running:
            status = "running"
            # calcular cuanto tiempo lleva # TODO
        else:
            status = "stopped"

        w = """{}
        long name: {}
        info: {}
        tags: {}
        status: {}""".format(self.name, lname, info, self.tags, status)

        if len(self.entries) > 0:
            w += "\n"
            w += self.all_entries()

        print(w)
        # return w

    def _action(self, action):
        print("{} {}".format(self.name, action))

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
files_dict = "jobs.dat"

def assert_folder():
    """ Ensures the existence of the needed folders"""
    folder = root_path + files_folder
    if not os.path.exists(folder):
        try:
            os.mkdir(folder)
        except:
            perror("Can't assert folder: {}".format(folder), exception=e)

def get_fname_dict():
    return root_path + files_folder + files_dict

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
    parser_show.add_argument('-n', '--name', default=None, type=str,
                        help="Name to lookup")

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


    # TODO: pasar a callbacks (en vez de ifs)

    if args.option == "start":
        # tomar key del trabajo
        key = validate_workname(args.name, d)
        d[key].start(t, args.info)

        # try:
        # except Exception as e:
        #     perror("Can't start the work '{}'".format(key), exception=e)

    elif args.option == "stop":
        # tomar key del trabajo
        key = validate_workname(args.name, d)
        try:
            d[key].stop(t)
        except Exception as e:
            perror("Can't stop the work '{}'".format(key), exception=e)

    elif args.option == "pause":
        # tomar key del trabajo
        key = validate_workname(args.name, d)

        if args.wait:
            pass
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

        # parser_edit.add_argument('name', default=None, type=str,
        #                     help="Name or alias of the work to edit")
        # parser_edit.add_argument('--new-name', default="", type=str,
        #                     help="New name")
        # parser_edit.add_argument('-l', '--longname', default="", type=str,
        #                     help="New long name")
        # parser_edit.add_argument('-i', '--info', default="", type=str,
        #                     help="New info about the work")
        # parser_edit.add_argument('--info-mode', choices=['add', 'replace', 'drop'], default='add', type=str,
        #                     help="Mode to edit the info. Drop means setting info as void")
        # parser_edit.add_argument('-t', '--tags', nargs='*',
        #                     help="New tags of the work")
        # parser_edit.add_argument('--tags-mode', choices=['add', 'replace', 'drop'], default='add', type=str,
        #                     help="Mode to edit the tags.")

        print(args)

        # if args.name



    elif args.option == "delete":
        # tomar key del trabajo
        key = validate_workname(args.name)

        if key in d:
            if args.y or input_y_n(question="Are you sure you want to drop '{}'".format(key)):
                del d[key]
        else:
            perror("The work '{}' does not exists".format(key))

    elif args.option == "show":
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
                d[k].pprint()

    # Guardar de vuelta diccionario
    dump(d, fname_dict)
