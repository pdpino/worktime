"""Module that provides classes to handle the application."""
from datetime import datetime
from re import search
from backend import jobs, results as rs, filesys as fs
import basic

def print_action(name, action):
    """Temporary function."""
    print("'{}' {}".format(name, action))

def print_error(name, status):
    """Temporary function. Should pass to ConsoleApplication"""
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

class Application():
    """Handle the application."""

    def __init__(self, root_path):
        """Constructor."""
        # File Handler
        self.fh = fs.JobFileHandler(root_path, "files") # HACK: "files" hardcoded

        # Current time
        self._time_mark()

    def _load_job(self, name):
        """Load a job given a name"""

        # Create empty job
        j = jobs.Job()

        # Load dict # FUTURE
        d = self.fh.load_job(name)

        # Load it into an object
        j.from_json(d)

        return j

    def _save_job(self, j):
        """Given a job, dump it to a json file."""

        # Make sure it can be dump
        if not j.can_dump():
            basic.perror("Job can't be saved to json")

        # Get name
        name = j.get_name()

        # Assure folder
        self.fh.save_job(j, name)

    def _get_job_names(self):
        """Get all the existing job names."""
        return self.fh.list_jobs()

    def _job_exists(self, name):
        """Bool indicating if job exists"""
        return name in self._get_job_names()

    def _assert_time(self, action="action"):
        """Assert the time variable set."""
        if self.t is None:
            basic.perror("Can't {} without a timestamp".format(action))

    def _time_mark(self):
        """Saves the current time."""
        self.t = datetime.now()


    """API methods"""
    def start_job(self, name, info):
        """Option to start a job."""
        self._assert_time("start a job")

        j = self._load_job(name)
        result = j.start(self.t, info)
        if result.is_ok():
            print_action(name, "started")
            self._save_job(j)
        else:
            print_error(name, result.status)

    def stop_job(self, name, info=None, stop_all=False, discard=False, quiet=True):
        """Option to stop a job."""

        # Assert time
        self._assert_time("stop a job")

        def _stop_job(n, discard):
            """Stop a given job."""
            # REVIEW: receive job it self, not names?

            # Load job
            j = self._load_job(n)

            # Confirmation
            if j.confirm_discard():
                if not basic.input_y_n(question="Are you sure you want to discard an entry for '{}'".format(n)):
                    discard = False

            # Stop
            result = j.stop(self.t, discard=discard, obs=info)

            if result.is_ok():
                self._save_job(j)
                # Print action
                action = "stopped"
                if discard:
                    action += ", entry discarded"
                print_action(n, action)

                # Print times
                if not quiet:
                    print("\t Runtime: total: {}, effective: {}, pause: {}".format(
                                basic.sec2hr(result.total_time),
                                basic.sec2hr(result.effective_time),
                                basic.sec2hr(result.pause_time)))

            else:
                print_error(n, result.status)

        if stop_all:
            for nn in self._get_job_names():
                _stop_job(nn, discard)
        else:
            _stop_job(name, discard)

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
        if self._job_exists(name):
            q = "A previous work called '{}' exists. Do you want to override it".format(name)
            if not basic.input_y_n(question=q):
                return

        j = jobs.Job()
        j.create(name, lname, info, tags)
        self._save_job(j)

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

        shown = 0
        for n in names:
            j = self._load_job(n)
            if match(n, name) and filter_running(j):
                j.pprint(self.t, name_only=name_only, show_entries=show_entries)
                shown += 1

        if shown == 0:
            print("No jobs to show")

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
