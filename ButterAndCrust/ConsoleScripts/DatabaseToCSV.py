import datetime as dt
import argparse

import ButterAndCrust.lib.DB.DB_queries as DB
import ButterAndCrust.lib.PackageConfig as PC
from ButterAndCrust.lib.DB.Tables.CompressedOrderHistory import CompressedOrderHistory

def main():
    parser = argparse.ArgumentParser(description="Produce csv file of DB")
    parser.add_argument("-date", help="delivery date of orders YYYY/mm/dd", type=lambda s: dt.datetime.strptime(s, '%Y/%m/%d'), required=False)
    args = parser.parse_args()

    table = CompressedOrderHistory(PC.ORDERS_DB_LOC)

    if args.date:
        df = table.select_by_delivery_date(args.date,
                                           args.date + dt.timedelta(days=1))
        filename = "CompressedOrderHistory_{}.csv".format(args.date.strftime("%Y%m%d"))

    else:
        df = table.select()
        filename = "CompressedOrderHistory_All.csv"

    df.to_csv(PC.DEFAULT_OUTPUT_LOCATION + filename)

if __name__ == "__main__":
    main()
