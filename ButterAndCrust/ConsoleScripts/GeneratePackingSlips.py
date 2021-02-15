import datetime as dt
import os
import argparse
import pandas as pd

import ButterAndCrust.lib.PackageConfig as PC
import ButterAndCrust.lib.DB.DB_queries as DB
from ButterAndCrust.lib.templates.main.StandardHTMLTemplate import template as html_template
from ButterAndCrust.lib.Order import Order
import ButterAndCrust.lib.General.FileQueries as file_queries
import ButterAndCrust.lib.General.Exceptions as e
from ButterAndCrust.lib.PackingSlipManager import PackingSlipManager

def main():
    parser = argparse.ArgumentParser(description="Produce B&C packing slips")
    parser.add_argument("-date", help="delivery date of orders YYYY/mm/dd", type=str, required=True)
    parser.add_argument("-file", help="file containing route order information", type=str, required=False)
    args = parser.parse_args()

    routes_file = args.file
    delivery_date = dt.datetime.strptime(args.date, "%Y/%m/%d")
    outfile = PC.DEFAULT_OUTPUT_LOCATION + "PackingSlips_{date}.pdf".format(date=delivery_date.strftime("%Y%m%d"))

    packing_slip_manager = PackingSlipManager(outfile, PC.WORKING_DIRECTORY,
                                              html_template, PC.PATH_WKHTMLTOPDF)
    
    packing_slip_manager.produce_packing_slips(delivery_date, routes_file, PC.ORDERS_DB_LOC)

if __name__ == "__main__":
    main()
