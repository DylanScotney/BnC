from airtable import Airtable
import pandas as pd
import datetime as dt

import ButterAndCrust.lib.DB.Tables.CompressedOrderHistory as s
from ButterAndCrust.lib.PackageConfig import ORDERS_DB_LOC

def main():
    base_key = "appWCrLerVduIq5SR"
    api_key = "keyQNWjWomXyaBGJK"
    airtable = CompressedOrderHistory(base_key, api_key)

    # all_records = airtable.get_all()
    # df = pd.DataFrame.from_records((r['fields'] for r in all_records))

    sqlTable = s.CompressedOrderHistory(ORDERS_DB_LOC)

    orders = sqlTable.select(where="(Email = 'alexemmajones@gmail.com' OR Email = '1980kbu@gmail.com') AND DeliveryDate <= date('2021-03-01')")
    # print(orders)
    orders = orders.to_dict(orient='records')

    airtable.sync(orders)

class CompressedOrderHistory(Airtable):
    """
    A simple helper for the Airtable library that makes using common
    queries for BnC user friendly
    """
    NAME = "CompressedOrderHistory"

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
        df['DeliveryDate'] = pd.to_datetime(df['DeliveryDate'], format='%Y-%m-%dT%H:%M:%S.%fZ')
        return df

    def get_max_deliverydate(self):
        """
        Gets the maximum value of a specified column in the table.

        Args:
            col_name(``str``): name of field
        """
        df = self._records_to_df(self.get_all())

        return df['DeliveryDate'].max()

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

    def sync(self, records):
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


if __name__ == "__main__":
    main()