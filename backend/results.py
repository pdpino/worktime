"""Provides classes to save the results of an action."""
from enum import Enum

class ResultType(Enum):
    """Provides an enum for the possibles statuses of a result.

    An action not necessarily can result on any of this statuses, this is a generic enum"""
    OK = 0
    Cancelled = 1 # Cancelled by user

    AlreadyExist = 10 # Job already exist
    NotExist = 11 # Job doesn't exist

    AlreadyRunning = 20 # Job already running
    NotRunning = 21 # Job isn't running


class Result(object):
    """Generic result object."""

    def __init__(self, status=None):
        """Constructor."""
        if status is None:
            self.status = ResultType.OK
        else:
            self.status = status

    def is_ok(self):
        return self.status == ResultType.OK

class StopResult(Result):
    """Result object for the 'stop' action."""

    def __init__(self, status=None, ttime=0, etime=0, ptime=0):
        """Constructor.

        ttime -- total time
        etime -- effective time
        ptime -- pause time"""

        super().__init__(status)

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

class ShowResult(Result):
    """Result object for the 'show' action."""


    def __init__(self, status):
        """Constructor."""

        super().__init__(status)

        print("ShowResult not implemented")
