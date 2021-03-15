import argparse
import datetime as dt

import ButterAndCrust.lib.PackageConfig as PC
from ButterAndCrust.lib.OrderProcessor import OrderProcessor
from ButterAndCrust.lib.DB.Tables.CompressedOrderHistory import airCompressedOrderHistory, sqlCompressedOrderHistory

def main():
    order_airtable = airCompressedOrderHistory(PC.base_key, PC.api_key)
    order_sqltable = sqlCompressedOrderHistory(PC.COLD_STORAGE_ORDERS_DB_LOC)

    end_date = dt.datetime.today() - dt.timedelta(days=29)
    df = order_airtable.get_all_by_delivery_date(dt.datetime.min, end_date)
    df['DeliveryDate'] = df['DeliveryDate'].dt.strftime('%Y-%m-%d')

    orders_for_cold_storage = df.to_dict('records')
    order_sqltable.sync_by_ID(orders_for_cold_storage)

    IDs_to_del = [r['ID'] for r in orders_for_cold_storage]
    # order_airtable.batch_delete()
    print(IDs_to_del)
    records_to_del = order_airtable.get_all_by_IDs(IDs_to_del)
    
    recordIDs_to_del = [r['id'] for r in records_to_del]
    print(recordIDs_to_del)
    
    order_airtable.batch_delete(recordIDs_to_del)


if __name__ == "__main__":
    main()