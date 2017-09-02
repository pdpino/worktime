#!/usr/bin/env python3
"""Worktime

Measure the time that you work on different subjects."""

__author__ = "pdpino"
__program__ = "Worktime"
__version__ = "2.5dev"

import sys
import argparse
import basic
import backend

def parse_args():
    """Create a parser, parse args, format them and return them."""
    def create_parser():
        # REFACTOR: move add_argument name to a function
        parser = argparse.ArgumentParser(prog=__program__, usage='%(prog)s [options]',
                        description="{}, author: {}, version: {}".format(__program__, __author__, __version__))

        parser.add_argument('--version', action='version', version='%(prog)s {}'.format(__version__))

        # Subparsers
        subparser = parser.add_subparsers(dest='option')
        # subparser.required = True

        parser_start = subparser.add_parser('start', help="Start to work on something")
        parser_start.add_argument('name', default=None, type=str, help="Name of the work to start")
        parser_start.add_argument('-i', '--info', default="", type=str, help="Optional observations")

        parser_stop = subparser.add_parser('stop', help="Stop a currently running work")
        parser_stop.add_argument('name', default=None, type=str, help="Name of the work to stop")
        parser_stop.add_argument('-d', '--discard', action="store_true", help="Discard this run")
        parser_stop.add_argument('-q', '--quiet', action="store_true", help="Don't print the time when stopped")
        parser_stop.add_argument('-i', '--info', default=None, type=str, help="Info about this run of the job")

        parser_pause = subparser.add_parser('pause', aliases=['unpause'],
                            help="Pause or unpause a running work. Useful when stopping for a short time")
        parser_pause.add_argument('name', default=None, type=str, help="Name of the work to pause/unpause")
        parser_pause.add_argument('-w', '--wait', action="store_true",
                            help="Wait for me. Put the job in pause until you press enter")

        parser_create = subparser.add_parser('create', help="Create a new work")
        parser_create.add_argument('name', default=None, type=str,
                            help="Name or alias of the work to create. \
                            One word is recommended, don't use spaces for multiple words")
        parser_create.add_argument('-l', '--longname', default="", type=str, help="Long name of the work to create")
        parser_create.add_argument('-i', '--info', default="", type=str, help="Info about the work")
        parser_create.add_argument('-t', '--tags', nargs='+', help="List of tags of the work")

        parser_edit = subparser.add_parser('edit', help="Edit an existing work")
        parser_edit.add_argument('name', default=None, type=str, help="Name or alias of the work to edit")
        parser_edit.add_argument('--new-name', default=None, type=str, help="New name")
        parser_edit.add_argument('-l', '--longname', default=None, type=str, help="New long name")
        parser_edit.add_argument('-i', '--info', default=None, type=str, help="New info about the work")
        parser_edit.add_argument('--info-mode', choices=['add', 'replace', 'drop'], default=None, type=str,
                            help="Mode to edit the info. Drop means setting info as void")
        parser_edit.add_argument('-t', '--tags', nargs='+',help="New tags of the work")
        parser_edit.add_argument('--tags-mode', choices=['add', 'replace', 'drop'], default=None, type=str,
                            help="Mode to edit the tags.")

        parser_delete = subparser.add_parser('delete', help="Delete an existing work")
        parser_delete.add_argument('name', default=None, type=str, help="Name of the work to delete")
        parser_delete.add_argument('-y', action="store_true", help="Skip confirmation")

        parser_select = subparser.add_parser('select', help="Select a work")
        parser_select.add_argument('name', nargs='?', default=None, type=str, help="Name of the work to select")
        parser_select.add_argument('-s', action='store_true', help="Show selected job")
        parser_select.add_argument('-u', action='store_true', help="Unselect job")

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


        parser_backup = subparser.add_parser('backup', help="Backup existing works")

        parser_update = subparser.add_parser('update', help="Update existing Job objects")

        return parser

    parser = create_parser()
    args = parser.parse_args()

    if args.option is None: # No option selected
        # DEFAULT: use 'work show -r' (show running jobs)
        args = parser.parse_args(['show', '-r'])

    return args

if __name__ == "__main__":
    # Create application object
    app = backend.ConsoleApplication(sys.path[0])

    # Parsear argumentos
    args = parse_args()

    if args.option == "start":
        app.start_job(args.name, args.info)
    elif args.option == "stop":
        app.stop_job(args.name, info=args.info, discard=args.discard, quiet=args.quiet)
    elif args.option == "pause":
        app.pause_job(args.name, args.wait)
    elif args.option == "create":
        app.create_job(args.name, args.longname, args.info, args.tags)
    elif args.option == "edit":
        app.edit_job(args.name,
                    new_name=args.new_name,
                    new_lname=args.longname,
                    new_info=args.info,
                    info_mode=args.info_mode,
                    new_tags=args.tags,
                    tags_mode=args.tags_mode)
    elif args.option == "delete":
        app.delete_job(args.name, args.y)
    elif args.option == "show":
        app.show_jobs(args.name, run_only=args.running, name_only=args.names, show_entries=args.entries)
    elif args.option == "select":
        if args.s:
            app.show_selected_job()
        elif args.u:
            app.unselect_job()
        else:
            app.select_job(args.name)
    elif args.option == "backup":
        app.backup_jobs()
    elif args.option == "update":
        app.update_jobs()

    app.close()
