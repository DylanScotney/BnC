import os
import shutil
import csv

def delete_dir(dirname):
    """
    Deletes a directory and all it's contents
    """
    if os.path.exists(dirname):
        shutil.rmtree(dirname)

def write_dict_to_csv(headers, values, outfile):
    """
    Writes a dictionary to csv such that each row will have 2 columns; 
    key and value.

    Args:
        headers(``list``): list of column headers. 
            Should be length 2
        values(``dict``): values to save 
        outfile(``str``): filepath of output location
    """

    with open(outfile, 'w', newline='') as csv_file:  
        writer = csv.writer(csv_file)
        writer.writerow([headers[0], headers[1]])
        for key, value in values.items():
            writer.writerow([key, value])


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