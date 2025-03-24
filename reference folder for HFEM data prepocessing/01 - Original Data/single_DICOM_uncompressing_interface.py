# -*- coding: utf-8 -*-

"""
Created on Thu Apr 18 10:59:07 2024

@author: cofo

Nice interface to uncompress ONE compressed-DICOM files into a jpg or dicom

    Args: none

    Returns: 

    notes : - 
"""

import decompress_dicom_as_jpg
import decompress_dicom_into_dicom
import pydicom
import numpy as np
from PIL import Image
import pandas as pd
import shutil
import sys
import tkinter as tk
from tkinter import filedialog
import inspect

def interactive_single_dicom_uncompressing():

    #==================   Path variables definition   =============================
    # Create a Tkinter root window
    root = tk.Tk()

    # Prompt the user to select a file using a file explorer
    input_file_path = filedialog.askopenfilename()

    # Prompt the user to select a path using a file explorer
    output_folder_path = filedialog.askdirectory()

    root.withdraw()

    # Print the selected file path
    print("Selected file:", input_file_path)
    input_file_name = str(input_file_path.split("/")[-1])

    # =================== uncompressing file ==========================
    output_file_path = output_folder_path + "/uncompressed_dicom-" + input_file_name
    if export_file_type == 'jpg' :
        ds = decompress_dicom_as_jpg.main(input_file_path, output_file_path)
        
    else:
        ds = decompress_dicom_into_dicom.main(input_file_path, output_file_path, True)


if __name__ == '__main__':
    interactive_single_dicom_uncompressing()