import sqlite3
import pandas as pd

import ButterAndCrust.lib.DB.DB_queries as DB

DB_BASE_PATH = "c:/Users/dylan/Documents/Programming/ButterAndCrust/DB/"
ORDERS_DB_NAME = "OrderHistory"
ORDERS_DB_LOC = DB_BASE_PATH + ORDERS_DB_NAME + ".db"

conn = DB.create_connection(ORDERS_DB_LOC)

sql = '''ALTER TABLE CompressedOrderHistory
        ADD COLUMN DeliveryNotes TEXT DEFAULT '' NOT NULL;'''

cur = conn.cursor()

cur.execute(sql)
conn.commit()
cur.close()