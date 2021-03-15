import os
import posixpath

import ButterAndCrust
import ButterAndCrust.images

DEVELOPMENT = False

# Airtable keys.
base_key = "appWCrLerVduIq5SR" if DEVELOPMENT else "appPhU88MDepiAjpR"
api_key = "keyQNWjWomXyaBGJK" if DEVELOPMENT else "keyEabJJ9ddj5UNsA"

# Location of cold storage DB
DB_BASE_PATH = "/Users/olliebrenman/Desktop/Butter/code/DB/"
ORDERS_DB_NAME = "OrderHistory"
COLD_STORAGE_ORDERS_DB_LOC = DB_BASE_PATH + ORDERS_DB_NAME + ".db"

# Must install [https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.4/wkhtmltox-0.12.4_msvc2015-win64.exe]
PATH_WKHTMLTOPDF =  "/Users/olliebrenman/Desktop/Butter/code/wkhtmltopdf"

# Default output location for package slips and stock requirements 
# this can also be changed on the command line
DEFAULT_OUTPUT_LOCATION = "/Users/olliebrenman/Desktop/Butter/code/Output/"

# A temporary working directory that will store files
WORKING_DIRECTORY = posixpath.join(os.path.dirname(ButterAndCrust.__file__), "WorkingDirectory/")

# Base directory of images / logos used
IMG_DIR = os.path.dirname(ButterAndCrust.images.__file__)
