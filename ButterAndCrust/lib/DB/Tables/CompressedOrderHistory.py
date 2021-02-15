import datetime as dt

from ButterAndCrust.lib.DB.Tables.SQLTable import SQLTable

class CompressedOrderHistory(SQLTable):

    def __init__(self, db_file):
        _NAME = "CompressedOrderHistory"
        _COLUMNS = [
            'ID',
            'Email',
            'DeliveryDate',
            'Lineitems',
            'BillingAddress',
            'ShippingAddress',
            'Total',
            'DeliveryNotes'
        ]
        _INDICES = [
            SQLTable.index("unique_ID", ["ID"], is_unique=True),
            SQLTable.index("dup_Email", ["Email"], is_unique=False)
        ]

        super().__init__(_NAME, _COLUMNS, db_file, _INDICES)

    def select_by_delivery_date(self, start_date, end_date):
        """
        Selects all the orders in a given table between start_date and 
        end_date and returns as a pandas df.

        Args:
            start_date(``datetime``): inclusive intial date of orders
            end_date(``datetime``): exclusive final date of orders

        """

        sql = (
        '''
            SELECT *
            FROM {table}
            WHERE DeliveryDate >= date('{i_date}') 
            AND DeliveryDate < date('{f_date}')
        '''.format(
                table=self.name,
                i_date=start_date,
                f_date=end_date
            )
        )

        return self.sql_to_df(sql)

    def get_most_recent_order_by_email(self, delivery_date, cutoff=28):
        """
        Gets the most recent order by email that was delivered less than 
        cutoff weeks ago.

        Args:
            delivery_date(``datetime``) the current delivery date
            cutoff(``int``) max number of days to lookback in the db
        
        Returns:
            (``DataFrame``) DataFrame of query results
        """

        cut_off_date = delivery_date - dt.timedelta(days=cutoff)

        sql = (
        '''
        SELECT ID, Email, DeliveryDate, Lineitems
        FROM
        (
            SELECT 
                ID,
                Email, 
                DeliveryDate,
                Lineitems,
                MAX(DeliveryDate) OVER (PARTITION BY Email) MaxDeliveryDate
            FROM
            (
                SELECT 
                    ID,
                    Email, 
                    DeliveryDate,
                    Lineitems
                FROM CompressedOrderHistory
                WHERE DeliveryDate < date('{d_date}') 
                AND DeliveryDate >= date('{c_date}')
            )
        )
        WHERE DeliveryDate = MaxDeliveryDate
        '''.format(
                d_date=delivery_date,
                c_date=cut_off_date
            )
        )

        return self.sql_to_df(sql)

    def generate_create_table_string(self):
        """
        returns the sql string required to create the table with sqlite
        """

        table = ('''
        CREATE TABLE CompressedOrderHistory(
        ID INTEGER NOT NULL,
        Email TEXT NOT NULL,
        DeliveryDate DATETIME NOT NULL,
        Lineitems TEXT NOT NULL,
        BillingAddress TEXT NOT NULL,
        ShippingAddress TEXT NOT NULL,
        Total DOUBLE NOT NULL, 
        DeliveryNotes TEXT NOT NULL
        )
        ''')

        return table
