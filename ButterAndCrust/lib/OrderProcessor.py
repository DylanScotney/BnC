import datetime as dt
import pandas as pd

import ButterAndCrust.lib.General.Exceptions as e
from ButterAndCrust.lib.DB.Tables.CompressedOrderHistory import CompressedOrderHistory
from ButterAndCrust.lib.items.OrderItems import Lineitems
import ButterAndCrust.lib.General.FileQueries as FQ
from ButterAndCrust.lib.Order import Order
from ButterAndCrust.lib.Address import Address

class OrderProcessor():
    """
    OrderProcessor class that will compress input orders and 
    store to a given table. 

    Also accounts for logic such as fortnighly coffee subscriptions
    """

    def __init__(self, input_file, delivery_date, table):
        """
        Instantiates a new instance of the OrderProcessor class

        Args:
            intput_file(``str``): filepath of the raw orders csv
            out_file(``str``): filepath of the output location
            delivery_date(``datetime``): delivery date of input orders
            table(``CompressedOrderHistory``): table to store orders

        """

        self.infile = input_file
        self.delivery_date = self._check_input_date(delivery_date)

        if isinstance(table, CompressedOrderHistory):
            self.orders_table = table
        else: 
            err = "Input table is not an instance of CompressedOrderHistory"
            raise TypeError(err)

        self._testing = False # private member for testing
    
    def _check_input_date(self, date):
        """
        Warns user if the input date is a Saturday and asks if would like to
        continue.

        Args:
            datestr(``str``): date formatted YYYY/mm/dd
        """
        date = dt.datetime.strptime(date, "%Y/%m/%d")

        if date.weekday() != 5:
            if not self._testing:
                e.throw_warning("Input delivery date is not a Saturday.")

        return date

    def _is_fortnightly_coffee(self, text):
        """
        Determines whether an item string is fornightly coffee lineitem

        Args:
            text(``str``): text to check
        """
        item = text.lower()
        return ("coffee" in item
                and ("every fortnight" in item
                or "every other week" in item)
                )

    
    def _check_last_delivery(self):
        """
        Checks if the last processed delivery date was more than a week ago 
        and warns if true
        """
        last_delivery_date = dt.datetime.strptime(self.orders_table.max("DeliveryDate"), "%Y-%m-%d")

        if last_delivery_date is None:
            err = "No deliveries have been processed for last Saturday."
            if not self._testing:
                e.throw_warning(err)
        else:
            diff = self.delivery_date - last_delivery_date

            if diff.days > 7:
                err = "No deliveries have been processed for last Saturday."
                if not self._testing:
                    e.throw_warning(err)

            if diff.days < 0:
                err = "Non chronological delivery dates."
                if not self._testing:
                    e.throw_warning(err)

    def process_orders(self, outfile):
        """
        Processes the orders:
            - compresses and syncs orders to self.orders_table
            - saves stock requirements to outfile

        Args:
            outfile(``str``): filepath of the output stock requirements
        """
        
        # before we process orders check the chronology of the previous ones
        self._check_last_delivery()

        orders = dict()
        total_items = dict()
        input_orders = pd.read_csv(self.infile, na_filter=False)
        prev_orders = self.orders_table.get_most_recent_order_by_email(self.delivery_date)

        # Process orders into a list of Order() objects so they're managable
        #==========================================================================
        for _, row in input_orders.iterrows():

            orderID = int(row['Name'][1:])

            # create a new Order() if this is a new orderID
            if orderID not in orders:
                orders[orderID] = Order(orderID, row['Email'])

            # get customers previous order if there is any
            prev_order = prev_orders[prev_orders['Email'].str.contains(orders[orderID].email)]

            orders[orderID].delivery_date = self.delivery_date

            if row['Total'] and not row['Total'].isspace():
                orders[orderID].update_total(float(row['Total']))

            if row['Notes'] and not row['Notes'].isspace():
                orders[orderID].notes = row['Notes']
            
            item_qty_str = row['Lineitem quantity']
            item_qty = int(item_qty_str) if item_qty_str else 0
            item_price_str = row['Lineitem price']
            item_price = float(item_price_str) if item_price_str else 0.0
            item = Lineitems.get(row['Lineitem name'])

            if not (self._is_fortnightly_coffee(item.description)
                and prev_order['Lineitems'].apply(func=self._is_fortnightly_coffee).any()
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
            
        FQ.write_dict_to_csv(["Lineitem", "Quantity"], total_items, outfile)

        # sync values to db table
        self.orders_table.sync(compressed_rows, ["ID"])

        return total_items
        #==========================================================================
    
    
    
