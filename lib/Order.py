from Address import Address
from datetime import datetime as dt
import pandas as pd
from datetime import timedelta

class Order():
    """
        Default order class
    """
    def __init__(self, ID, email):
        self.ID = ID
        self.email = email

        # declare empty/default members on init  
        self.total = 0.0
        self.subtotal = 0.0
        self.shipping_fee = 0.0
        self.taxes = 0.0
        self.payment_date = None
        self.delivery_date = None
        self.shipping_info = Address()
        self.billing_info = Address()
        self.lineitems = dict()
        self.ccy = ""
        self.financial_status = ""
        self.fulfillment_status = ""
        self.fulfillment_date = None
        self.accepts_marketing = ""
        self.discount_code = ""
        self.discount_amount = 0.0
        self.shipping_method = ""
        self.creation_date = None
        self.notes = ""
        self.note_attributes = ""
        self.cancellation_date = None
        self.payment_method = ""
        self.payment_reference = ""
        self.refunded_amount = 0.0
        self.vendor = ""
        self.tags = ""
        self.risk_level = ""
        self.source = ""
        self.phone = ""
        self.receipt_number = ""

    def add_payment_date(self, date):
        self.payment_date = date

    def __calculate_delivery_date(self, cutoff=1, weekday=5):
        """
        Calculates delivery date depending on the payment date

        @weekday:   Weekday as an integer between 0 (Mon) and 6 (Sun)
        @cutoff:    Latest day a payment can be made in order to be
                    be delivered on the same week
        """
        d = self.payment_date
        t = timedelta((7 + weekday - d.weekday()) % 7)
        t_extra = timedelta(7) if d.weekday() > cutoff else timedelta(0)
        self.delivery_date = d + t + t_extra

    def add_lineitem(self, item, price, qty):
        """
        Stores line items with price and quantity in dictionary
        """
        if item not in self.lineitems:
            self.lineitems[item] = {'quantity' : qty, 'price per unit' : price}
        else: 
            self.lineitems[item]['quantity'] += qty

    def update_total(self, amount):
        self.total += amount
    
    def update_subtotal(self, amount):
        self.subtotal += amount

    def add_billing_info(self, address):
        """
        Safely adds billing info dealing with potential empty lines in
        order csv.

        @address:      Address class
        """

        if address.name and not address.name.isspace():
            self.billing_info.name = address.name

        if address.street and not address.street.isspace():
            self.billing_info.street = address.street

        if address.address1 and not address.address1.isspace():
            self.billing_info.address1 = address.address1

        if address.address2 and not address.address2.isspace():
            self.billing_info.address2 = address.address2

        if address.company and not address.company.isspace():
            self.billing_info.company = address.company
        
        if address.city and not address.city.isspace():
            self.billing_info.city = address.city

        if address.zip and not address.zip.isspace():
            self.billing_info.zip = address.zip

        if address.province and not address.province.isspace():
            self.billing_info.province = address.province
        
        if address.country and not address.country.isspace():
            self.billing_info.country = address.country

        if address.phone and not address.phone.isspace():
            self.billing_info.phone = address.phone

    def add_shipping_info(self, address):
        """
        Safely adds shipping info dealing with potential empty lines in
        order csv.

        @address:      Address class
        """

        if address.name and not address.name.isspace():
            self.shipping_info.name = address.name

        if address.street and not address.street.isspace():
            self.shipping_info.street = address.street

        if address.address1 and not address.address1.isspace():
            self.shipping_info.address1 = address.address1

        if address.address2 and not address.address2.isspace():
            self.shipping_info.address2 = address.address2

        if address.company and not address.company.isspace():
            self.shipping_info.company = address.company
        
        if address.city and not address.city.isspace():
            self.shipping_info.city = address.city

        if address.zip and not address.zip.isspace():
            self.shipping_info.zip = address.zip

        if address.province and not address.province.isspace():
            self.shipping_info.province = address.province
        
        if address.country and not address.country.isspace():
            self.shipping_info.country = address.country

        if address.phone and not address.phone.isspace():
            self.shipping_info.phone = address.phone

    def __repr__(self):
        return "Order()"

    def __str__(self):
        
        items_str = ""

        for item in self.lineitems:
            s = str(self.lineitems[item]['quantity']) + "x\t" + item + "\n"
            items_str += s

        return (
            "Order Summary\n\n"
            "{shipping_info}\n\n"
            + "Payment date: {paymentdate}\n"
            + "Delivery date: {deliverydate}\n\n"
            + "Items:\n{items}\n"
            + "Total: £{total}"
        ).format(
            paymentdate = self.payment_date.strftime('%Y-%m-%d'),
            deliverydate = self.delivery_date.strftime('%Y-%m-%d'),
            shipping_info = self.shipping_info,
            items = items_str,
            total = self.total
        )
        