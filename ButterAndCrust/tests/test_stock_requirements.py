import pandas as pd
import datetime as dt
import os

from ConsoleScripts.OrderProcessor import proccess_orders
import lib.DB.DB_queries as DB
from lib.PackageConfig import ORDERS_DB_LOC, WORKING_DIRECTORY

def test_stock_requirements():

    delivery_date = dt.datetime(2021, 1, 23)
    conn = DB.create_connection(ORDERS_DB_LOC)
    filepath = os.path.dirname(__file__) + "/mockdata/orders_20210123.csv"

    expected_items = {
        "Extra Loaf":	15,
        "Sweet Morning Treats" :	89,
        "Butter & Crust Subscription (Loaf Included)" :	134,
        "Granola" : 28,
        "Townsend Farm Apple Juice 750ml" : 33,
        "Cultured Butter 250g" : 57,
        "Preserves 125g" : 62,
        "Monmouth Coffee. - Our Pick / Wholebean / 250g per week" : 8,
        "Monmouth Coffee. - Our Pick / Medium (Filter/Aeropress) / 250g every other week" : 1,
        "Monmouth Coffee. - Espresso / Wholebean / 250g per week" : 3,
        "Four Week Gift Subscription" : 2,
        "Monmouth Coffee. - Classic / Fine (Espresso/Moka Pot) / 250g per week" : 2,
        "Monmouth Coffee. - Classic / Wholebean / 250g every other week" : 2,
        "Monmouth Coffee. - Classic / Medium (Filter/Aeropress) / 250g every other week" : 1,
        "Monmouth Coffee. - Our Pick / Coarse (French Press) / 250g per week" : 6,
        "Monmouth Coffee. - Our Pick / Fine (Espresso/Moka Pot) / 250g every other week" : 1,
        "Monmouth Coffee. - Classic / Medium (Filter/Aeropress) / 250g per week" : 1,
        "Monmouth Coffee. - Espresso / Wholebean / 250g every other week" : 1,
        "Monmouth Coffee. - Classic / Coarse (French Press) / 250g per week" : 2,
        "Monmouth Coffee. - Classic / Coarse (French Press) / 250g every other week" : 1,
        "Monmouth Coffee. - Our Pick / Wholebean / 250g every other week" : 1,
        "Monmouth Coffee. - Espresso / Fine (Espresso/Moka Pot) / 250g every other week" : 1,
        "Monmouth Coffee. - Our Pick / Medium (Filter/Aeropress) / 250g per week" : 1,
        "Eight Week Gift Subscription" : 1,
        "Monmouth Coffee. - Our Pick / Coarse (French Press) / 250g every other week" : 1,
        "Monmouth Coffee. - Classic / Wholebean / 250g per week" : 1
    }

    actual_items = proccess_orders(filepath, delivery_date, conn)

    dict_compare(actual_items, expected_items)


def dict_compare(expected_dict, actual_dict):

    for key in expected_dict:
        print("\n\nItem: ", key,
              "\nExpected quantity: ", expected_dict[key],
              "\nActual quantity: ", actual_dict[key])
        assert key in actual_dict
        assert expected_dict[key] == actual_dict[key]
        
    
