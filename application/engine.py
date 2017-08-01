"""Module to manage jobs"""
import json
from datetime import datetime
from collections import OrderedDict
from re import search
import basic
import application.data as data

def get_dict(obj):
    """Return the dict to dump as json.

    Each class that is dumped should have a method: get_keys(),
    which return a list of the attributes to dump in order.
    If the class doesn't have a method, all the attributes will be dumped in any order"""
    # REVIEW: move this method to basic ???

    try:
        # Try get keys of the class
        keyorder = obj.get_keys()

        if keyorder is None:
            return None

        # Obtain subset of keys
        d = {k:obj.__dict__[k] for k in keyorder if k in obj.__dict__}

        return OrderedDict(sorted(d.items(), key=lambda i:keyorder.index(i[0])))
    except AttributeError as e:
        basic.perror("Can't get keys from {} object, {}".format(type(obj), obj.__dict__), exception=e, force_continue=True)
        return obj.__dict__


class Entry():
    """Entry of a job, i.e. instance"""

    """Basic methods."""
    def __init__(self):
        """Constructor."""
        self._is_created = False

    def _create(self):
        """Set is_created bool, validates the attributes."""
        self._is_created = True

    def _close(self):
        """Finish an entry."""
        self.finished = True

        # REVIEW: change name by _finish?

        # function to round 2 decimals
        round_decs = lambda x: float("{0:.2f}".format(x))

        self.total_time = round_decs(self.total_time)
        self.effective_time = round_decs(self.effective_time)
        self.pause_time = round_decs(self.pause_time)

    def from_json(self, d):
        """Load the entry from a dict (loaded from json)"""
        if not d is None:
            self.__dict__ = d
            self._create()

    def update(self):
        """Update the objects, given a change in the structure."""

        ### ADD HERE YOUR UPDATES TO ENTRIES ###

    def get_keys(self):
        """Return the keys of the attributes to save to json."""
        if not self._is_created:
            return None

        if self.finished:
            return ["obs", "finished",
                    "date",
                    "hi", "hf",
                    "n_pauses",
                    "total_time", "effective_time", "pause_time"]
        else:
            return ["obs", "finished", "is_paused",
                    "date",
                    "hi",
                    "n_pauses",
                    "total_time", "effective_time", "pause_time",
                    "_ti", "_pi"]


    """Operations."""
    def start(self, t, obs=""):
        """Create a new entry."""
        self.obs = ""
        self.add_obs(obs)

        # Fecha de inicio
        fecha = basic.date(t)
        self.date = "{}/{}/{}".format(*fecha) #[0], fecha[1], fecha[2])

        # Tiempo inicio
        self.hi = basic.hour(t) # hora inicio: H:M
        self._ti = basic.seconds(t) # tiempo inicio: segundos

        # Tiempo fin
        #self.hf = 0
        #self._tf = 0

        # Tiempo pausa
        self._pi = 0 # inicio pausa
        self.n_pauses = 0

        # Contadores
        self.total_time = 0
        self.effective_time = 0
        self.pause_time = 0

        # Booleans
        self.finished = False
        self.is_paused = False

        # Validate
        self._create()

    def stop(self, t):
        """Stop working."""
        if self.finished:
            basic.perror("Can't stop a finished entry")

        if self.is_paused:
            # Si es esta en pausa, unpause()
            self.pause(t)

        self.hf = basic.hour(t) # hora termino
        tf = basic.seconds(t) # segundos termino

        # calcular tiempos
        self.total_time = tf - self._ti
        self.effective_time = self.total_time - self.pause_time

        # Close the entry
        self._close()

    def pause(self, t):
        """Toggle pause/unpause the entry.

        If pausing, return number of pauses made
        else, return time paused"""
        if self.finished:
            basic.perror("Can't pause a finished entry")

        if self.is_paused:
            # sacar de pausa
            pf = basic.seconds(t) # pausa final
            p_time = pf - self._pi # pause time actual
            self.pause_time += p_time # sumar pause time al total de la entry

            self.is_paused = False

            return p_time
        else:
            # poner en pausa
            self._pi = basic.seconds(t) # pausa init
            self.n_pauses += 1

            self.is_paused = True

            return self.n_pauses


    """Get methods."""
    def pstr(self):
        """Pretty string"""
        if not self._is_created:
            return ""

        if self.obs != "":
            obs = "\n\t\t{}".format(self.obs)
        else:
            obs = self.obs

        if self.finished:
            horas = "{} to {} -- total: {} -- pause: {} -- effective: {}".format(self.hi, self.hf, basic.sec2hr(self.total_time), basic.sec2hr(self.pause_time), basic.sec2hr(self.effective_time))
        else:
            horas = "{}-present".format(self.hi)

        return "{} -- {} {}".format(self.date, horas, obs)

    def ctime_running(self, t):
        """ Current time running
        Get the total time for a running entry"""
        if t is None:
            return "unknown"
        return basic.sec2hr(basic.seconds(t)-self._ti)

    def ctime_effective(self, t):
        """ Current time effective.
        Get the effective time for a running entry"""
        if t is None:
            return "unknown"
        return basic.sec2hr(basic.seconds(t)-self._ti-self.pause_time)

    def ctime_paused(self, t):
        """ Current time paused
        Get the pause time for a running entry"""
        if t is None:
            return "unknown"
        return basic.sec2hr(basic.seconds(t)-self._pi)

    def add_obs(self, obs):
        """Add observation for an entry."""
        if not obs is None:
            if len(self.obs) > 0:
                self.obs += ". "
            self.obs += str(obs)

class Job():
    """Job"""

    def __init__(self):
        self._is_created = False

    def _create(self):
        """Set is_created bool, validates the attributes."""
        self._is_created = True

    def create(self, name, longname, info, tags):
        """Create a Job from"""
        self.name = name
        self.longname = longname
        self.info = info

        if tags is None:
            self.tags = list()
        else:
            self.tags = list(tags)

        self.entries = []

        self._entry = None # current entry
        self.is_running = False
        self.is_paused = False # solo valido si is_running=True, indica si esta en pause

        # Validates the rest of attributes
        self._create()

    def get_keys(self):
        """Return the keys of the attributes to save to a json."""
        return ["name", "longname", "info",
                "tags",
                "is_running", "is_paused",
                "_entry", "entries"]

    def to_json(self, str_fname):
        """Dump the object to a json file."""
        if not self._is_created:
            basic.perror("Job can't be saved to json, isn't created")

        # Format filename
        fname = str_fname.format(self.name)

        try:
            with open(fname, "w") as f:
                json.dump(self, f, default=get_dict, sort_keys=False, indent=4)
        except Exception as e:
            basic.perror("Can't dump '{}' to json".format(self.name), exception=e)

    def from_json(self, fname):
        """Create the job from a json file."""
        if self._is_created:
            basic.perror("Job can't be loaded from json, is already created")

        # Load the json dict
        with open(fname, "r") as f:
            d = json.load(f)

        # Save the dict in the object
        self.__dict__ = d

        # Load current entry
        if "_entry" in d:
            _entry = Entry()
            _entry.from_json(d["_entry"])
            self._entry = _entry
        else:
            self._entry = None

        # Load all entries
        entries = []
        for i in range(len(d["entries"])):
            e = Entry()
            e.from_json(d["entries"][i])
            entries.append(e)
        self.entries = entries

        self._create()

    def update(self):
        """Update the Job given a change in the structure."""

        ### ADD HERE YOUR UPDATES TO JOBS ###

        # Update entries
        self._entry.update()
        for e in self.entries:
            e.update()



    """Basic operations methods."""
    def start(self, t, obs=""):
        if self.is_running:
            basic.perror("Work '{}' is already running".format(self.name))

        # Crear entrada de lista
        self._entry = Entry()
        self._entry.start(t, obs)

        self._print_action("started")
        self.is_running = True
        self.is_paused = False

    def pause(self, t):
        if not self.is_running:
            basic.perror("Work '{}' is not running".format(self.name))

        # Toggle pause
        r = self._entry.pause(t)
        if self.is_paused: # sacar de pausa
            self._print_action("unpaused", additional="paused time: {}".format(basic.sec2hr(r)))
            self.is_paused = False
        else: # poner en pausa
            self._print_action("paused")
            self.is_paused = True

    def stop(self, t, discard=False, print_time=True, ign_error=False, obs=None):
        """ Stop a running job"""
        if not self.is_running:
            if ign_error:
                return
            else:
                basic.perror("Work '{}' is not running".format(self.name))


        self._entry.add_obs(obs)
        self._entry.stop(t)
        ttime = self._entry.total_time # total time
        etime = self._entry.effective_time # effective time
        ptime = self._entry.pause_time # pause time

        # Preguntar si esta seguro que quiere descartar
        if discard and etime > 30*60: # etime > 30min
            if not basic.input_y_n(question="You've been working more than half an hour. Are you sure you want to discard it"):
                discard = False

        # Anadir entrada
        if not discard:
            self.entries.append(self._entry)
        self._entry = None

        # Reportar accion al user
        action = "stopped"
        if discard:
            action += ", entry discarded"
        self._print_action(action)

        # Change
        self.is_running = False
        self.is_paused = False

        if print_time and not discard:
            self._print_times(ttime, etime, ptime)

    def delete(self):
        """Delete the job."""
        self._print_action("deleted")



    """Printing methods"""
    def _print_times(self, ttime, etime, ptime):
        """Print in screen the given times"""
        print("\t Runtime: total: {}, effective: {}, pause: {}".format(
                        basic.sec2hr(ttime),
                        basic.sec2hr(etime),
                        basic.sec2hr(ptime)))

    def _print_action(self, action, additional=None):
        """Print to stdout an action."""
        w = "{} {}".format(self.name, action)
        if not additional is None:
            w += " -- {}".format(additional)
        print(w)

    def _str_entries(self):
        """Concatenate string of all entries."""
        # Initial string
        string = ""
        def str_entry(s, e):
            """Concatenate the string from the entry e"""
            return s + "\t{}\n".format(e.pstr())

        # All the entries
        for s in self.entries:
            string = str_entry(string, s)

        # Current entry
        if not self._entry is None:
            string = str_entry(string, self._entry)

        return string

    def _str_status(self, t):
        if not self._is_created:
            return "job not created"

        if self.is_running:
            if self.is_paused:
                status = "paused ({} in pause)".format(self._entry.ctime_paused(t))
            else:
                status = "running (total: {}, effective: {})".format(
                            self._entry.ctime_running(t),
                            self._entry.ctime_effective(t))
        else:
            status = "stopped"

        return status

    def pprint(self, t=None, name_only=False, show_entries=False):
        """Pretty print for a job."""
        if not self._is_created:
            basic.perror("Can't print an empty job")

        # Fix Nones
        lname = self.longname or "-"
        info = self.info or "-"

        # Status string
        status = self._str_status(t)

        # String to print
        if name_only:
            w = "{}".format(self.name)
        else:
            w = """{}
            long name:  {}
            info:       {}
            tags:       {}
            status:     {}
            total runs: {}""".format(self.name, lname, info, self.tags, status, len(self.entries))

        if show_entries:
            w += "\n\tEntries: "
            if len(self.entries) > 0:
                w += "\n"
                w += self._str_entries()
            else:
                w += "None\n"

        print(w)


    """Edit methods"""
    def edit_info(self, i, mode):
        """Edit the Job info"""
        if i is None:
            return

        if mode is None:
            mode = "add" # DEFAULT

        # If mode is add, but there is no info, then replace
        if mode == "add" and len(self.info) == 0:
            mode = "replace"

        # REVIEW: change the mode by an enum
        if mode == "add":
            self.info += ". " + i
        elif mode == "replace":
            self.info = i
        elif mode == "drop":
            self.info = ""
            self._print_action("dropped info")
        else: # Mode not supported
            basic.perror("Edit info mode '{}' not supported".format(mode))

    def edit_tags(self, t, mode):
        """Edit the Job tags"""
        if t is None:
            return

        if mode is None:
            mode = "add" # DEFAULT

        if mode == "add":
            self.tags += t
        elif mode == "replace":
            self.tags = t
        elif mode == "drop":
            self.tags = list()
            self._print_action("dropped tags")
        else:
            basic.perror("Edit tags mode '{}' not supported".format(mode))

    def change_longname(self, ln):
        """Change the current longname by ln"""
        self.longname = ln

    def change_name(self, n):
        """Change the Job name by n"""
        self.name = n
        # TODO: cambiar nombre de json file

class Engine():
    """Handle the application"""

    def __init__(self, root_path):
        """Constructor."""
        # File Handler
        self.fh = data.FileHandler(root_path, "files")

        # Current time
        self._time_mark()

    def _load_job(self, name):
        """Load a job given a name"""

        # Assure folder
        self.fh.assure_folder()

        # Get filename
        fname = self.fh.get_fname(name)

        # Load job
        j = Job()

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

    def create_job(self, name, lname, info, tags):
        """Option to create a job."""
        q = "A previous work called '{}' exists. Do you want to override it".format(name)
        if not self._job_exists(name) or basic.input_y_n(question=q):
            j = Job()
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
