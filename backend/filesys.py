"""Module that handles the interaction with the files."""
import os
import shutil
from collections import OrderedDict
import json
import basic

class JsonFileHandler:
    """Provide basic functionality to handle files."""

    def __init__(self, root_path, files_path, backup_path="backup"):
        """Constructor."""
        # Individual folders
        self._root = root_path + "/"
        self._files = files_path + "/"
        self._backup = backup_path + "/"
        self._archive = "archive/" # hardcoded

        # Absolute folder
        self.files_folder = self._root + self._files

        # Absolute folder strings to fullfil
        self._str_files = self.files_folder + "{}.json"
        self._str_backup = self.files_folder + self._backup + "{}.json"
        self._str_archive = self.files_folder + self._archive + "{}.json"

    def _assure_folder(self, folder=None):
        """Assure the existence of folder."""
        folder = folder or self.files_folder
        if not os.path.exists(folder):
            try:
                os.mkdir(folder)
            except:
                basic.perror("Can't create folder: {}".format(folder), exception=e)

    def _list_files(self):
        """List the files of a folder."""

        extension = ".json"
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

    def _get_fname(self, name=None, backup=False, archive=False):
        """Given a name, return the filename for the json file."""

        if backup:
            string = self._str_backup
        elif archive:
            string = self._str_archive
        else:
            string = self._str_files

        if not name is None:
            string = string.format(name)

        return string

    def _remove_file(self, name):
        """Remove a file"""
        fname = self._get_fname(name, backup=False)
        os.remove(fname)

    def _backup_file(self, name):
        """Copy a file in the backup folder."""
        self._assure_folder()
        fname_original = self._get_fname(name, backup=False)
        fname_backup = self._get_fname(name, backup=True)

        shutil.copyfile(fname_original, fname_backup)

    def _archive_file(self, name, unarchive=False):
        """Move file between archived/unarchived folders."""
        # Assuring archive folder
        self._assure_folder(self.files_folder + self._archive)

        fname_original = self._get_fname(name, archive=unarchive)
        fname_dest = self._get_fname(name, archive=(not unarchive))

        os.rename(fname_original, fname_dest)

    def _save_file(self, obj, name):
        """Save an object to a json file."""
        self._assure_folder()
        fname = self._get_fname(name, backup=False)

        with open(fname, "w") as f:
            json.dump(obj, f, default=self._get_dict, sort_keys=False, indent=4)

    def _load_file(self, name):
        """Load an object from json."""
        self._assure_folder()
        fname = self._get_fname(name)

        with open(fname, "r") as f:
            d = json.load(f)
        return d

    def _get_dict(self, obj):
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

    def _exist_file(self, name, archive=False):
        """Boolean indicating if a job exists."""
        fname = self._get_fname(name, backup=False, archive=archive)
        return os.path.isfile(fname)

class JobFileHandler(JsonFileHandler):
    """Wrapper for the JsonFileHandler, used for jobs."""

    def save_job(self, job, name):
        """Save a job to json."""
        super()._save_file(job, name)

    def load_job(self, name):
        """Load a job from json."""
        try:
            json_obj = self._load_file(name)
            return json_obj
        except FileNotFoundError:
            basic.perror("Can't find the job '{}', maybe you haven't created it?".format(name))

    def backup_job(self, name):
        """Backup a job."""
        self._backup_file(name)

    def archive_job(self, name):
        """Archive a job."""
        self._archive_file(name, unarchive=False)

    def unarchive_job(self, name):
        """Unarchive a job."""
        self._archive_file(name, unarchive=True)

    def list_jobs(self):
        """List the jobs."""
        return self._list_files()

    def remove_job(self, name):
        """Remove a job."""
        self._remove_file(name)

    def exist_job(self, name, archive=False):
        return self._exist_file(name, archive=archive)

class AdminFileHandler(JsonFileHandler):
    """Wrapper to use the JsonFileHandler, used for admin files."""

    def __init__(self, root_path, files_path, fname):
        """Constructor."""
        self.fname = fname
        super().__init__(root_path, files_path)

    def save_admin(self, admin_data):
        """Save admin data to json."""
        super()._save_file(admin_data, self.fname)

    def load_admin(self):
        """Load the admin data from json."""
        try:
            json_obj = self._load_file(self.fname)
            return json_obj
        except FileNotFoundError:
            return None
