from django.utils.crypto import get_random_string
import shutil
import os
import posixpath

class WorkingDirectoryManager():
    """
    A working directory manager that will construct it's own unique 
    working directory and safely delete all it's contents on
    deconstruction. 

    Arguments:
        :param working_dir:         (str) file path to create a working
                                    directory

    Attributes:
        _path:         (str) full file path of the unique
                                    working directory
    """
    def __init__(self, working_dir):

        # construct a unique working dir on init
        unique_working_dir = get_random_string(22)

        path = posixpath.join(working_dir + "/" + unique_working_dir)
        while os.path.exists(path):
            unique_working_dir = get_random_string(22)
            path = posixpath.join(working_dir + "/" + unique_working_dir)
        
        self._path = posixpath.join(path, "")
        os.mkdir(self.path)
    
    def __del__(self):
        """
        Deletes the working directory and all it's contents on
        deconstruction
        """
        if os.path.exists(self.path):
            shutil.rmtree(self.path)

    def clear_working_dir(self):
        if os.path.exists(self.path):
            for filename in os.listdir(self.path):
                file_path = os.path.join(self.path, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print('Failed to delete %s. Reason: %s' % (file_path, e))

    @property
    def path(self):
        return self._path
