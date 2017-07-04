#!/usr/bin/env python3
""" WorkTime

Measure the time that you work on something, by calling start and stop functions
"""

import sys
import argparse
from datetime import datetime
from re import search
import basic
import application


def create_parser():
    parser = argparse.ArgumentParser(description='Worktime', usage='%(prog)s [options]')

    # Subparsers
    subparser = parser.add_subparsers(dest='option')

    # Start
    parser_start = subparser.add_parser('start', help="Start to work on something")
    parser_start.add_argument('name', default=None, type=str, help="Name of the work to start")
    parser_start.add_argument('-i', '--info', default="", type=str, help="Optional observations")

    # Stop
    parser_stop = subparser.add_parser('stop', help="Stop a currently running work")
    parser_stop.add_argument('name', default=None, type=str, help="Name of the work to stop")
    parser_stop.add_argument('-a', '--all', action="store_true", help="Stop all the running jobs")
    parser_stop.add_argument('-d', '--discard', action="store_true", help="Discard this run")
    parser_stop.add_argument('-q', '--quiet', action="store_true", help="Don't print the time when stopped")
    parser_stop.add_argument('-i', '--info', default=None, type=str, help="Info about this run of the job")

    # Pause
    parser_pause = subparser.add_parser('pause', aliases=['unpause'],
                        help="Pause or unpause a running work. Useful when stopping for a short time")
    parser_pause.add_argument('name', default=None, type=str, help="Name of the work to pause/unpause")
    parser_pause.add_argument('-w', '--wait', action="store_true",
                        help="Wait for me. Put the job in pause until you press enter")

    # Create
    parser_create = subparser.add_parser('create', help="Create a new work")
    parser_create.add_argument('name', default=None, type=str,
                        help="Name or alias of the work to create. \
                        One word is recommended, don't use spaces for multiple words")
    parser_create.add_argument('-l', '--longname', default="", type=str, help="Long name of the work to create")
    parser_create.add_argument('-i', '--info', default="", type=str, help="Info about the work")
    parser_create.add_argument('-t', '--tags', nargs='+', help="List of tags of the work")

    # edit
    parser_edit = subparser.add_parser('edit', help="Edit an existing work")
    parser_edit.add_argument('name', default=None, type=str, help="Name or alias of the work to edit")
    parser_edit.add_argument('--new-name', default=None, type=str, help="New name")
    parser_edit.add_argument('-l', '--longname', default=None, type=str, help="New long name")
    parser_edit.add_argument('-i', '--info', default=None, type=str, help="New info about the work")
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


    # Update # load existing version of Job objects, update to newer
    parser_update = subparser.add_parser('update', help="Update existing Job objects")

    return parser


if __name__ == "__main__":
    # Application object
    app = application.Engine(sys.path[0])

    # Tomar tiempo
    t = datetime.now()

    # Parsear argumentos
    parser = create_parser()
    args = parser.parse_args()

    if args.option == None:
        # REVIEW: parser no puede hacer esto automaticamente? (required=True, o algo asi)
        basic.usage_error("No option selected. See --help")

    if args.option == "start":
        j = app.load_job(args.name)
        j.start(t, args.info)
        app.save_job(j)

    elif args.option == "stop":
        def stop_job(name, **kwargs):
            j = app.load_job(name)
            j.stop(t, **kwargs)
            app.save_job(j)

        if args.all:
            for name in app.get_job_names():
                stop_job(name, ign_error=True)
        else:
            stop_job(args.name, discard=args.discard, print_time=(not args.quiet), obs=args.info)

    elif args.option == "pause":
        # Load job
        j = app.load_job(args.name)

        # Pause the job
        j.pause(t)

        if args.wait: # Wait for input
            input("Press enter to unpause the job ")
            j.pause(datetime.now())

        # Save to json
        app.save_job(j)

    elif args.option == "create":
        if not app.job_exists(args.name) \
                or basic.input_y_n(question="A previous work called '{}' exists. \
                                Do you want to override it".format(args.name)):
            j = application.Job()
            j.create(args.name, args.longname, args.info, args.tags)
            app.save_job(j)

    elif args.option == "edit":
        # Load job
        j = app.load_job(args.name)

        # Cambiar nombre
        if not args.new_name is None:
            basic.perror("Change name isnt implemented")

        # Cambiar long name
        if not args.longname is None:
            j.change_longname(args.longname)

        # Cambiar info # REVIEW: metodo en Job que se encargue
        if not args.info is None:
            if args.info_mode == "add":
                j.add_info(args.info)
            elif args.info_mode == "replace":
                j.replace_info(args.info)
            elif args.info_mode == "drop":
                j.drop_info()

        # Cambiar tags
        if not args.tags is None:
            if args.tags_mode == "add":
                j.add_tags(args.tags)
            elif args.tags_mode == "replace":
                j.replace_tags(args.tags)
            elif args.tags_mode == "drop":
                j.drop_tags()

        app.save_job(j)

    elif args.option == "delete":
        if app.job_exists(args.name):
            if args.y or basic.input_y_n(default="n", question="Are you sure you want to drop '{}'".format(args.name)):
                j = app.load_job(args.name)
                j.delete()
                app.delete_job(args.name)
        else:
            basic.perror("The work '{}' does not exists".format(args.name))

    elif args.option == "show":
        def match_regex(k, m):
            """Boolean matching k with m, using regex."""
            return not search(m, k) is None

        def is_running(j):
            """Boolean, job is running."""
            return j.is_running

        def dont_match(dummy1=None, dummy2=None):
            """Return true always, i.e don't match."""
            return True

        names = app.get_job_names()

        if not args.name is None: # Hay nombre de input
            match = match_regex
        else: # No hay nombre de input
            match = dont_match

        if args.running:
            filter_running = is_running
        else:
            filter_running = dont_match

        shown = 0
        for name in names:
            j = app.load_job(name)
            if match(name, args.name) and filter_running(j):
                j.pprint(t, name_only=args.names, show_entries=args.entries)
                shown += 1

        if shown == 0:
            print("No jobs to show")

    elif args.option == "backup":
        names = app.get_job_names()

        for name in names:
            j = app.load_job(name)
            app.save_job(j, backup=True)

        print("Jobs backed up")


    elif args.option == "update":
        ## Pasar de bin a json
        # try:
        #     d = basic.load_bin("files/jobs.dat")
        # except Exception as e:
        #     basic.perror("Can't load dict", exception=e)
        #
        # for k in list(d):
        #     d[k].update()
        #     d[k].to_json()

        ## Usando json
        for name in app.get_job_names():
            j = app.load_job(name)
            j.update()
