import os

from ButterAndCrust.lib.General.WorkingDirectoryManager import WorkingDirectoryManager

def test_safe_deletion_1():
    """
    Test that checks the safe deletion of a working dir on
    deconstruction
    """
    working_dir_path = "C:/temp/"
    working_directory = WorkingDirectoryManager(working_dir_path)
    unique_working_dir = working_directory.path

    assert os.path.exists(unique_working_dir)

    del working_directory

    assert not os.path.exists(unique_working_dir)


def test_safe_deletion_2():
    """
    Test that checks the safe deletion of a working dir on
    deconstruction
    """
    working_dir_path = "C:/temp/"
    unique_working_dir = ""

    for _ in range(0):
        working_directory = WorkingDirectoryManager(working_dir_path)
        unique_working_dir = working_directory.path

        assert os.path.exists(unique_working_dir)

    assert not os.path.exists(unique_working_dir)

def test_dirpath_safely_ends():
    """
    Test that dirpath ends in "/"
    """
    working_dir_path = "C:/temp/"

    working_dir = WorkingDirectoryManager(working_dir_path)
    

    assert working_dir.path.endswith("/")

    


