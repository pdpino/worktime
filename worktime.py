#!/usr/bin/env python
""" WorkTime

Measure the time that you work on something, by calling start and stop functions
"""

import sys
import os
import argparse
# from timeit import default_timer as time
from basic import *
from datetime import datetime


# Next TODOs:
# TODO: Opcion pause
# TODO: Opcion edit, para cambiar nombres, info, o cualquier cosa de un Job
# TODO: Opcion stop all
# TODO: Opcion para exportar a csv # IDEA: hacer analisis del trabajo
# TODO: Opcion para eliminar entradas (instancias)
    # de manera interactiva es mas facil? se puede usar input_option()
# TODO: Opcion show 'work'
    # show work especifico, sino pueden ser muchos

# otros
# IDEA: añadir categorias (labels o tags) a jobs (ademas de info y nombre largo)

# Chicos
# TODO: ordenar archivos, variable con nombre de carpeta y nombre de archivo
# TODO: rellenar readme


class Entry():
    def __init__(self, t, obs=""):
        """Constructor """
        self.obs = obs

        # Fecha de inicio
        fecha = date(t)
        self.year = fecha[0]
        self.month = fecha[1]
        self.day = fecha[2]

        # Hora de inicio
        self.hi = hour(t) # hora inicio: H:M
        self._ti = seconds(t) # tiempo inicio: segundos

        self.finished = False

    def stop(self, t):
        """ Stop working"""
        self.hf = hour(t) # hora termino
        self._tf = seconds(t) # segundos termino

        # calcular tiempos
        self.total_time = self._tf - self._ti
        self.finished = True

    def __str__(self):
        """To string"""
        if self.obs != "":
            obs = "\n\t{}".format(self.obs)
        else:
            obs = self.obs

        if self.finished:
            horas = "{} to {} -- total: {:.1f} seconds".format(self.hi, self.hf, self.total_time)
        else:
            horas = "{}-present".format(self.hi)

        return "{}/{}/{} -- {} {}".format(self.year, self.month, self.day, horas, obs)

class Job():
    def __init__(self, name, longname, info):
        self.name = name
        self.longname = longname
        self.info = info

        self.entries = []

        self._entry = None # current entry
        self.is_running = False

        # TODO: implementar pausas (agregar tiempo efectivo y tiempo pausas)

    def start(self, t, obs=""):
        if self.is_running:
            perror("Work '{}' is already running".format(self.name))

        # Crear entrada de lista
        self._entry = Entry(t, obs)

        print("{} started".format(self.name))
        self.is_running = True

    def stop(self, t):
        if not self.is_running:
            perror("Work '{}' is not running".format(self.name))


        self._entry.stop(t)
        self.entries.append(self._entry)
        self._entry = None

        print("{} stopped".format(self.name))
        self.is_running = False

    def all_entries(self):
        """ Retornar string concatenado de todas las entries"""
        e = ""
        for s in self.entries:
            e += "\t" + str(s) + "\n"

        if not self._entry is None:
            e += "\t" + str(self._entry)
        return e

    def __str__(self):
        lname = self.longname or "-"
        info = self.info or "-"
        status = "running" if self.is_running else "stopped"
        w = "{}\n\tlong name: {}\n\tinfo: {}\n\tstatus: {}".format(self.name, lname, info, status)

        if len(self.entries) > 0:
            w += "\n"
            w += self.all_entries()

        return w

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


    return parser

def assert_work(k, d):
    """Assert that the work d[k] exists.

    If exists return k, else exit.
    d: dict
    k: key """
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

    # Nombre de archivo
    fname_dict = this_path + "/files/diccionario.dat"

    # Asegurarse de que existan carpetas
    assert_folder()

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
        key = assert_work(args.name, d)
        d[key].start(t, args.info)

        # try:
        # except Exception as e:
        #     perror("Can't start the work '{}'".format(key), exception=e)

    elif args.option == "stop":
        # tomar key del trabajo
        key = assert_work(args.name, d)
        try:
            d[key].stop(t)
        except Exception as e:
            perror("Can't stop the work '{}'".format(key), exception=e)

    elif args.option == "create":
        # tomar key del trabajo
        key = args.name

        j = Job(key, args.longname, args.info)
        if key in d:
            # Si es que ya existe work, preguntar al user
            if input_y_n(question="A previous work called '{}' exists. Do you want to override it".format(key)):
                del d[key]
                d[key] = j
        else:
            d[key] = j

    elif args.option == "delete":
        # tomar key del trabajo
        key = args.name

        if key in d:
            if args.y or input_y_n(question="Are you sure you want to drop '{}'".format(key)):
                del d[key]
        else:
            perror("The work '{}' does not exists".format(key))

    elif args.option == "show":
        for k in d:
            print(d[k])

    # Guardar de vuelta diccionario
    dump(d, fname_dict)
