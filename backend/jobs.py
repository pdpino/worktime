"""Module that provides classes to handle the jobs"""
import basic

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

    def get_name(self):
        """Return the name."""
        # REVIEW: use properties?
        return self.name

    def can_dump(self):
        """Boolean indicating if the job can be dump to a file."""
        return self._is_created

    def from_json(self, d):
        """Create the job from a dict (readed from json)."""
        if self._is_created:
            basic.perror("Job can't be loaded from json, is already created")

        # Save the dict in the object
        self.__dict__ = d

        # HACK: "_entry" and "entries" hardcoded
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
