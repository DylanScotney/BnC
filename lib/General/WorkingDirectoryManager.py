from django.utils.crypto import get_random_string
import shutil
import os

class WorkingDirectoryManager():
    """
    A working directory manager that will construct it's own unique 
    working directory and safely delete all it's contents on
    deconstruction. 

    Arguments:
        :param working_dir:         (str) file path to create a working
                                    directory

    Attributes:
        _working_directory:         (str) full file path of the unique
                                    working directory
    """
    def __init__(self, working_dir):

        # construct a unique working dir on init
        unique_working_dir = get_random_string(22)

        while os.path.exists(working_dir + "/" + unique_working_dir):
            unique_working_dir = get_random_string(22)
        
        self._working_directory = working_dir + "/" + unique_working_dir + "/"
        os.mkdir(self.working_directory)
    
    def __del__(self):
        """
        Deletes the working directory and all it's contents on
        deconstruction
        """
        if os.path.exists(self.working_directory):
            shutil.rmtree(self.working_directory)

    def clear_working_dir(self):
        if os.path.exists(self.working_directory):
            for filename in os.listdir(self.working_directory):
                file_path = os.path.join(self.working_directory, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print('Failed to delete %s. Reason: %s' % (file_path, e))

    @property
    def working_directory(self):
        return self._working_directory
