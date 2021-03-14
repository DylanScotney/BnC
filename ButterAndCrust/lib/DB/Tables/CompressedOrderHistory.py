import datetime as dt
import abc
from airtable import Airtable
import pandas as pd

from ButterAndCrust.lib.DB.Tables.SQLTable import SQLTable

class ICompressedOrderHistory(metaclass=abc.ABCMeta):
    """
    Simple interface for the CompressedOrderHistory table. 
    Using this allows to safely switch between using Airtable or 
    SQLLite for backend storage.

    Includes several abstract methods that are required for order
    and packing slip processing
    """

    NAME = "CompressedOrderHistory"

    @abc.abstractmethod
    def get_max(self, col_name: str):
        """
        Gets the maximum value of a specified column in the table.

        Args:
            col_name(``str``): name of field

        Returns:
            max value in col_name
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_all_by_IDs(self, IDs: list):
        """
        Gets all orders by order ID. 

        Args:
            IDs(``list of ints``): list of order IDs to get 

        Returns: 
            (``list``): list of records
        """
        raise NotImplementedError
    
    @abc.abstractmethod
    def get_most_recent_order_by_email(self):
        """
        Gets each customers most recent order and returns the results 
        in a dateframe. 

        Args: 
            current_date(``datetime``, optional): current date, default
                is today
            cutoff(``int``): max number of days before current_date
                to load
        
        Returns:
            df(``DataFrame``): Dataframe of each customers most recent 
                orders
        """
        raise NotImplementedError

    @abc.abstractmethod
    def sync_by_ID(self, records: list):
        """
        Will syncronise a list of records onto the table. 
        Updates existing records and inserts new ones

        Args:
            records(``list``): list of records to sync
        """
        raise NotImplementedError

class airCompressedOrderHistory(Airtable, ICompressedOrderHistory):
    """
    Airtable implementation of CompressedOrderHistory
    """
    def __init__(self, base_key, api_key):

        NAME = "CompressedOrderHistory"

        super().__init__(base_key, NAME, api_key)
        self.name = NAME
        self._base_key = base_key
        self._api_key = api_key

    def _records_to_df(self, records):
        """
        Converts list of records into a pandas df
        """
        df = pd.DataFrame.from_records((r['fields'] for r in records))

        # convert dtypes
        df['DeliveryDate'] = pd.to_datetime(df['DeliveryDate'], format='%Y-%m-%dT%H:%M:%S.%fZ')
        df['Last Modified'] = pd.to_datetime(df['Last Modified'], format='%Y-%m-%dT%H:%M:%S.%fZ')
        df['Created'] = pd.to_datetime(df['Created'], format='%Y-%m-%dT%H:%M:%S.%fZ')
        df['Email'] = df['Email'].astype('unicode')
        df['Lineitems'] = df['Lineitems'].astype('unicode')
        df['BillingAddress'] = df['BillingAddress'].astype('unicode')
        df['ShippingAddress'] = df['ShippingAddress'].astype('unicode')
        df['DeliveryNotes'] = df['DeliveryNotes'].astype('unicode')

        return df

    def get_max(self, col_name):
        """
        Gets the maximum value of a specified column in the table.

        Args:
            col_name(``str``): name of field

        Returns:
            max value in col_name
        """
        df = self._records_to_df(self.get_all())

        return df[col_name].max()

    def get_all_by_IDs(self, IDs):
        """
        Gets all orders by order ID. 

        Args:
            IDs(``list of ints``): list of order IDs to get 

        Returns: 
            (``list``): list of records
        """

        formula = "OR(" + ",".join(["{ID}=" + str(ID) for ID in IDs]) + ")"
        return self.get_all(formula=formula)

    def get_all_by_delivery_date(self, start_date, end_date):
        """
        Gets all records by delivery date between [start_date, end_date)

        Args: 
            start_date(``datetime``): start date to get orders (inclusive)
            end_date(``datetime``): end date to get orders (exclusive)
        """

        start_date = start_date.date() if isinstance(start_date, dt.datetime) else start_date
        end_date = end_date.date() if isinstance(end_date, dt.datetime) else end_date
        start_date = start_date.strftime("%Y/%m/%d")
        end_date = (end_date).strftime("%Y/%m/%d")

        formula = """
            AND(
                {{{col}}}<DATETIME_PARSE('{f_date}', 'YYYY/MM/DD'),
                {{{col}}}>=DATETIME_PARSE('{s_date}' , 'YYYY/MM/DD')
            )
        """.format(
                col="DeliveryDate",
                f_date=end_date,
                s_date=start_date
            )

        records = self.get_all(formula=formula)
        df = self._records_to_df(records)
        return df

    def get_most_recent_order_by_email(self, current_date=dt.date.today(),
                                       cutoff=28):
        """
        Gets each customers most recent order and returns the results 
        in a dateframe. 

        Args: 
            current_date(``datetime``, optional): current date, default
                is today
            cutoff(``int``): max number of days before current_date
                to load
        
        Returns:
            df(``DataFrame``): Dataframe of each customers most recent 
                orders
        """
        cutoff_date = current_date - dt.timedelta(days=cutoff + 1)

        df = self.get_all_by_delivery_date(cutoff_date, current_date)
        df = df.loc[df.reset_index().groupby(['Email'])['DeliveryDate'].idxmax()]

        return df

    def sync_by_ID(self, records):
        """
        Will syncronise a list of records onto the table. 
        Updates existing records and inserts new ones

        Args:
            records(``list``): list of records to sync
        """

        IDs = [r['ID'] for r in records]

        existing_records_to_update = self.get_all_by_IDs(IDs)

        IDs_to_update = [r['fields']['ID'] for r in existing_records_to_update]

        records_to_insert = [r for r in records if r['ID'] not in IDs_to_update]
        records_to_update = [{'id': self.match('ID', r['ID'])['id'], 'fields': r} for r in records if r['ID'] in IDs_to_update]

        self.batch_insert(records_to_insert)        
        self.batch_update(records_to_update)

class sqlCompressedOrderHistory(SQLTable, ICompressedOrderHistory):
    """
    SQLLite implementation of CompressedOrderHistory.
    """

    def __init__(self, db_file):
        """
        Instantiates a new instance of a sqlCompressedOrderHistory
        obj. 

        Args:
            db_file(``str``): filepath of sqllite db file
        """
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

    def get_max(self, col_name):
        """
        Gets the maximum value of a specified column in the table.

        Args:
            col_name(``str``): name of field

        Returns:
            max value in col_name
        """
        return self.max(col_name)

    def get_all_by_IDs(self, IDs):
        """
        Gets all orders by order ID. 

        Args:
            IDs(``list of ints``): list of order IDs to get 

        Returns: 
            (``list``): list of records
        """
        where = "ID in (" + ",".join((str(id) for id in IDs)) + ")"
        return self.select(where=where)

    def get_all_by_delivery_date(self, start_date, end_date):
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

    def sync_by_ID(self, records):
        """
        Will syncronise a list of records onto the table. 
        Updates existing records and inserts new ones. 

        Args:
            records(``list``): list of records to sync
        """
        self.sync(records, ['ID'])

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
