import datetime as dt
import os
import argparse

from lib.PackageConfig import *
import lib.DB.DB_queries as DB
from lib.templates.main.StandardHTMLTemplate import template as html_template
from lib.Order import Order
import lib.General.FileQueries as file_queries
import lib.General.Exceptions as e

def main():
    parser = argparse.ArgumentParser(description="Produce B&C packing slips")
    parser.add_argument("-date", help="delivery date of orders YYYY/mm/dd", type=str, required=True)
    args = parser.parse_args()

    OrdersDB = DB.create_connection(ORDERS_DB_LOC)

    delivery_date = dt.datetime.strptime(args.date, "%Y/%m/%d")
    outfile = DEFAULT_OUTPUT_LOCATION + "PackingSlips{date}.pdf".format(date=delivery_date.strftime("%Y%m%d"))
    produce_packing_slips(delivery_date, outfile, OrdersDB)

def produce_packing_slips(delivery_date, output_file, conn):

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

            for item in ordr['Lineitems'].split("|"):
                order.add_lineitem(item, 0.0, 1)
            
            order_html = build_order_packing_slip(order, html_template)
            file_queries.save_file(order_html, temp_html_dir, str(order.ID) + ".html")

        all_html_files = ([temp_html_dir + f for f in os.listdir(temp_html_dir)
                        if f.lower().endswith('.html')])

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
                shop_name="Butter & Crust",
                shop_email="support@butterandcrust.com",
                shop_domain="butterandcrust.com"
    )

if __name__ == "__main__":
    main()