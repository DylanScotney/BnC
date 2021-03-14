import argparse

import ButterAndCrust.lib.PackageConfig as PC
from ButterAndCrust.lib.OrderProcessor import OrderProcessor
from ButterAndCrust.lib.DB.Tables.AirTable import CompressedOrderHistory

def main():
    parser = argparse.ArgumentParser(description="Process B&C Weekly Orders")
    parser.add_argument("-file", help="location of weekly orders csv file", type=str, required=True)
    parser.add_argument("-date", help="delivery date of input orders YYYY/mm/dd", type=str, required=True)
    args = parser.parse_args()
    
    d = args.date.replace("/","")

    outfile = PC.DEFAULT_OUTPUT_LOCATION + "/RequiredStock_{}.csv".format(d)

    # TO DO: REBUILD BODY BEFORE PROCESSING ORDERS.
    
    order_table = CompressedOrderHistory(PC.base_key, PC.api_key)
    order_processor = OrderProcessor(args.file, args.date, order_table)
    order_processor.process_orders(outfile)

if __name__ == "__main__":
    main()
