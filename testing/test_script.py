import pandas as pd
import csv

from lib.Address import Address
import lib.DB.DB_queries as DB
from lib.PackageConfig import ORDERS_DB_LOC
from lib.DB.TableSchemas.CompressedOrderHistory import CompressedOrderHistory

all_orders = pd.read_csv("C:/Users/dylan/Documents/test/CompressedOrderHistory_new.csv", na_filter=False)

# with open("C:/Users/dylan/Documents/test/test.csv", 'w', encoding="utf-8", newline='') as csv_file:
#     writer = csv.writer(csv_file)
#     for i, row in all_orders.iterrows():
#         orderID = int(row['Name'][1:])

#         billing_info = Address(
#                                     row['Billing Name'],
#                                     row['Billing Street'],
#                                     row['Billing Address1'],
#                                     row['Billing Address2'],
#                                     row['Billing Company'],
#                                     row['Billing City'],
#                                     row['Billing Zip'],
#                                     row['Billing Province'],
#                                     row['Billing Country'],
#                                     row['Billing Phone']
#                                 )

#         shipping_info = Address(
#                                 row['Shipping Name'],
#                                 row['Shipping Street'],
#                                 row['Shipping Address1'],
#                                 row['Shipping Address2'],
#                sql                 row['Shipping Company'],
#                                 row['Shipping City'],
#                                 row['Shipping Zip'],
#                                 row['Shipping Province'],
#                                 row['Shipping Country'],
#                                 row['Shipping Phone']
#                             )
#         writer.writerow([orderID, billing_info, shipping_info])


columns = ['ID', 'Email', 'DeliveryDate', 'Lineitems', 'BillingAddress', 'ShippingAddress', 'Total']
values = []
conn = DB.create_connection(ORDERS_DB_LOC)

for i, row in all_orders.iterrows():
    print(row['BillingAddress'])
    values += [(
        row['ID'],
        row['Email'],
        row['DeliveryDate'],
        row['Lineitems'],
        row['BillingAddress'].replace(",", ",<br>"),
        row['ShippingAddress'].replace(",", ",<br>"),
        row['Total']
    )]

DB.sync_table("CompressedOrderHistory", columns, values, conn)