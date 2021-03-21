import argparse
import datetime as dt

import ButterAndCrust.lib.PackageConfig as PC
from ButterAndCrust.lib.OrderProcessor import OrderProcessor
from ButterAndCrust.lib.DB.Tables.CompressedOrderHistory import airCompressedOrderHistory, sqlCompressedOrderHistory

def main():
    delivery_date = "2021/01/23"
    filepath = "C:/Users/dylan/Documents/Programming/ButterAndCrust/ButterAndCrust/tests/mockdata/orders_20210123.csv"

    base_key = "appWCrLerVduIq5SR"
    api_key = "keyQNWjWomXyaBGJK"
    table = airCompressedOrderHistory(base_key, api_key)

    processor = OrderProcessor(filepath, delivery_date, table)
    outfile = "C:/temp/outfile.csv"

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

    actual_items = processor.process_orders(outfile)

    print(actual_items)


if __name__ == "__main__":
    main()