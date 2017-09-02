"""Module that provides a class to handle the application from the console."""
from backend import results as rs
from .application import Application
import basic

class ConsoleApplication(Application):
    """Handle the application from the console."""

    def _print_action(self, name, action):
        """Print an action made."""
        print("'{}' {}".format(name, action))
        self._notify_action(name, action)

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

    def _print_job(self, sjob, name_only=False, status_only=False, show_entries=False):
        """Pretty print for a job (ShowJob)."""

        def pstr(sentry):
            """Pretty string for a show_entry"""
            if sentry.obs != "":
                obs = "\n\t\t{}".format(sentry.obs)
            else:
                obs = sentry.obs

            ttime = basic.sec2hr(sentry.total_time)
            etime = basic.sec2hr(sentry.effective_time)
            ptime = basic.sec2hr(sentry.pause_time)

            return "{} -- {} to {} -- total: {} -- effective: {} -- pause: {} {}".format(sentry.date,
                        sentry.hour_init, sentry.hour_end,
                        ttime, etime, ptime,
                        obs)

        # Get status string
        status = sjob.status
        if sjob.status == "paused": # HACK: "paused" and "running" hardcoded, use enum
            status = "paused ({} in pause)".format(sjob.pause_time)
        elif sjob.status == "running":
            status = "running (total: {}, effective: {})".format(sjob.total_time, sjob.effective_time)

        # String to print
        if name_only:
            w = "{}".format(sjob.name)
        elif status_only:
            w = "{} -- {}".format(sjob.name, status)
        else:
            w = """{}
            long name:  {}
            info:       {}
            tags:       {}
            status:     {}
            total runs: {}""".format(sjob.name, sjob.longname, sjob.info, sjob.tags, status, sjob.total_runs)

            if show_entries: # show_entries only works if not name_only and not status_only
                w += "\n\tEntries: "
                if len(sjob.entries) > 0:
                    w += "\n"
                    for s in sjob.entries:
                        w += "\t{}\n".format(pstr(s))
                else:
                    w += "None\n"

        print(w)
        return w

    def close(self):
        """Close the application."""
        super().close()

    def start_job(self, name, info):
        """Option to start a job."""

        result = super().start_job(name, info)
        if result.is_ok():
            self._print_action(result.jobname, "started")
        else:
            self._print_error(result.jobname, result.status)

    def stop_job(self, name, info=None, discard=False, quiet=True):
        """Option to stop a job."""

        # Confirmation for discarding
        confirm = lambda: basic.input_y_n(question="Are you sure you want to discard an entry for '{}'".format(name))

        result = super().stop_job(name, confirm, info=info, discard=discard)
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


            self._print_action(result.jobname, action)
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
                    self._print_action(result.jobname, "paused")
                else:
                    self._print_action(result.jobname,
                                    "unpaused -- paused time: {}".format(basic.sec2hr(result.pause_time)))
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
            self._print_action(name, "created")
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
            self._print_action(name, "selected")
        else:
            self._print_error(name, result.status)

    def unselect_job(self):
        """Unselect the currently selected job."""
        result = super().unselect_job()
        if result.is_ok():
            self._print_action(result.jobname, "unselected")
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
            self._notify_action(None, message)
        else:
            self._print_error(None, rs.ResultType.NotSelected) # HACK

    def show_jobs(self, name, run_only=False, name_only=False, status_only=False, show_entries=False):
        """Option to show jobs."""

        results = super().show_jobs(name, run_only)

        if results.no_jobs():
            message = "No jobs to show"
        else:
            message = ""
            for r in results:
                message += self._print_job(r, name_only=name_only, status_only=status_only, show_entries=show_entries)
                message += "\n"

        print(message)
        self._notify_action(action=message)

    def backup_jobs(self):
        """Backup existing jobs."""
        result = super().backup_jobs()
        if result.is_ok():
            print("Jobs backed up")
        else:
            self._print_error(None, result.status)

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
