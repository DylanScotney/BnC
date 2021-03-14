import datetime as dt
import argparse

import ButterAndCrust.lib.PackageConfig as PC
from ButterAndCrust.lib.templates.main.StandardHTMLTemplate import template as html_template
import ButterAndCrust.lib.General.Exceptions as e
from ButterAndCrust.lib.PackingSlipManager import PackingSlipManager
from ButterAndCrust.lib.DB.Tables.CompressedOrderHistory import airCompressedOrderHistory

def main():
    parser = argparse.ArgumentParser(description="Produce B&C packing slips")
    parser.add_argument("-date", help="delivery date of orders YYYY/mm/dd", type=str, required=True)
    parser.add_argument("-file", help="file containing route order information", type=str, required=False)
    args = parser.parse_args()

    routes_file = args.file
    delivery_date = check_input_date(args.date)
    outfile = PC.DEFAULT_OUTPUT_LOCATION + "PackingSlips_{date}.pdf".format(date=delivery_date.strftime("%Y%m%d"))

    packing_slip_manager = PackingSlipManager(outfile, PC.WORKING_DIRECTORY,
                                              html_template, PC.PATH_WKHTMLTOPDF)
    
    order_table = airCompressedOrderHistory(PC.base_key, PC.api_key)
    packing_slip_manager.produce_packing_slips(delivery_date, routes_file, order_table)

def check_input_date(datestr):
    """
    Warns user if the input date is a Saturday and asks if would like to
    continue.
    """
    date = dt.datetime.strptime(datestr, "%Y/%m/%d")

    if date.weekday() != 5:
        e.throw_warning("Input delivery date is not a Saturday.")

    return date


if __name__ == "__main__":
    main()
