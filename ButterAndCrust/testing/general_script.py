import pandas as pd
import csv
import datetime as dt

from ButterAndCrust.lib.Address import Address
import ButterAndCrust.lib.DB.DB_queries as DB
from ButterAndCrust.lib.PackageConfig import ORDERS_DB_LOC, WORKING_DIRECTORY, PATH_WKHTMLTOPDF
from ButterAndCrust.lib.PackingSlipManager import PackingSlipManager
from ButterAndCrust.lib.templates.main.StandardHTMLTemplate import template
from ButterAndCrust.lib.General.WorkingDirectoryManager import WorkingDirectoryManager


    



manager = PackingSlipManager("C:\\temp\\PackingSlipTests.pdf", WORKING_DIRECTORY, template, PATH_WKHTMLTOPDF)

manager.produce_packing_slips(dt.datetime(2021, 2, 6), "C:\\Users\\dylan\\Documents\\Programming\\ButterAndCrust\\DB\\test_routes.csv", ORDERS_DB_LOC)

