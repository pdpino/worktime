"""Module that provides a class to handle the application from the console."""
from backend import results as rs
from .application import Application
import basic
import os
import threading
import time

PIPE_PATH = "/tmp/worktime" # HACK: copied from work-indicator.py
DATE_FORMAT = "%Y/%m/%d"

def send_indicator_message_thread(message):
    if not os.path.exists(PIPE_PATH):
        # indicator not up
        return

    pipe_fd = os.open(PIPE_PATH, os.O_WRONLY)

    with os.fdopen(pipe_fd, "w") as pipe:
        pipe.write(message)


def send_indicator_message(message):
    # Send it in a thread so it doesn't hang if work-indicator is not up
    t = threading.Thread(target=send_indicator_message_thread, args=(message,))
    t.start()


def start_indicator():
    send_indicator_message("start")

def stop_indicator():
    send_indicator_message("stop")

def pause_indicator():
    send_indicator_message("pause")

def validate_date_format(date, date_format):
    if date is None:
        return None
    try:
        time.strptime(date, date_format)
        return date
    except:
        print("The date '{}' should be in format year/month/day".format(date))
        return None

class ConsoleApplication(Application):
    """Handle the application from the console."""

    def _print_action(self, name, action, more_title=None):
        """Print an action made."""
        print("'{}' {}".format(name, action))
        self._notify_action(name, action, more_title=more_title)

    def _print_error(self, name, status):
        """Print an error to stdout."""
        # REFACTOR: create ResultHandler with a dict, so this is not needed
        if status == rs.ResultType.Cancelled:
            self._print_action(name, "cancelled") # REFACTOR: add action to parameters, so 'action cancelled' can be printed
        elif status == rs.ResultType.NoneNotAccepted:
            message = "A name is needed"
            print(message)
            self._notify_action(action=message) # TASK: better message
        elif status == rs.ResultType.AlreadyRunning:
            self._print_action(name, "is already running")
        elif status == rs.ResultType.NotRunning:
            self._print_action(name, "is not running")
        elif status == rs.ResultType.AlreadyExist:
            self._print_action(name, "already exist")
        elif status == rs.ResultType.NotExist:
            self._print_action(name, "doesn't exist")
        elif status == rs.ResultType.NotSelected:
            msg = "No job selected"
            print(msg)
            self._notify_action(action=msg)
        else:
            self._print_action(name, status)

    def _print_job(self, sjob, show_info=False, show_entries=False, show_time=False, from_date=None, until_date=None):
        """Pretty print for a job (ShowJob)."""

        if from_date is not None:
            from_date = time.strptime(from_date, DATE_FORMAT)
            filter_from_date = lambda date: from_date <= time.strptime(date, DATE_FORMAT)
        else:
            filter_from_date = lambda date: True

        if until_date is not None:
            until_date = time.strptime(until_date, DATE_FORMAT)
            filter_until_date = lambda date: until_date >= time.strptime(date, DATE_FORMAT)
        else:
            filter_until_date = lambda date: True

        different_days = dict()

        def get_entry_detail(sentry):
            """Pretty string and effective time for a ShowEntry"""
            if sentry.obs != "":
                obs = "\n\t\t{}".format(sentry.obs)
            else:
                obs = sentry.obs

            ttime = basic.sec2hr(sentry.total_time)
            etime = basic.sec2hr(sentry.effective_time)
            ptime = basic.sec2hr(sentry.pause_time)

            if filter_from_date(sentry.date) and filter_until_date(sentry.date):
                # Mark a different day
                different_days[sentry.date] = True
                details = "{} -- {} to {} -- total: {} -- effective: {} -- pause: {} {}".format(sentry.date,
                        sentry.hour_init, sentry.hour_end,
                        ttime, etime, ptime,
                        obs)
                effective_time = float(sentry.effective_time)
                total_time = float(sentry.total_time)
            else:
                details = ""
                effective_time = 0
                total_time = 0

            return details, total_time, effective_time

        # Get status string
        status = sjob.status
        if sjob.status == "paused": # HACK: "paused" and "running" hardcoded, use enum
            status = "paused ({} in pause)".format(sjob.pause_time)
        elif sjob.status == "running":
            status = "running (total: {}, effective: {})".format(sjob.total_time, sjob.effective_time)

        # To add times from entries
        total_eff_time = 0
        total_time = 0

        # String to print
        full_string = "{} -- {}".format(sjob.name, status)

        if show_info:
            full_string += """
            long name:  {}
            info:       {}
            tags:       {}
            total runs: {}""".format(sjob.longname, sjob.info, sjob.tags, sjob.total_runs)

        # Filter entries
        entries_string = "\n"
        n_entries = 0
        for entry in sjob.entries:
            detail, all_time, eff_time = get_entry_detail(entry)
            if detail != "":
                entries_string += "\t    {}\n".format(detail)
                n_entries += 1
            total_eff_time += eff_time
            total_time += all_time

        # Calculate statistics
        n_days = len(different_days)
        effectiveness = total_eff_time*100/total_time if total_time > 0 else 0
        time_avg = total_eff_time / n_days if n_days > 0 else 0
        entries_avg = n_entries / n_days if n_days > 0 else 0

        # No entries were found
        if total_time == 0:
            entries_string += "\t    None\n"

        # Add separator
        entries_string += "\t----------------------\n"

        # Show statistics of entries
        entries_string += "\t{} days, {} entries (average {:.1f} entries by day)\n".format(n_days, n_entries, entries_avg)

        # Show time statistics
        if show_time:
            entries_string += "\tTime:\n"
            entries_string += "\t    daily average:\t{}\n".format(basic.sec2hr(time_avg, use_days=False))
            entries_string += "\t    effective:\t\t{} ({:.1f}%)\n".format(basic.sec2hr(total_eff_time, use_days=False), effectiveness)
            entries_string += "\t    total:\t\t{}".format(basic.sec2hr(total_time, use_days=False))

        if show_entries:
            full_string += "\n\tEntries: "
            full_string += entries_string

        # print(full_string)
        return full_string, total_eff_time

    def close(self):
        """Close the application."""
        super().close()

    def start_job(self, name, info):
        """Option to start a job."""

        result = super().start_job(name, info)
        if result.is_ok():
            self._print_action(result.jobname, "started", more_title="start")
            start_indicator()
        else:
            self._print_error(result.jobname, result.status)

    def stop_job(self, name, info=None, discard=False, quiet=True, force_seconds=None):
        """Option to stop a job."""

        # Confirmation for discarding
        confirm = lambda: basic.input_y_n(question="Are you sure you want to discard an entry for '{}'".format(name))

        result = super().stop_job(name, confirm, info=info, discard=discard, force_seconds=force_seconds)
        if result.is_ok():
            action = "stopped"
            if result.was_discard:
                action += ", entry discarded"

            # Print times
            if not quiet:
                action += "\n\t Runtime: total: {}, effective: {}, pause: {}".format(
                            basic.sec2hr(result.total_time),
                            basic.sec2hr(result.effective_time),
                            basic.sec2hr(result.pause_time))


            self._print_action(result.jobname, action, more_title="stop")
            stop_indicator()
        else:
            self._print_error(result.jobname, result.status)

    def pause_job(self, name, wait=False):
        """Option to pause a job.

        wait -- if true, the console wait for an input and the toggles pause again"""

        def _pause_job():
            """Call the super to actually pause the job. Return a boolean indicating if is OK"""
            result = super(ConsoleApplication, self).pause_job(name)
            if result.is_ok():
                if result.was_paused:
                    self._print_action(result.jobname, "paused", more_title="pause")
                    pause_indicator()
                else:
                    self._print_action(result.jobname,
                                    "unpaused -- paused time: {}".format(basic.sec2hr(result.pause_time)),
                                    more_title="pause")
                    start_indicator()
            else:
                self._print_error(result.jobname, result.status)
                return False

            return True

        if _pause_job() and wait:
            input("Press enter to unpause the job ")
            self._mark_time()
            _pause_job()

    def create_job(self, name, lname, info, tags):
        """Option to create a job."""

        confirm_question = "A previous work called '{}' exists. Do you want to override it"
        confirmation = lambda: basic.input_y_n(question=confirm_question.format(name))

        result = super().create_job(name, confirmation, lname, info, tags)

        if result.is_ok():
            self._print_action(name, "created", more_title="create")
        else:
            self._print_error(name, result.status)

    def edit_job(self, name, new_name=None, new_lname=None, new_info=None, info_mode=None, new_tags=None, tags_mode=None):
        """Option to edit a job."""

        super().edit_job(name, new_name, new_lname, new_info, info_mode, new_tags, tags_mode)

    def delete_job(self, name, force=False):
        """Option to delete a job."""

        confirm = lambda: basic.input_y_n(question="Are you sure you want to drop '{}'".format(name), default="n")

        result = super().delete_job(name, confirm, force)

        if result.is_ok():
            if result.was_deleted:
                self._print_action(name, "deleted")
            else:
                self._print_action(name, "not deleted")
        else:
            self._print_error(name, result.status)

    def select_job(self, name, interactive=False):
        """Select a job to use later without calling the name."""
        if interactive:
            name = self._select_job_GUI()

        result = super().select_job(name)
        if result.is_ok():
            self._print_action(name, "selected", more_title="select")
        else:
            self._print_error(name, result.status)

    def unselect_job(self):
        """Unselect the currently selected job."""
        result = super().unselect_job()
        if result.is_ok():
            self._print_action(result.jobname, "unselected", more_title="unselect")
        else:
            self._print_error(result.jobname, result.status)

    def show_selected_job(self):
        """Show the selected job."""
        # HACK: this method doesn't pass throw the application
        jobname = self.admin_data.get_selected_job()
        if not jobname is None:
            # HACK: use self._print_action()
            message = "Selected job: '{}'".format(jobname)
            print(message)
            self._notify_action(None, message, more_title='show selected')
        else:
            self._print_error(None, rs.ResultType.NotSelected) # HACK

    def show_jobs(self, name, run_only=False, show_info=False, show_entries=False, show_time=False, from_date=None, until_date=None):
        """Option to show jobs."""

        is_filtering_by_date = from_date is not None or until_date is not None

        results = super().show_jobs(name, run_only)

        if results.no_jobs():
            message = "No jobs to show"
        else:
            from_date = validate_date_format(from_date, DATE_FORMAT)
            until_date = validate_date_format(until_date, DATE_FORMAT)

            message = ""
            total_time = 0
            for r in results:
                job_message, job_time = self._print_job(r, show_info=show_info, show_entries=show_entries, show_time=show_time, from_date=from_date, until_date=until_date)

                if is_filtering_by_date and name is None and job_time == 0:
                    # Is filtering by date, not searching by name and the job didn't have time
                    # Don't print it
                    continue

                message += job_message
                if job_message != "":
                    message += "\n"

                total_time += job_time

            if show_time: # REVIEW: Should this be checked? total_time > 0:
                message += "\nTotal effective time: {}".format(basic.sec2hr(total_time, use_days=False))

        if self.notify: # HACK!!!
            self._notify_action(action=message, more_title='show')
        else:
            print(message)
            self.show_selected_job()


    def backup_jobs(self):
        """Backup existing jobs."""
        result = super().backup_jobs()
        if result.is_ok():
            print("Jobs backed up")
        else:
            self._print_error(None, result.status)

    def archive_job(self, name, unarchive=False):
        """Backup existing jobs."""
        result = super().archive_job(name, unarchive)
        if result.is_ok():
            self._print_action(name, "archived" if not unarchive else "unarchived")
        else:
            self._print_error(name, result.status)

    def update_jobs(self):
        """Make an update to the Job objects."""
        result = super().update_jobs()
        if result.is_ok():
            print("Jobs updated")
        else:
            self._print_error(None, result.status)

    def display_help(self, shortcut=True):
        """Display a help message."""
        super().display_help(shortcut)
