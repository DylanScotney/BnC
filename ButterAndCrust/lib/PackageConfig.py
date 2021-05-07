import os
import posixpath

import ButterAndCrust
import ButterAndCrust.images

DEVELOPMENT = False

# Airtable keys.
base_key = "appWCrLerVduIq5SR" if DEVELOPMENT else "appPhU88MDepiAjpR"
api_key = "keyQNWjWomXyaBGJK" if DEVELOPMENT else "keyEabJJ9ddj5UNsA"

# Must install [https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.4/wkhtmltox-0.12.4_msvc2015-win64.exe]
PATH_WKHTMLTOPDF =  "C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe"

# Default output location for package slips and stock requirements 
# this can also be changed on the command line
DEFAULT_OUTPUT_LOCATION = "C:\\Users\\olibr\\OneDrive\\Desktop\\Butter\\Output\\"

# A temporary working directory that will store files
WORKING_DIRECTORY = posixpath.join(os.path.dirname(ButterAndCrust.__file__), "WorkingDirectory/")

# Base directory of images / logos used
IMG_DIR = os.path.dirname(ButterAndCrust.images.__file__)