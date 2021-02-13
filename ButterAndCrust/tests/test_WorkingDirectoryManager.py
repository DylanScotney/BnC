import os

from lib.General.WorkingDirectoryManager import WorkingDirectoryManager

def test_safe_deletion_1():
    """
    Test that checks the safe deletion of a working dir on
    deconstruction
    """
    working_dir = "C:/temp/"
    manager = WorkingDirectoryManager(working_dir)
    unique_working_dir = manager.working_directory

    assert os.path.exists(unique_working_dir)

    del manager

    assert not os.path.exists(unique_working_dir)


def test_safe_deletion_2():
    """
    Test that checks the safe deletion of a working dir on
    deconstruction
    """
    working_dir = "C:/temp/"
    unique_working_dir = ""

    for _ in range(0):
        manager = WorkingDirectoryManager(working_dir)
        unique_working_dir = manager.working_directory

        assert os.path.exists(unique_working_dir)

    assert not os.path.exists(unique_working_dir)

