
class CompressedOrderHistory():

    def __init__(self):

        self.name = 'CompressedOrderHistory'
        self.PK = 'ID'
        self.columns = {
                    'ID': 'INTEGER NOT NULL',
                    'Email': 'TEXT NOT NULL',
                    'DeliveryDate': 'DATETIME NOT NULL',
                    'Lineitems': 'TEXT NOT NULL'
                    }

    def generate_create_table_string(self):
        """
        returns the sql string required to create the table with sqlite
        """

        table = ('''
        CREATE TABLE CompressedOrderHistory(
        ID INTEGER NOT NULL,
        Email TEXT NOT NULL,
        DeliveryDate DATETIME NOT NULL,
        Lineitems TEXT NOT NULL
        ''')

        indices = [self.PK]

        return table, indices
