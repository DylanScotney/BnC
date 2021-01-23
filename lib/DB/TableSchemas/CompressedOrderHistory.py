
class CompressedOrderHistory():

    def __init__(self):

        self.name = 'CompressedOrderHistory'
        self.PK = 'ID'
        self.columns = {
                    'ID': 'INTEGER NOT NULL',
                    'Email': 'TEXT NOT NULL',
                    'DeliveryDate': 'DATETIME NOT NULL',
                    'Lineitems': 'TEXT NOT NULL',
                    'ReceivedFortnightlyCoffee': 'BOOL NULL'
                    }
