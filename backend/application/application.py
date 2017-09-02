"""Module that provides classes to handle the application."""
from datetime import datetime
import subprocess
from re import search
from backend import jobs, results as rs, filesys as fs
import basic

class AdminData():
    """Handle administrative and configuration data."""

    def __init__(self):
        """Constructor."""
        self.selected_job_name = None

    def from_json(self, d):
        """Load admin data from a dict (loaded from json)."""
        if not d is None:
            self.__dict__ = d

    def get_keys(self):
        """Return the attributes that will be saved to json."""
        return ["selected_job_name"]

    def select_job(self, name):
        # REFACTOR: use property
        self.selected_job_name = name

    def get_selected_job(self):
        return self.selected_job_name

    def update(self):
        """Update function."""

        ### ADD YOUR UPDATES HERE ###

class Application():
    """Handle the application."""

    def __init__(self, root_path, notify=False):
        """Constructor."""
        self.fh = fs.JobFileHandler(root_path, "files") # HACK: "files" hardcoded
        self._mark_time()
        self.admin_fh = fs.AdminFileHandler(root_path, "config", "admin") # "config" and "admin" hardcoded
        self.admin_data = AdminData()
        self.admin_data.from_json(self.admin_fh.load_admin())

        self.notify = notify

    def close(self):
        """Close the application."""
        self.admin_fh.save_admin(self.admin_data)

    def _choose_name(self, name):
        """If name is None, return the selected name in the admin data."""
        return name or self.admin_data.get_selected_job()

    def _load_job(self, name):
        """Load a job given a name."""
        job = jobs.Job()
        json_dict = self.fh.load_job(name)
        job.from_json(json_dict)

        return job

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

    def _exist_job(self, name):
        """Bool indicating if job exists"""
        return self.fh.exist_job(name) #name in self._get_job_names()

    def _assert_time(self, action="action"):
        """Assert the time variable set."""
        if self.t is None:
            basic.perror("Can't {} without a timestamp".format(action))

    def _mark_time(self):
        """Saves the current time."""
        self.t = datetime.now()

    def _notify_action(self, jobname=None, action=None):
        """Notify an action to the screen."""
        if self.notify:
            title = "Worktime"
            message = jobname or ""
            message += " "
            message += action or ""
            subprocess.run("notify-send --urgency=critical '{}' '{}'".format(title, message), shell=True)
            # NOTE: use return_value.returncode of run() to see the status of the called command

    """API methods"""
    def start_job(self, name, info):
        """Option to start a job."""
        self._assert_time("start a job")

        # REFACTOR: this is copied in start/stop/pause methods, use decorators
        name = self._choose_name(name)
        if name is None:
            return rs.StartResult(rs.ResultType.NotSelected)

        if not self._exist_job(name):
            return rs.StartResult(rs.ResultType.NotExist, jobname=name)

        job = self._load_job(name)
        result = job.start(self.t, info)
        if result.is_ok():
            self._save_job(job)

        return result

    def stop_job(self, name, confirmation, info=None, discard=False):
        """Option to stop a job.

        confirmation -- function to call if confirmation for discarding an entry is needed"""

        self._assert_time("stop a job")

        name = self._choose_name(name)
        if name is None:
            return rs.StopResult(rs.ResultType.NotSelected)

        if not self._exist_job(name):
            return rs.StopResult(rs.ResultType.NotExist, jobname=name)

        j = self._load_job(name)

        # Confirmation
        if j.confirm_discard(): # Confirmation needed
            if not confirmation(): # Ask for confirmation
                discard = False

        result = j.stop(self.t, discard=discard, obs=info)

        if result.is_ok():
            self._save_job(j)

        return result

    def pause_job(self, name):
        """Option to pause a job."""
        self._assert_time("pause a job")

        name = self._choose_name(name)
        if name is None:
            return rs.PauseResult(rs.ResultType.NotSelected)

        j = self._load_job(name)
        result = j.pause(self.t)
        if result.is_ok():
            self._save_job(j)

        return result

    def create_job(self, name, confirmation, lname=None, info=None, tags=None):
        """Option to create a job."""
        if self._exist_job(name):
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

        if not self._exist_job(name):
            return rs.DeleteResult(rs.ResultType.NotExist)

        deleted = False
        if force or confirmation():
            j = self._load_job(name)
            self.fh.remove_job(name)
            deleted = True

        return rs.DeleteResult(was_deleted=deleted)

    def select_job(self, name):
        """Select a job to use later without calling the name."""
        if name is None:
            return rs.Result(rs.ResultType.NoneNotAccepted)
        elif self._exist_job(name):
            self.admin_data.select_job(name)
            return rs.Result()
        else:
            return rs.Result(rs.ResultType.NotExist)

    def unselect_job(self):
        """Unselect a job."""
        prev_jobname = self.admin_data.get_selected_job()
        if not prev_jobname is None:
            self.admin_data.select_job(None)
            return rs.UnselectResult(jobname=prev_jobname)
        else:
            return rs.UnselectResult(status=rs.ResultType.NotSelected)

    def show_jobs(self, name, run_only=False):
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
        self.admin_data.update()

        for name in self._get_job_names():
            j = self._load_job(name)
            j.update()
            self._save_job(j)

        return rs.Result()
