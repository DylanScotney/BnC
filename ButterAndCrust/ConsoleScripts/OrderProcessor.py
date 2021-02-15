from datetime import datetime as dt
import pandas as pd
import sqlite3
import argparse
import pdfkit
import os
import shutil
import csv

from ButterAndCrust.lib.Order import Order
from ButterAndCrust.lib.Address import Address
import ButterAndCrust.lib.PackageConfig as PC
import ButterAndCrust.lib.General.Exceptions as e
import ButterAndCrust.lib.General.FileQueries as file_queries
from ButterAndCrust.lib.DB.Tables.CompressedOrderHistory import CompressedOrderHistory
from ButterAndCrust.lib.DB.Tables.SQLTable import SQLTable
from ButterAndCrust.lib.templates.main.StandardHTMLTemplate import template

def main():
    parser = argparse.ArgumentParser(description="Process B&C Weekly Orders")
    parser.add_argument("-file", help="location of weekly orders csv file", type=str, required=True)
    parser.add_argument("-date", help="delivery date of input orders YYYY/mm/dd", type=str, required=True)
    args = parser.parse_args()

    input_delivery_date = check_input_date(args.date)
    input_file = args.file
    OrdersDB = SQLTable.create_connection(PC.ORDERS_DB_LOC)
    check_last_delivery(input_delivery_date, OrdersDB)
    proccess_orders(input_file, input_delivery_date, PC.ORDERS_DB_LOC)

def check_last_delivery(delivery_date, db_file):
    """
    Checks if the last processed delivery date was more than a week ago 
    and warns if true
    """
    table = CompressedOrderHistory(db_file)
    last_delivery_date = table.max("DeliveryDate")

    if last_delivery_date is None:
        e.throw_warning("No deliveries have been processed for last Saturday.")
    else:
        diff = delivery_date - dt.strptime(last_delivery_date[:10], "%Y-%m-%d")

        if diff.days > 7:
            e.throw_warning("No deliveries have been processed for last Saturday.")

        if diff.days < 0:
            e.throw_warning("Non chronological delivery dates.")

def check_input_date(datestr):
    """
    Warns user if the input date is a Saturday and asks if would like to
    continue.
    """
    date = dt.strptime(datestr, "%Y/%m/%d")

    if date.weekday() != 5:
        e.throw_warning("Input delivery date is not a Saturday.")

    return date

def is_fortnightly_coffee(text):
    """
    Determines whether an item string is fornightly coffee lineitem
    """
    item = text.lower()
    return ("coffee" in item
            and ("every fortnight" in item
            or "every other week" in item)
            )

def proccess_orders(file_path, delivery_date, db_file):
    
    compressed_orders = CompressedOrderHistory(db_file)
    input_delivery_date = delivery_date
    orders = dict()
    total_items = dict()
    input_orders = pd.read_csv(file_path, na_filter=False)
    prev_orders = compressed_orders.get_most_recent_order_by_email(delivery_date)

    # Process orders into a list of Order() objects so they're managable
    #==========================================================================
    for _, row in input_orders.iterrows():

        orderID = int(row['Name'][1:])

        # create a new Order() if this is a new orderID
        if orderID not in orders:
            orders[orderID] = Order(orderID, row['Email'])

        # get customers previous order if there is any
        prev_order = prev_orders[prev_orders['Email'].str.contains(orders[orderID].email)]

        orders[orderID].delivery_date = input_delivery_date

        if row['Total'] and not row['Total'].isspace():
            orders[orderID].update_total(float(row['Total']))

        if row['Notes'] and not row['Notes'].isspace():
            orders[orderID].notes = row['Notes']
        
        item_qty_str = row['Lineitem quantity']
        item_qty = int(item_qty_str) if item_qty_str else 0
        item_price_str = row['Lineitem price']
        item_price = float(item_price_str) if item_price_str else 0.0
        item = row['Lineitem name']

        if not (is_fortnightly_coffee(item)
             and prev_order['Lineitems'].apply(func=is_fortnightly_coffee).any()
            ):
            # don't add fornightly coffee if they had it in their last order
            orders[orderID].add_lineitem(item, item_price, item_qty)
        
        billing_info = Address(
                                row['Billing Name'],
                                row['Billing Street'],
                                row['Billing Address1'],
                                row['Billing Address2'],
                                row['Billing Company'],
                                row['Billing City'],
                                row['Billing Zip'],
                                row['Billing Province'],
                                row['Billing Country'],
                                row['Billing Phone']
                            )
        orders[orderID].add_billing_info(billing_info)

        shipping_info = Address(
                                row['Shipping Name'],
                                row['Shipping Street'],
                                row['Shipping Address1'],
                                row['Shipping Address2'],
                                row['Shipping Company'],
                                row['Shipping City'],
                                row['Shipping Zip'],
                                row['Shipping Province'],
                                row['Shipping Country'],
                                row['Shipping Phone']
                            )
        orders[orderID].add_shipping_info(shipping_info)
    #==========================================================================

    # Sync orders to the CompressedOrderHistory DB Table and save each order
    # to a file.
    # Technically this is inefficient as we are iterating over orders twice
    # but for small set this should be ok for now
    #==========================================================================
    compressed_rows = []

    for orderID in orders:
        order = orders[orderID]      
        lineitems = ""

        # format lineitems for table
        for item in order.lineitems:
            qty = order.lineitems[item]['quantity']

            if item in total_items:
                total_items[item] += qty
            else:
                total_items[item] = qty

            for _ in range(qty):
                lineitems += item + "|"

        lineitems = lineitems[:-1]
        compressed_rows += [{
            "ID": orderID, 
            "Email": order.email,
            "DeliveryDate": order.delivery_date.strftime("%Y-%m-%d"),
            "Lineitems": lineitems,
            "BillingAddress": str(order.billing_info),
            "ShippingAddress": str(order.shipping_info),
            "Total": order.total,
            "DeliveryNotes": order.notes
        }]
        
    file_output_format = PC.DEFAULT_OUTPUT_LOCATION + "{name}_{date}.{ext}"
    csv_out_loc = file_output_format.format(name="RequiredStock", date=delivery_date.strftime("%Y%m%d"), ext="csv")
    file_queries.write_items_to_csv(["Lineitem", "Quantity"], total_items, csv_out_loc)

    # sync values to db table
    compressed_orders.sync(compressed_rows, ["ID"])

    return total_items
    #==========================================================================

if __name__ == "__main__":
    main()
