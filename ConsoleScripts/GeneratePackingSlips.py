import datetime as dt
import os
import argparse
import pandas as pd

from lib.PackageConfig import *
import lib.DB.DB_queries as DB
from lib.templates.main.StandardHTMLTemplate import template as html_template
from lib.Order import Order
import lib.General.FileQueries as file_queries
import lib.General.Exceptions as e

def main():
    parser = argparse.ArgumentParser(description="Produce B&C packing slips")
    parser.add_argument("-date", help="delivery date of orders YYYY/mm/dd", type=str, required=True)
    parser.add_argument("-file", help="file containing route order information", type=str, required=False)
    args = parser.parse_args()

    OrdersDB = DB.create_connection(ORDERS_DB_LOC)

    delivery_date = dt.datetime.strptime(args.date, "%Y/%m/%d")
    outfile = DEFAULT_OUTPUT_LOCATION + "PackingSlips_{date}.pdf".format(date=delivery_date.strftime("%Y%m%d"))
    produce_packing_slips(delivery_date, args.file, outfile, OrdersDB)

def produce_packing_slips(delivery_date, route_order_file, output_file, conn):
    """
    Produces the packing slips for a given delivery date and route 
    orders.

    :param delivery_date:           (datetime) date of delivery
    :param route_order_file:        (csv) file containing information 
                                    about the order deliveries are made
                                    required columns: ['Bike', 
                                                       'Route',
                                                       'Stop on Route'
                                                      ]
    :param output_file:             (str) location to save packing slips
    :param conn:                    (sqlite connection object)
    """

    route_orders = pd.read_csv(route_order_file, na_filter=False)

    # A temp working directory to store single html files
    temp_html_dir = WORKING_DIRECTORY + "order_htmls/"

    # delete any old contents before using
    file_queries.delete_dir(temp_html_dir) 

    try: 
        fdate = delivery_date + dt.timedelta(days=1)
        orders = DB.select_all_by_delivery_date("CompressedOrderHistory",
                                                delivery_date, fdate, conn)

        for _, ordr in orders.iterrows():
            
            order = Order(int(ordr['ID']), ordr['Email'])
            order.shipping_info = ordr['ShippingAddress']
            order.billing_info = ordr['BillingAddress']
            order.delivery_date = dt.datetime.strptime(ordr['DeliveryDate'], "%Y-%m-%d")
            order.total = ordr['Total']
            order.notes = ordr['DeliveryNotes']

            for item in ordr['Lineitems'].split("|"):
                order.add_lineitem(item, 0.0, 1)

            route_order = route_orders.loc[route_orders['Order_Number'] == order.ID]

            if len(route_order.index) == 0:
                e.throw_warning('''
                There are no rows for order #{orderid} in {filename}
                '''.format(orderid=order.ID, filename=route_order_file)
                )
                
                order_filename = str(order.ID) + ".html"
            else:
                if len(route_order.index) > 1:
                    e.throw_warning(
                    '''
                    There are {num} rows for order #{orderid} in {filename}\n. 
                    Expected only 1 row per order.\n
                    If continue we will use the first order only.\n
                    '''.format(num=len(route_order.index),
                                orderid=order.ID,
                                filename=route_order_file)
                    )

                route_order = route_orders.loc[route_orders['Order_Number'] == order.ID].iloc[0]

                order.bike_name = route_order['Bike']
                order.route_name = route_order['Route']
                raw_stop_number = route_order['Stop on Route']
            
                order.stop_on_route = str(raw_stop_number) if raw_stop_number > 9 else "0" + str(raw_stop_number)

                order_filename = order.route_name + "_" + order.stop_on_route + ".html"
                order_filename = order_filename.replace(" ", "_")
                order_filename = order_filename.replace("/", "of")

            if not order_filename or order_filename.isspace():
                order_filename = str(order.ID) + ".html"

            order_html = build_order_packing_slip(order, html_template)          

            file_queries.save_file(order_html, temp_html_dir, order_filename)

        all_html_files = ([temp_html_dir + f for f in os.listdir(temp_html_dir)
                        if f.lower().endswith('.html')])
        
        all_html_files.sort()

        file_queries.render_html_files_to_pdf(all_html_files, output_file, PATH_WKHTMLTOPDF)

    except:
        # delete any contents in working directory if we hit an error
        file_queries.delete_dir(temp_html_dir)
        raise

    # delete any contents in working directory after use
    file_queries.delete_dir(temp_html_dir) 

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
                ordernotes=order.notes,
                shop_name="Butter & Crust",
                shop_email="support@butterandcrust.com",
                shop_domain="butterandcrust.com",
                bikename=order.bike_name,
                stopnumber=order.stop_on_route,
                routename=order.route_name
    )

if __name__ == "__main__":
    main()