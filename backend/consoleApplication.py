"""Module that provides a class to handle the application from the console."""
from backend import application
import basic

class ConsoleApplication(application.Application):
    """Handle the application from the console."""

    def _print_action(self, name, action):
        """Print an action made."""
        print("'{}' {}".format(name, action))

    def _print_error(self, name, status):
        """Print an error to stdout."""
        if status == rs.ResultType.AlreadyRunning:
            print_action(name, "is already running")
        elif status == rs.ResultType.NotRunning:
            print_action(name, "is not running")
        elif status == rs.ResultType.AlreadyExist:
            print_action(name, "already exist")
        elif status == rs.ResultType.NotExist:
            print_action(name, "doesn't exist")
        else:
            print_action(name, status)

    def _print_job(self, sjob, name_only=False, show_entries=False):
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
        else:
            w = """{}
            long name:  {}
            info:       {}
            tags:       {}
            status:     {}
            total runs: {}""".format(sjob.name, sjob.longname, sjob.info, sjob.tags, status, sjob.total_runs)

        if show_entries:
            w += "\n\tEntries: "
            if len(sjob.entries) > 0:
                w += "\n"
                for s in sjob.entries:
                    w += "\t{}\n".format(pstr(s))
            else:
                w += "None\n"

        print(w)



    def start_job(self, name, info):
        """Option to start a job."""

        result = super().start_job(name, info)

        if result.is_ok():
            self.print_action(name, "started")
        else:
            self.print_error(name, result.status)

    def stop_job(self, name, info=None, discard=False, quiet=True):
        """Option to stop a job."""

        # Confirmation for discarding
        confirm = lambda: basic.input_y_n(question="Are you sure you want to discard an entry for '{}'".format(name))

        # Stop
        result = super().stop_job(name, confirm, info=info, discard=discard)

        if result.is_ok():
            action = "stopped"
            if result.was_discard:
                action += ", entry discarded"
            self.print_action(name, action)

            # Print times
            if not quiet:
                print("\t Runtime: total: {}, effective: {}, pause: {}".format(
                            basic.sec2hr(result.total_time),
                            basic.sec2hr(result.effective_time),
                            basic.sec2hr(result.pause_time)))
        else:
            self.print_error(name, result.status)

    def pause_job(self, name, wait=False):
        """Option to pause a job."""
        self._assert_time("pause a job")

        def _pause_job(j, t):
            result = j.pause(t)
            if result.is_ok():
                if result.was_paused:
                    print_action(name, "paused")
                else:
                    print_action(name, "unpaused -- paused time: {}".format(basic.sec2hr(result.pause_time)))
            else:
                print_error(name, result.status)

        j = self._load_job(name)
        _pause_job(j, self.t)

        if wait: # Wait for input
            input("Press enter to unpause the job ")
            self._time_mark() # Take another mark
            _pause_job(j, self.t)


        # Save to json
        self._save_job(j)

    def create_job(self, name, lname, info, tags):
        """Option to create a job."""

        confirm = lambda: basic.input_y_n(question="A previous work called '{}' exists. Do you want to override it".format(name))

        result = super().create_job(name, confirm, lname, info, tags)

        if result.is_ok():
            self.print_action(name, "created")
        else:
            self.print_error(name, result.status)


    def edit_job(self, name, new_name=None, new_lname=None, new_info=None, info_mode=None, new_tags=None, tags_mode=None):
        """Option to edit a job."""

        basic.perror("DEPRECATED: can't edit job")

        j = self._load_job(name)

        # Cambiar nombre
        if not new_name is None:
            # j.change_name(new_name)
            basic.perror("Change name isnt implemented")

        if not new_lname is None:
            j.change_longname(new_lname)

        if not new_info is None:
            j.edit_info(new_info, info_mode)

        if not new_tags is None:
            j.edit_tags(new_tags, tags_mode)

        self._save_job(j)

    def delete_job(self, name, force=False):
        """Option to delete a job."""

        if not self._job_exists(name):
            print_error(name, rs.ResultType.NotExist)
            return

        q = "Are you sure you want to drop '{}'".format(name)
        if force or basic.input_y_n(question=q, default="n"):
            j = self._load_job(name)
            self.fh.remove_job(name)

    def show_jobs(self, name, run_only=False, name_only=False, show_entries=False):
        """Option to show jobs."""

        # REVIEW: dont create functions every time
        def match_regex(k, m):
            """Boolean matching k with m, using regex."""
            return not search(m, k) is None

        def is_running(j):
            """Boolean, job is running."""
            return j.is_running

        def dont_match(dummy1=None, dummy2=None):
            """Return true always, i.e don't match."""
            return True

        names = self._get_job_names()

        if not name is None: # There is a name to filter
            match = match_regex
        else:
            match = dont_match

        if run_only: # Show only running jobs
            filter_running = is_running
        else:
            filter_running = dont_match

        results = rs.ShowResult()
        for n in names:
            j = self._load_job(n)
            if match(n, name) and filter_running(j):
                sjob = j.show(self.t)
                results.add_job(sjob)

        if results.no_jobs():
            print("No jobs to show")
        else:
            for r in results:
                print_job(r, name_only, show_entries)

    def backup_jobs(self):
        """Backup existing jobs."""
        for name in self._get_job_names():
            self.fh.backup_job(name)

        print("Jobs backed up")

    def update(self):
        """Make an update to the Job objects."""
        for name in self._get_job_names():
            j = self._load_job(name)
            j.update()
            self._save_job(j)

        print("Jobs updated")
