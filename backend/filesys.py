"""Module that handles the interaction with the files."""
import os
import shutil
from collections import OrderedDict
import json
import basic

def get_dict(obj):
    """Return the dict to dump as json.

    Each class that is dumped should have a method: get_keys(),
    which return a list of the attributes to dump in order.
    If the class doesn't have a method, all the attributes will be dumped in any order"""
    # REVIEW: move this method to basic ???

    try: # REVIEW: use if, instead of try/except
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

class JsonFileHandler:
    """Provide basic functionality to handle files."""

    def __init__(self, root_path, files_path, backup_path="backup"):
        """Constructor."""
        # Individual folders
        self._root = root_path + "/"
        self._files = files_path + "/"
        self._backup = backup_path + "/"

        # Absolute folder
        self.files_folder = self._root + self._files

        # Absolute folder strings to fullfil
        self._str_files = self.files_folder + "{}.json"
        self._str_backup = self.files_folder + self._backup + "{}.json"

    def assure_folder(self):
        """Assure the existence of the needed folders."""
        folder = self.files_folder
        if not os.path.exists(folder):
            try:
                os.mkdir(folder)
            except:
                basic.perror("Can't create folder: {}".format(folder), exception=e)

    def list_files(self, extension):
        """List the files of a folder, given an extension."""

        folder = self.files_folder # folder to lookup
        names = []
        n = len(extension)

        # Search through the files in the folder
        for f in os.listdir(folder): # list everything in the folder
            if os.path.isfile(os.path.join(folder, f)): # is a file
                if f.endswith(extension): # ends with the correct extension
                    only_name = f[:-n] # Trim the extension
                    names.append(only_name)

        return names

    def get_fname(self, name=None, backup=False):
        """Given a name, return the filename for the json file."""

        if not backup:
            string = self._str_files
        else:
            string = self._str_backup

        if not name is None:
            string = string.format(name)

        return string

    def remove_file(self, name):
        """Remove a file"""
        fname = self.get_fname(name, backup=False)
        os.remove(fname)

    def copy_file(self, name1, name2):
        """Copy a file from name1 to name2."""
        shutil.copyfile(name1, name2)

class JobFileHandler(JsonFileHandler):
    """Provides functionality to save files in json format."""

    def save_job(self, j, name):
        """Save a job to json."""

        # Assure folder
        self.assure_folder()

        # Get the filename
        fname = self.get_fname(name, backup=False)

        # Try to save
        try:
            with open(fname, "w") as f:
                json.dump(j, f, default=get_dict, sort_keys=False, indent=4)
        except Exception as e:
            basic.perror("Can't dump '{}' to json".format(fname), exception=e)

    def load_job(self, name):
        """Load a job from json."""
        # Assure folder
        self.assure_folder()

        # Get filename
        fname = self.get_fname(name)

        try:
            # Load the json dict
            with open(fname, "r") as f:
                d = json.load(f)
        except FileNotFoundError:
            basic.perror("Can't find the job '{}', maybe you haven't created it?".format(name))

    def backup_job(self, name):
        """Backup a job."""
        fname_original = self.get_fname(name, backup=False)
        fname_backup = self.get_fname(name, backup=True)
        self.copy_file(fname_original, fname_backup)
