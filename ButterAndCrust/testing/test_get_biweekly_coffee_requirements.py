import datetime as dt

import ButterAndCrust.lib.DB.DB_queries as DB
import ButterAndCrust.lib.PackageConfig as config 

conn = DB.create_connection(config.ORDERS_DB_LOC)

testdate = dt.datetime(2021, 1, 16)
enddate = testdate + dt.timedelta(days=1)

orders = DB.select_all_by_delivery_date("CompressedOrderHistory", testdate, testdate, conn)

print(orders)

orders.to_csv("C:/Users/dylan/Documents/test/20210116_orders.csv")
