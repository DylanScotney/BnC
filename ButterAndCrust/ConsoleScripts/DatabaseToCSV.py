import datetime as dt
import argparse

import ButterAndCrust.lib.DB.DB_queries as DB
import ButterAndCrust.lib.PackageConfig as PC
from ButterAndCrust.lib.DB.TableSchemas.CompressedOrderHistory import CompressedOrderHistory

def main():
    parser = argparse.ArgumentParser(description="Produce csv file of DB")
    parser.add_argument("-date", help="delivery date of orders YYYY/mm/dd", type=lambda s: dt.datetime.strptime(s, '%Y/%m/%d'), required=False)
    args = parser.parse_args()
    OrdersDB = DB.create_connection(PC.ORDERS_DB_LOC)

    table = CompressedOrderHistory()

    if args.date:
        df = DB.select_all_by_delivery_date(table.name,
                                            args.date,
                                            args.date + dt.timedelta(days=1),
                                            OrdersDB)
        filename = "CompressedOrderHistory_{}.csv".format(args.date.strftime("%Y%m%d"))

    else:
        df = DB.select_all(table.name, OrdersDB)
        filename = "CompressedOrderHistory_All.csv"

    df.to_csv(PC.DEFAULT_OUTPUT_LOCATION + filename)

if __name__ == "__main__":
    main()
