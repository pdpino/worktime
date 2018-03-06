#!/usr/bin/env python3
"""Worktime

Measure the time that you work on different subjects."""

__author__ = "pdpino"
__program__ = "Worktime"
__version__ = "2.8"

import sys
import os
import argparse
import basic
import backend
import datetime

def parse_args():
    """Create a parser, parse args, format them and return them."""
    def create_parser():
        # REFACTOR: move add_argument name to a function
        parser = argparse.ArgumentParser(prog=__program__, usage='%(prog)s [options]',
                        description="{}, author: {}, version: {}".format(__program__, __author__, __version__))

        parser.add_argument('--version', action='version', version='%(prog)s {}'.format(__version__))
        parser.add_argument('--notify', action='store_true', help="Notify the actions on the screen")

        # Subparsers
        subparser = parser.add_subparsers(dest='option')
        # subparser.required = True

        parser_start = subparser.add_parser('start', help="Start to work on something")
        parser_start.add_argument('name', nargs='?', default=None, type=str, help="Name of the work to start")
        parser_start.add_argument('-i', '--info', default="", type=str, help="Optional observations")

        parser_stop = subparser.add_parser('stop', help="Stop a currently running work")
        parser_stop.add_argument('name', nargs='?', default=None, type=str, help="Name of the work to stop")
        parser_stop.add_argument('-d', '--discard', action="store_true", help="Discard this run")
        parser_stop.add_argument('-q', '--quiet', action="store_true", help="Don't print the time when stopped")
        parser_stop.add_argument('-i', '--info', default=None, type=str, help="Info about this run of the job")
        parser_stop.add_argument('-f', '--force', default=None, type=float, help="Input an amount of seconds to force the effective and total time to that")

        parser_pause = subparser.add_parser('pause', aliases=['unpause'],
                            help="Pause or unpause a running work. Useful when stopping for a short time")
        parser_pause.add_argument('name', nargs='?', default=None, type=str, help="Name of the work to pause/unpause")
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
        parser_select.add_argument('-I', '--interactive', action="store_true", help="Select job interactively with a GUI")
        parser_select.add_argument('-s', action='store_true', help="Show selected job")
        parser_select.add_argument('-u', action='store_true', help="Unselect job")

        parser_show = subparser.add_parser('show', help="Show existing works")
        parser_show_filter = parser_show.add_argument_group(title="Filter options", description="Options to filter the results.\nThe dates must be in the format: 2017/07/18")
        parser_show_filter.add_argument('name', nargs='?', type=str, help="Name to lookup")
        parser_show_filter.add_argument('-r', '--running', action="store_true", help="Show only the running jobs")
        parser_show_filter.add_argument('--today', action="store_true", help="Consider only entries from today")
        parser_show_filter.add_argument('--yesterday', action="store_true", help="Consider only entries from yesterday")
        parser_show_filter.add_argument('--day', type=str, help="Consider only entries from a specific day")
        parser_show_filter.add_argument('--days-ago', type=int, help="Consider only entries from N days ago")
        parser_show_filter.add_argument('--from-date', type=str, help="Filter entries from date (inclusive)")
        parser_show_filter.add_argument('--until-date', type=str, help="Filter entries until date (inclusive)")

        parser_show_opts = parser_show.add_argument_group(title="Show options", description=None)
        parser_show_opts.add_argument('--info', action="store_true", help="Show the info of each job")
        parser_show_opts.add_argument('-e', '--entries', action="store_true", help="Show the entries (may be a lot)")
        parser_show_opts.add_argument('--time', action="store_true", help="Show the time added between entries")

        parser_backup = subparser.add_parser('backup', help="Backup existing works")

        parser_archive = subparser.add_parser('archive', help="Archive a job")
        parser_archive.add_argument('name', type=str, help="Name of the job to archive")
        parser_archive.add_argument('-u', '--unarchive', action="store_true", help="Unarchive the job")

        parser_update = subparser.add_parser('update', help="Update existing work objects from older versions. Use only when there is a non-backward compatible change and update() methods are ready")

        parser_help = subparser.add_parser('help', help="Display a command help message")
        parser_help.add_argument('--shortcut', action="store_true", help="Display shorcuts")

        return parser

    parser = create_parser()
    args = parser.parse_args()

    if args.option is None: # No option selected
        # DEFAULT: use 'work show -r' (show status of running jobs)
        args = parser.parse_args(['show', '-r'])

    return args

if __name__ == "__main__":
    app = backend.ConsoleApplication(os.path.join(os.environ["HOME"], ".worktime"))
    args = parse_args()
    app.notify = args.notify

    if args.option == "start":
        app.start_job(args.name, args.info)
    elif args.option == "stop":
        app.stop_job(args.name, info=args.info, discard=args.discard, quiet=args.quiet, force_seconds=args.force)
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
        if args.from_date is not None or args.until_date is not None or args.today or args.yesterday or args.day is not None or args.days_ago is not None:
            # If filtering by dates, use entries
            args.entries = True

        if args.entries: # If show entries, also show added time
            args.time = True

        # Select today or yesterday
        if args.today:
            args.day = datetime.date.today().strftime("%Y/%m/%d")
            # HACK: date format copied from consoleapp
        elif args.yesterday:
            args.days_ago = 1

        # Select days ago, only if --day is not selected
        if args.days_ago and args.day is None:
            day = datetime.date.today() - datetime.timedelta(days=args.days_ago)
            args.day = day.strftime("%Y/%m/%d")

        # Select day
        if args.day is not None:
            args.from_date = args.day
            args.until_date = args.day

        app.show_jobs(args.name,
                    run_only=args.running,
                    show_info=args.info,
                    show_entries=args.entries,
                    show_time=args.time,
                    from_date=args.from_date,
                    until_date=args.until_date)
    elif args.option == "select":
        if args.s:
            app.show_selected_job()
        elif args.u:
            app.unselect_job()
        else:
            app.select_job(args.name, args.interactive)
    elif args.option == "backup":
        print("Backup option is being fixed :grimacing:")
        # app.backup_jobs()
    elif args.option == "archive":
        app.archive_job(args.name, args.unarchive)
    elif args.option == "update":
        app.update_jobs()
    elif args.option == "help":
        app.display_help(args.shortcut)

    app.close()
