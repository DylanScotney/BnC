import pdfkit
import os
import shutil
import csv

def delete_dir(dirname):
    """
    Deletes a directory and all it's contents
    """
    if os.path.exists(dirname):
        shutil.rmtree(dirname)

def write_items_to_csv(columns, items, outfile):
    """
    Writes a dictionary to csv such that each row will have 2 columns; 
    key and value.

    :param columns:         (list) of column headers
    :param items:           (dict) of values to save
    :param outfile:         (str) output filepath
    """

    with open(outfile, 'w', newline='') as csv_file:  
        writer = csv.writer(csv_file)
        writer.writerow([columns[0], columns[1]])
        for key, value in items.items():
            writer.writerow([key, value])


def render_html_files_to_pdf(infiles, outfile, wkhtml_exe_path):
    """
    Renders a list of html files to pdf

    :param infiles:                 (list) of html filepaths to render
    :param outfile:                 (str) filepath of pdf output
    :param wkhtml_exe_path:         (str) path to wkhtltopdf executable
    """
    
    config = pdfkit.configuration(wkhtmltopdf=wkhtml_exe_path)
    pdfkit.from_file(infiles, outfile, configuration=config)


def save_file(string_to_save, basepath, filename):
    """
    Checks if directory exists before saving a file and creates

    :param string_to_save:  (str) string to save to file
    :param basepath:        (str) base path of the file
    :param filename:        (str) filename
    """

    # create dir if it doesn't already exist 
    if not os.path.exists(basepath):
        os.makedirs(basepath)

    filepath = basepath + filename

    with open(filepath, 'w', encoding="utf-8") as html_file:
        html_file.write(string_to_save)