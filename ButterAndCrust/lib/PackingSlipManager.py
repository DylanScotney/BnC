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
from ButterAndCrust.lib.items.OrderItems import Lineitems

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
        self.working_directory = working_dir
        self.outfile = output_file
        self.html_template = template
        self.wkhtml_exe_path = wkhtml_exe_path

    def _chunk(self, iterable, chunk_size):
        """Break iterable into chunks."""
        for i in range(0, len(iterable), chunk_size):
            yield iterable[i : i + chunk_size]

    def produce_packing_slips(self, delivery_date, route_order_file, order_table):
        """
        Produces the packing slips for a given delivery date and route 
        orders. Whilst safely handling the WorkingDirectory

        Args:
            delivery_date(``datetime``): date of delivery
            route_order_file(``str``, csv): file containing information 
                about the order deliveries are made. Required columns: 
                ['Bike', 'Route', 'Stop on Route']
            db_file(``str``, db file) filepath to db
 
        """

        with WorkingDirectoryManager(self.working_directory) as working_dir:

            self._produce_packing_slips(delivery_date, route_order_file,
                                        working_dir, order_table)

    def _produce_packing_slips(self, delivery_date, route_order_file, working_dir, order_table):
        """
        Produces the packing slips for a given delivery date and route 
        orders.

        Args:
            delivery_date(``datetime``): date of delivery
            route_order_file(``str``, csv): file containing information 
                about the order deliveries are made. Required columns: 
                ['Bike', 'Route', 'Stop on Route']
            working_dir(``WorkingDirectorManager``) working directory 
                encapsulated by the working directory manager
            db_file(``str``, db file) filepath to db
        """

        route_orders = pd.read_csv(route_order_file, na_filter=False)

        # delete any old contents before using working directory
        working_dir.clear_working_dir()

        fdate = delivery_date + dt.timedelta(days=1)
        idate = delivery_date
        orders = order_table.get_all_by_delivery_date(idate, fdate)

        for _, ordr in orders.iterrows():
            
            # use order class to hold necessary info
            order = Order(int(ordr['ID']), ordr['Email'])
            order.shipping_info = ordr['ShippingAddress']
            order.billing_info = ordr['BillingAddress']
            order.total = ordr['Total']
            order.notes = ordr['DeliveryNotes']            
            order.delivery_date = ordr['DeliveryDate']

            # store line items with price as 0.0 as price irrelevant here
            for item_desc in ordr['Lineitems'].split("|"):
                item = Lineitems.get(item_desc)
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

                route_order = route_orders.loc[route_orders['Tracking_ID'] == order.ID].iloc[0]

                order.route_name = route_order['Rider']
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
                        working_dir.path,
                        order_filename
                    )

        # create a list of all html files we have generated
        all_html_files = ([working_dir.path + f for f in os.listdir(working_dir.path)
                           if f.lower().endswith('.html')])
        
        # sort filenames so they are rendered in delivery order
        all_html_files.sort()

        for i, file_chunk in enumerate(self._chunk(all_html_files, 100)):
            self.render_html_files_to_pdf(file_chunk, self.outfile + "_{num}.pdf".format(num=i))

        # delete contents once finished with them
        working_dir.clear_working_dir()

    def build_order_packing_slip(self, order, html_template):
        """
        Builds a packing slip for an input order and html template

        :param order:           (Order) object
        :param html_template:   (str) formattable string of html template
        """

        # images
        # <div class="flex-line-item-img">
        # <div class="aspect-ratio aspect-ratio-square" style="width: 58px; height: 58px;">
        # <img src="{lineitem_image}" style="width: 58px; height: 58px;">
        # </div>
        # </div>

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

        item_str = ""

        for desc in order.lineitems:
            item = order.lineitems[desc]['item']
            qty = order.lineitems[desc]['quantity']
            item_desc = item.friendly_desc if qty == 1 else "<strong><u>" + item.friendly_desc + "</u></strong>"
            qty_str = str(qty) if qty == 1 else "<strong><u>" + str(qty) + "</u></strong>"

            item_str += item_context.format(
                                            # lineitem_image=item.img,
                                            lineitem=item_desc,
                                            lineitem_qty=qty_str,
                                        )

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
