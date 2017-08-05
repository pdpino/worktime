"""Module that handles the interaction with the files."""
import os
import shutil
import basic

class FileHandler:
    """Handle filenames"""

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
