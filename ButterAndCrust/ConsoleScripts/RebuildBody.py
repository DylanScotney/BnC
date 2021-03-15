import argparse
import datetime as dt
import json

import ButterAndCrust.lib.PackageConfig as PC
from ButterAndCrust.lib.OrderProcessor import OrderProcessor
from ButterAndCrust.lib.DB.Tables.CompressedOrderHistory import airCompressedOrderHistory, sqlCompressedOrderHistory

def main():
    order_airtable = airCompressedOrderHistory(PC.base_key, PC.api_key)
    order_sqltable = sqlCompressedOrderHistory(PC.COLD_STORAGE_ORDERS_DB_LOC)

    rebuild_body(order_sqltable, order_airtable)

def rebuild_body(body, head, date=dt.datetime.today(), cutoff=29):
    """
    Moves records that are older than date - cutoff days old
    from the head table (airtable) to the body (sqlite3 cold storage)

    Args:
        body(``sqlCompressedOrderHistory``): SQLLite cold storage 
            CompressedOrderHistory table
        head(``airCompressedOrderHistory``): airtable implementation 
            of CompressedOrderHistory. Typically only contains the 
            last 4 weeks of orders
        date(``datetime``): Delivery date
        cutoff(``int``): Orders with a delivery date before
            date - timedelta(days=cutoff) will be moved to cold storage
    """

    end_date = date - dt.timedelta(days=cutoff)

    # Get all orders to move from head table
    df = head.get_all_by_delivery_date(dt.datetime.min, dt.datetime.max)

    # convert delivery date column to string so it can be safely synced
    # to no sql
    df['DeliveryDate'] = df['DeliveryDate'].dt.strftime('%Y-%m-%d')

    # Drop unused columns and convert df to records format
    orders_for_cold_storage = df.drop(columns=['Last Modified', 'Created']).to_dict('records')

    # Sync orders to cold storage 
    body.sync_by_ID(orders_for_cold_storage)

    # # Get order IDs of the records we are moving 
    # IDs_to_del = [r['ID'] for r in orders_for_cold_storage]

    # # Get airtable records of the IDs we are moving
    # records_to_del = head.get_all_by_IDs(IDs_to_del)
    
    # # airtable record IDs
    # recordIDs_to_del = [r['id'] for r in records_to_del]

    # # batch delete from head using airtable record id    
    # head.batch_delete(recordIDs_to_del)

if __name__ == "__main__":
    main()