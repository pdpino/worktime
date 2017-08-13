"""Provides classes to save the results of an action."""
from enum import Enum

class ResultType(Enum):
    """Provides an enum for the possibles statuses of a result.

    An action not necessarily can result on any of this statuses, this is a generic enum"""
    OK = 0
    Cancelled = 1 # by user
    InternalError = 2

    AlreadyExist = 10 # Job already exist
    NotExist = 11 # Job doesn't exist

    AlreadyRunning = 20 # Job already running
    NotRunning = 21 # Job isn't running

class Result(object):
    """Generic result object."""

    def __init__(self, status=None, message=None):
        """Constructor. if status is None then OK, there is an optional message"""
        if status is None:
            self.status = ResultType.OK
        else:
            self.status = status

        self.message = message

    def is_ok(self):
        return self.status == ResultType.OK

class StopResult(Result):
    """Result object for the 'stop' action."""

    def __init__(self, status=None, was_discard=False, ttime=0, etime=0, ptime=0):
        """Constructor.

        ttime -- total time
        etime -- effective time
        ptime -- pause time"""

        super().__init__(status)

        self.was_discard = was_discard
        self.total_time = ttime
        self.effective_time = etime
        self.pause_time = ptime

class PauseResult(Result):
    """Result object for the 'pause' action."""

    def __init__(self, status=None, was_paused=False, pause_time=0):
        """Constructor.

        was_paused -- if true the job was paused, else the job was unpaused. Only works if status is OK"""

        super().__init__(status)
        self.was_paused = was_paused
        self.pause_time = pause_time

class ShowEntry(object):
    """Container for entry attributes to show."""
    def __init__(self, date, hour_init, hour_end, total_time, effective_time, pause_time, obs):
        self.date = date
        self.hour_init = hour_init
        self.hour_end = hour_end
        self.total_time = total_time
        self.effective_time = effective_time
        self.pause_time = pause_time
        self.obs = obs

class ShowJob(object):
    """Container for job attributes to show."""
    def __init__(self, name, longname, info, tags, status, total_time, effective_time, pause_time, total_runs, show_entries):
        self.name = name
        self.longname = longname
        self.info = info
        self.tags = tags
        self.status = status
        self.total_time = total_time
        self.effective_time = effective_time
        self.pause_time = pause_time
        self.total_runs = total_runs
        self.entries = show_entries

class ShowResult(Result):
    """Result object for the 'show' action."""

    def __init__(self, status=None):
        """Constructor."""

        super().__init__(status)

        self.jobs = []

    def add_job(self, var):
        """Add a job to the result."""
        # if type(var) is Result: # hack
        #     self.status = var.status
        #     self.message = var.message

        self.jobs.append(var)

    def no_jobs(self):
        """Boolean indicating if no jobs to show"""
        return len(self.jobs) == 0

    def __iter__(self):
        """Iterate over the jobs."""
        for j in self.jobs:
            yield j
