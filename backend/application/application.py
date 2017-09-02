"""Module that provides classes to handle the application."""
from datetime import datetime
from re import search
from backend import jobs, results as rs, filesys as fs
import basic

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

        # Load dict
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
            self._save_job(j)

        return result

    def stop_job(self, name, confirmation, info=None, discard=False):
        """Option to stop a job.

        confirmation -- function to call if confirmation for discarding an entry is needed"""

        # Assert time
        self._assert_time("stop a job")

        # Load job
        j = self._load_job(name)

        # Confirmation
        if j.confirm_discard(): # Confirmation needed
            if not confirmation(): # Ask for confirmation
                discard = False

        # Stop
        result = j.stop(self.t, discard=discard, obs=info)

        if result.is_ok():
            self._save_job(j)

        return result

    def pause_job(self, name):
        """Option to pause a job."""
        self._assert_time("pause a job")

        j = self._load_job(name)
        result = j.pause(self.t)
        if result.is_ok():
            self._save_job(j)

        return result

    def create_job(self, name, confirmation, lname=None, info=None, tags=None):
        """Option to create a job."""
        if self._job_exists(name):
            if not confirmation():
                return rs.Result(rs.ResultType.Cancelled)

        j = jobs.Job()
        result = j.create(name, lname, info, tags)

        if result.is_ok():
            self._save_job(j)

        return result

    def edit_job(self, name, new_name=None, new_lname=None, new_info=None, info_mode=None, new_tags=None, tags_mode=None):
        """Option to edit a job."""

        basic.perror("DEPRECATED: can't edit job")

        j = self._load_job(name)

        # Cambiar nombre
        if not new_name is None:
            # j.change_name(new_name)
            pass # TODO

        if not new_lname is None:
            j.change_longname(new_lname)

        if not new_info is None:
            j.edit_info(new_info, info_mode)

        if not new_tags is None:
            j.edit_tags(new_tags, tags_mode)

        self._save_job(j)

    def delete_job(self, name, confirmation, force=False):
        """Option to delete a job."""

        if not self._job_exists(name):
            return rs.DeleteResult(rs.ResultType.NotExist)

        deleted = False
        if force or confirmation():
            j = self._load_job(name)
            self.fh.remove_job(name)
            deleted = True

        return rs.DeleteResult(was_deleted=deleted)

    def show_jobs(self, name, run_only=False, name_only=False, show_entries=False):
        """Option to show jobs."""

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

        # Functions to filter
        match = dont_match if name is None else match_regex
        filter_running = dont_match if not run_only else is_running

        results = rs.ShowResult()
        for n in names:
            j = self._load_job(n)
            if match(n, name) and filter_running(j):
                result = j.show(self.t)
                results.add_job(result)

        return results

    def backup_jobs(self):
        """Backup existing jobs."""
        for name in self._get_job_names():
            self.fh.backup_job(name)

        return rs.Result()

    def update_jobs(self):
        """Make an update to the Job objects."""
        for name in self._get_job_names():
            j = self._load_job(name)
            j.update()
            self._save_job(j)

        return rs.Result()
