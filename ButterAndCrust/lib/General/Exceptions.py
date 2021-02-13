


def throw_warning(warning_str):
    """
    Throws a warning message and asks user if they would like to continue
    """
    error = warning_str
    warning = "\n\nWARNING: {e} Continue? [Y/N]\n\n".format(e=error)
    cont = input(warning)
    if cont.lower() == "n":
        raise RuntimeError(error)