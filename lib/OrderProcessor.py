from datetime import datetime as dt
import pandas as pd
import sqlite3
import argparse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.conf import settings
import pdfkit
import os
import shutil
import csv

from .Order import Order
from .Address import Address
from .PackageConfig import *
from .DB import DB_queries as DB
from .DB.TableSchemas.CompressedOrderHistory import CompressedOrderHistory
from .templates.main.StandardHTMLTemplate import template

def main():
    settings.configure()
    parser = argparse.ArgumentParser(description="Process B&C Weekly Orders")
    parser.add_argument("-file", help="location of weekly orders csv file", type=str, required=True)
    parser.add_argument("-date", help="delivery date of input orders YYYY/mm/dd", type=str, required=True)
    args = parser.parse_args()

    input_delivery_date = check_input_date(args.date)
    input_file = args.file
    OrdersDB = DB.create_connection(ORDERS_DB_LOC)
    check_last_delivery(input_delivery_date, OrdersDB)

    OrdersDB = DB.create_connection(ORDERS_DB_LOC)
    proccess_orders(input_file, input_delivery_date, OrdersDB)

def check_last_delivery(delivery_date, db_conn):
    """
    Checks if the last processed delivery date was more than a week ago 
    and warns if true
    """
    last_delivery_date = DB.get_max_value("CompressedOrderHistory", "DeliveryDate", db_conn)

    if last_delivery_date is None:
        throw_warning("No deliveries have been processed for last Saturday.")
    else:
        diff = delivery_date - dt.strptime(last_delivery_date[:10], "%Y-%m-%d")

        if diff.days > 7:
            throw_warning("No deliveries have been processed for last Saturday.")

        if diff.days < 0:
            throw_warning("Non chronological delivery dates.")


def throw_warning(warning_str):
    """
    Throws a warning message and asks user if they would like to continue
    """
    error = warning_str
    warning = "\n\nWARNING: {e} Continue? [Y/N]\n\n".format(e=error)
    cont = input(warning)
    if cont.lower() == "n":
        raise RuntimeError(error)

def check_input_date(datestr):
    """
    Warns user if the input date is a Saturday and asks if would like to
    continue.
    """
    date = dt.strptime(datestr, "%Y/%m/%d")

    if date.weekday() != 5:
        throw_warning("Input delivery date is not a Saturday.")

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

def proccess_orders(file_path, delivery_date, db_conn):
    
    input_delivery_date = delivery_date
    orders = dict()
    total_items = dict()
    input_orders = pd.read_csv(file_path, na_filter=False)
    prev_orders = DB.get_most_recent_order_by_email(input_delivery_date, db_conn)

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

        # Add order data 
        if row['Paid at'] and not row['Paid at'].isspace():
            orders[orderID].add_payment_date(dt.strptime(row['Paid at'][:18], '%Y-%m-%d %H:%M:%S'))

        if row['Total'] and not row['Total'].isspace():
            orders[orderID].update_total(float(row['Total']))

        if row['Subtotal'] and not row['Subtotal'].isspace():
            orders[orderID].update_subtotal(float(row['Subtotal']))

        if row['Shipping'] and not row['Shipping'].isspace():
            orders[orderID].shipping_fee = float(row['Shipping'])

        if row['Taxes'] and not row['Taxes'].isspace():
            orders[orderID].taxes = float(row['Taxes'])
        
        if row['Currency'] and not row['Currency'].isspace():
            orders[orderID].ccy = row['Currency']
        
        if row['Financial Status'] and not row['Financial Status'].isspace():
            orders[orderID].financial_status = row['Financial Status']

        if row['Fulfillment Status'] and not row['Fulfillment Status'].isspace():
            orders[orderID].fulfillment_status = row['Fulfillment Status']

        if row['Fulfilled at'] and not row['Fulfilled at'].isspace():
            orders[orderID].fulfillment_date = dt.strptime(row['Fulfilled at'][:18], '%Y-%m-%d %H:%M:%S')

        if row['Accepts Marketing'] and not row['Accepts Marketing'].isspace():
            orders[orderID].accepts_marketing = row['Accepts Marketing']
        
        if row['Discount Code'] and not row['Discount Code'].isspace():
            orders[orderID].discount_code = row['Discount Code']

        if row['Discount Amount'] and not row['Discount Amount'].isspace():
            orders[orderID].discount_code = float(row['Discount Amount'])

        if row['Shipping Method'] and not row['Shipping Method'].isspace():
            orders[orderID].shipping_method = row['Shipping Method']

        if row['Created at'] and not row['Created at'].isspace():
            orders[orderID].creation_date = dt.strptime(row['Created at'][:18], '%Y-%m-%d %H:%M:%S')

        if row['Notes'] and not row['Notes'].isspace():
            orders[orderID].notes = row['Notes']

        if row['Note Attributes'] and not row['Note Attributes'].isspace():
            orders[orderID].notes_attributes = row['Note Attributes']

        if row['Cancelled at'] and not row['Cancelled at'].isspace():
            orders[orderID].cancellation_date = dt.strptime(row['Cancelled at'][:18], '%Y-%m-%d %H:%M:%S')
        
        if row['Payment Method'] and not row['Payment Method'].isspace():
            orders[orderID].payment_method = row['Payment Method']

        if row['Payment Reference'] and not row['Payment Reference'].isspace():
            orders[orderID].payment_reference = row['Payment Reference']

        if row['Refunded Amount'] and not row['Refunded Amount'].isspace():
            orders[orderID].refunded_amount = float(row['Refunded Amount'])

        if row['Vendor'] and not row['Vendor'].isspace():
            orders[orderID].vendor = row['Vendor']        
        
        if row['Tags'] and not row['Tags'].isspace():
            orders[orderID].tags = row['Tags']

        if row['Risk Level'] and not row['Risk Level'].isspace():
            orders[orderID].risk_level = row['Risk Level']

        if row['Source'] and not row['Source'].isspace():
            orders[orderID].source = row['Source']
        
        if row['Phone'] and not row['Phone'].isspace():
            orders[orderID].phone = row['Phone']
        
        if row['Receipt Number'] and not row['Receipt Number'].isspace():
            orders[orderID].receipt_number = row['Receipt Number']
        
        item_qty_str = row['Lineitem quantity']
        item_qty = int(item_qty_str) if item_qty_str else 0
        item_price_str = row['Lineitem price']
        item_price = float(item_price_str) if item_price_str else 0.0
        item = row['Lineitem name']

        if (is_fortnightly_coffee(item)
             and prev_order['Lineitems'].apply(func=is_fortnightly_coffee).any()
            ):
            # don't add fornightly coffee if they had it in their last order
            pass
        else:
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
    values_to_sync = []
    temp_html_dir = WORKING_DIRECTORY + "order_htmls/"

    # delete any old contents before using
    delete_dir(temp_html_dir) 

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
        values_to_sync += [(
                            orderID, 
                            order.email,
                            order.delivery_date,
                            lineitems
                        )]
        
        # build and save packing slip for the order
        html_template = build_order_packing_slip(order, template)
        save_html_file(html_template, temp_html_dir, str(orderID)+".html")

    all_html_files = ([temp_html_dir + f for f in os.listdir(temp_html_dir)
                      if f.lower().endswith('.html')])
    
    file_output_format = DEFAULT_OUTPUT_LOCATION + "{name}_{date}.{ext}"

    pdf_out_loc = file_output_format.format(name="PackingSlips", date=delivery_date.strftime("%Y%m%d"), ext="pdf")
    csv_out_loc = file_output_format.format(name="RequiredStock", date=delivery_date.strftime("%Y%m%d"), ext="csv")
    render_html_files_to_pdf(all_html_files, pdf_out_loc)

    # delete any contents in working directory after use
    delete_dir(temp_html_dir) 

    write_items_to_csv(["Lineitem", "Quantity"], total_items, csv_out_loc)

    # sync values to db table
    table = CompressedOrderHistory()
    DB.sync_table(table.name, table.columns.keys(), values_to_sync, db_conn)

    return total_items
    #==========================================================================


def delete_dir(dirname):
    """
    Deletes a directory and all it's contents
    """
    if os.path.exists(dirname):
        shutil.rmtree(dirname)

def write_items_to_csv(columns, items, outfile):

    with open(outfile, 'w', newline='') as csv_file:  
        writer = csv.writer(csv_file)
        writer.writerow([columns[0], columns[1]])
        for key, value in items.items():
            writer.writerow([key, value])


def render_html_files_to_pdf(infiles, outfile):
    """
    Renders a list of html files to pdf

    :param infiles:     (list) of html filepaths to render
    :param outfile:     (str) filepath of pdf output
    """
    
    config = pdfkit.configuration(wkhtmltopdf=PATH_WKHTMLTOPDF)
    pdfkit.from_file(infiles, outfile, configuration=config)


def save_html_file(string_to_save, basepath, filename):
    """
    Checks if directory exists before saving a file and creates

    :param string_to_save:  (str) string to save to file
    :param basepath:        (str) base path of the file
    :param filename:        (str) filename
    """

    # create dir if it doesn't already exist 
    if not os.path.exists(basepath):
        os.makedirs(basepath)

    filepath = basepath + filename

    with open(filepath, 'w') as html_file:
        html_file.write(string_to_save)


def build_order_packing_slip(order, html_template):
    """
    Builds a packing slip for an input order and html template

    :param order:           (Order) object
    :param html_template:   (str) formattable string of html template
    """

    item_context = '''
    <div class="flex-line-item">
    <div class="flex-line-item-description">
    <p>
    <span class="line-item-description-line">
    {lineitem}
    </span>
    </p>
    </div>
    <div class="flex-line-item-quantity">
    <p class="text-align-right">
    {lineitem_qty}
    </p>
    </div>
    </div>
    '''

    item_context_strong = '''
    <div class="flex-line-item">
    <div class="flex-line-item-description">
    <p>
    <span class="line-item-description-line">
    <strong>{lineitem}</strong>
    </span>
    </p>
    </div>
    <div class="flex-line-item-quantity">
    <p class="text-align-right">
    <strong>{lineitem_qty}</strong>
    </p>
    </div>
    </div>
    '''

    item_str = ""

    for item in order.lineitems:
        qty = order.lineitems[item]['quantity']

        if qty > 1:
            item_str += item_context_strong.format(lineitem=item, lineitem_qty=qty)
        else:
            item_str += item_context.format(lineitem=item, lineitem_qty=qty)

    return html_template.format(
                orderID=order.ID,
                delivery_date=order.delivery_date.date(),
                shipping_address=order.shipping_info,
                billing_address=order.billing_info,
                lineitems=item_str,
                shop_name="Butter & Crust",
                shop_address_address1="70 Woodwarde Road",
                shop_address_city="London",
                shop_address_zip="SE22 8UL",
                shop_address_country="United Kingdom",
                shop_email="support@butterandcrust.com",
                shop_domain="butterandcrust.com"
    )

if __name__ == "__main__":
    main()
