import os
import posixpath

import ButterAndCrust
import ButterAndCrust.images

# Location of DB
DB_BASE_PATH = "C:/Users/dylan/Documents/Programming/ButterAndCrust/DB/"
ORDERS_DB_NAME = "OrderHistory"
ORDERS_DB_LOC = DB_BASE_PATH + ORDERS_DB_NAME + ".db"

# Must install [https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.4/wkhtmltox-0.12.4_msvc2015-win64.exe]
PATH_WKHTMLTOPDF = "C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe"

# Default output location for package slips and stock requirements 
# this can also be changed on the command line
DEFAULT_OUTPUT_LOCATION = "C:/Users/dylan/Documents/test/"

# A temporary working directory that will store files
WORKING_DIRECTORY = posixpath.join(os.path.dirname(ButterAndCrust.__file__), "WorkingDirectory/")

# Base directory of images / logos used
IMG_DIR = os.path.dirname(ButterAndCrust.images.__file__)
