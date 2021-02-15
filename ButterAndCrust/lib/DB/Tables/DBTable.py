
class DBTable(object):
    """
    DBTable class.

    Base class object with name and column attributes
    """
    def __init__(self, table_name, columns):
        self.name = table_name
        self.columns = columns
