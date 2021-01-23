from datetime import datetime as dt
import pandas as pd
from .Order import Order
from .Address import Address
from .DB.credentials import ORDERS_DB_LOC
from .DB import DB_queries as DB
from .DB.TableSchemas.CompressedOrderHistory import CompressedOrderHistory
import sqlite3
import argparse

# The first delivery date for fornightly coffe
INITIAL_COFFEE_DATE = dt(2020, 1, 9)

def main():
    parser = argparse.ArgumentParser(description="Process B&C Weekly Orders")
    # parser.add_argument("-file", help="location of weekly orders csv file", type=str, required=True)
    parser.add_argument("-date", help="delivery date of input orders YYYY/mm/dd", type=str, required=True)
    args = parser.parse_args()

    argsfile = "C:/Users/dylan/Documents/Programming/ButterAndCrust/DB/OpenOrders_20210109.csv"
    input_delivery_date = check_input_date(args.date)
    input_file = argsfile
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
    
    df = pd.read_csv(file_path, na_filter=False)
    
    input_delivery_date = delivery_date
    orders = dict()

    prev_orders = DB.get_most_recent_order_by_email(input_delivery_date, db_conn)

    for _, row in df.iterrows():

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

        if is_fortnightly_coffee(item):
                orders[orderID].receive_fortnightly_coffee = True

        # if they recieved it in their previous orders then they don't this time
        if prev_order['ReceivedFortnightlyCoffee'].any():
            orders[orderID].receive_fortnightly_coffee = False

        if (is_fortnightly_coffee(item)
            and not orders[orderID].receive_fortnightly_coffee
            ):
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

    sync_orders_to_DB(orders, db_conn)


def sync_orders_to_DB(orders, db_conn):
    """
    Synchronises orders to the CompressedOrderHistory table on the 
    OrdersDB

    :param orders:          (list of Orders())
    :param db_conn:         (sqlite connection object)
    """

    values_to_sync = []

    for orderID in orders:

        order = orders[orderID]      

        lineitems = ""

        for item in order.lineitems:
            for _ in range(order.lineitems[item]['quantity']):
                lineitems += item + "|"

        lineitems = lineitems[:-1]
        values_to_sync += [(orderID, order.email, order.delivery_date, lineitems, order.receive_fortnightly_coffee)]
    
    # sync values to db table
    table = CompressedOrderHistory()
    DB.sync_table(table.name, table.columns.keys(), values_to_sync, db_conn)


if __name__ == "__main__":
    main()
