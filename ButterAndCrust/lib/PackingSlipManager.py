from django.utils.crypto import get_random_string
import shutil
import os
import pandas as pd 
import datetime as dt
import pdfkit

from ButterAndCrust.lib.General.WorkingDirectoryManager import WorkingDirectoryManager
import ButterAndCrust.lib.General.Exceptions as e
from ButterAndCrust.lib.Order import Order
import ButterAndCrust.lib.General.FileQueries as FQ
from ButterAndCrust.lib.DB.Tables.CompressedOrderHistory import CompressedOrderHistory

class PackingSlipManager():
    """
    A class that safely managers and builds packing slips in the 
    order deliveries are made.

    
    :param output_file:         (str) full filepath to save the full 
                                pdf of the packingslips
    :param working_dir:         (str) a temporary working directory. 
                                Ensure this is a safe location to be 
                                deleted
    :param template:            (str) The html template of the packing slip
    :param wkhtml_exe_path:     (str) file path to the wkhtml executable
    """

    def __init__(self, output_file, working_dir, template, wkhtml_exe_path):
        self.working_directory = WorkingDirectoryManager(working_dir)
        self.outfile = output_file
        self.html_template = template
        self.wkhtml_exe_path = wkhtml_exe_path

    def produce_packing_slips(self, delivery_date, route_order_file, db_file):
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
        :param conn:                    (sqlite connection object)
        """

        route_orders = pd.read_csv(route_order_file, na_filter=False)

        order_table = CompressedOrderHistory(db_file)

        # delete any old contents before using working directory
        self.working_directory.clear_working_dir()
        working_dir = self.working_directory.path

        fdate = delivery_date + dt.timedelta(days=1)
        idate = delivery_date
        orders = order_table.select_by_delivery_date(idate, fdate)

        for _, ordr in orders.iterrows():
            
            # use order class to hold necessary info
            order = Order(int(ordr['ID']), ordr['Email'])
            order.shipping_info = ordr['ShippingAddress']
            order.billing_info = ordr['BillingAddress']
            order.total = ordr['Total']
            order.notes = ordr['DeliveryNotes']            
            order.delivery_date = dt.datetime.strptime(ordr['DeliveryDate'],
                                                       "%Y-%m-%d")

            # store line items with price as 0.0 as price irrelevant here
            for item in ordr['Lineitems'].split("|"):
                order.add_lineitem(item, 0.0, 1)

            # get the route order info for this orderID
            route_order = route_orders.loc[route_orders['Order_Number'] == order.ID]

            # check that only one row per orderID exists in route order file
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
                    '''.format(
                        num=len(route_order.index),
                        orderid=order.ID,
                        filename=route_order_file
                        )
                    )

                route_order = route_orders.loc[route_orders['Order_Number'] == order.ID].iloc[0]

                order.bike_name = route_order['Bike']
                order.route_name = route_order['Route']
                stop_on_route = route_order['Stop on Route']

                # safely process stop numbers
                try:
                    raw_stop_number = int(stop_on_route)
                except:
                    e.throw_warning(
                    '''
                    Cannot understand Stop on Route: {route_order}, for
                    order #{orderid}. If continiure, will use Stop on
                    Route: 1
                    '''.format(
                            route_order=stop_on_route,
                            orderid=order.ID
                        )
                    )
                    raw_stop_number = "00"
            
                # create an order filename that will be sortable in the 
                # order of deliveries
                order.stop_on_route = str(raw_stop_number) if raw_stop_number > 9 else "0" + str(raw_stop_number)
                order_filename = order.route_name + "_" + order.stop_on_route + ".html"
                order_filename = order_filename.replace(" ", "_")
                order_filename = order_filename.replace("/", "of")
            
            # if something has gone wrong and order filename is still
            # blank just name it orderID
            if not order_filename or order_filename.isspace():
                order_filename = str(order.ID) + ".html"

            # generate html of the packing slip for each order
            order_html = self.build_order_packing_slip(order, self.html_template)          

            FQ.save_file(
                        order_html,
                        working_dir,
                        order_filename
                    )

        # create a list of all html files we have generated
        all_html_files = ([working_dir + f for f in os.listdir(working_dir)
                           if f.lower().endswith('.html')])
        
        # sort filenames so they are rendered in delivery order
        all_html_files.sort()

        self.render_html_files_to_pdf(all_html_files, self.outfile)

        # delete contents once finished with them
        self.working_directory.clear_working_dir()

    def build_order_packing_slip(self, order, html_template):
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
    

    def render_html_files_to_pdf(self, infiles, outfile):
        """
        Renders a list of html files to pdf

        :param infiles:                 (list) of html filepaths to render
        :param outfile:                 (str) filepath of pdf output
        """

        config = pdfkit.configuration(wkhtmltopdf=self.wkhtml_exe_path)
        pdfkit.from_file(infiles, outfile, configuration=config)
