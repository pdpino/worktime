"""Module that provides classes to handle the application."""
from datetime import datetime
from re import search
import basic
from backend import filesys as fs, jobs

class Application():
    """Handle the application."""

    def __init__(self, root_path):
        """Constructor."""
        # File Handler
        self.fh = fs.FileHandler(root_path, "files")

        # Current time
        self._time_mark()

    def _load_job(self, name):
        """Load a job given a name"""

        # Assure folder
        self.fh.assure_folder()

        # Get filename
        fname = self.fh.get_fname(name)

        # Load job
        j = jobs.Job()

        try:
            j.from_json(fname)
        except FileNotFoundError:
            basic.perror("Can't find the job '{}', maybe you haven't created it?".format(name))

        return j

    def _save_job(self, j, backup=False):
        """Given a job, dump it to a json file."""
        str_fname = self.fh.get_fname(backup=backup)
        j.to_json(str_fname)

    def _get_job_names(self):
        """Get all the existing job names."""
        return self.fh.list_files(".json")

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
    def close(self):
        """Close the application."""
        self.t = None

    def start_job(self, name, info):
        """Option to start a job."""
        self._assert_time("start a job")

        j = self._load_job(name)
        j.start(self.t, info)
        self._save_job(j)

    def _stop_job(self, name, **kwargs):
        """Stop a given job."""
        # REVIEW: receive job it self, not names?
        self._assert_time("stop a job")

        j = self._load_job(name)
        j.stop(self.t, **kwargs)
        self._save_job(j)

    def stop_job(self, name, info=None, stop_all=False, discard=False, quiet=True):
        """Option to stop a job."""
        if stop_all:
            for n in self._get_job_names():
                self._stop_job(n, ign_error=True)
        else:
            self._stop_job(name, discard=discard, print_time=(not quiet), obs=info)

    def pause_job(self, name, wait=False):
        """Option to pause a job."""
        self._assert_time("pause a job")

        j = self._load_job(name)
        j.pause(self.t)

        if wait: # Wait for input
            input("Press enter to unpause the job ")
            self._time_mark() # Take another mark
            j.pause(self.t)

        # Save to json
        self._save_job(j)

    def create_job(self, name, lname, info, tags):
        """Option to create a job."""
        q = "A previous work called '{}' exists. Do you want to override it".format(name)
        if not self._job_exists(name) or basic.input_y_n(question=q):
            j = jobs.Job()
            j.create(name, lname, info, tags)
            self._save_job(j)

    def edit_job(self, name, new_name=None, new_lname=None, new_info=None, info_mode=None, new_tags=None, tags_mode=None):
        """Option to edit a job."""
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

        if self._job_exists(name):
            q = "Are you sure you want to drop '{}'".format(name)
            if force or basic.input_y_n(question=q, default="n"):
                j = self._load_job(name)
                j.delete()
                self.fh.remove_file(name)
        else:
            basic.perror("The work '{}' does not exists".format(name))

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
            j = self._load_job(name)
            self._save_job(j, backup=True)
        print("Jobs backed up")

    def update(self):
        """Make an update to the Job objects."""
        for name in self._get_job_names():
            j = self._load_job(name)
            j.update()
            self._save_job(j, backup=False)
