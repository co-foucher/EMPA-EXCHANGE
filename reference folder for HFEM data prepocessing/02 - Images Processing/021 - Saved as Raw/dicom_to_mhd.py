'''
-----------------------------------------------
File Name: convert_dcm_to_mhd$
Description: convert dicom files into mhd file
Author: Jing$
Date: 16/11/2022$
-----------------------------------------------
'''
import os
import SimpleITK as sitk
import pydicom
import numpy as np
import glob
import sys
import tkinter as tk
from tkinter import filedialog


def convert(input_path,output_path):
    '''
    Procedure:
    # To get first image as refenece image, supposed all images have same dimensions
    # To get Dimensions, 3D spacing, image origin
    # To make numpy array
    # loop through all the DICOM files
        # To read the dicom file
        # store the raw image data
    :param input_path: the path of dicom files
    :param output_path: the output path of mhd file
    :return: null
    '''
    DICOM_directory = glob.glob(input_path)
    Image = pydicom.dcmread(DICOM_directory[0])
    Dimension = (int(Image.Rows), int(Image.Columns), len(DICOM_directory))
    Spacing = (float(Image.PixelSpacing[0]), float(Image.PixelSpacing[1]), float(Image.SliceThickness))
    Origin = Image.ImagePositionPatient
    NpArrDc = np.zeros(Dimension, dtype=Image.pixel_array.dtype)
    for filename in DICOM_directory:
        df = pydicom.dcmread(filename)
        NpArrDc[:, :, DICOM_directory.index(filename)] = df.pixel_array
        print(f"{filename} extracted")
    print("now saving as mhd")
    NpArrDc = np.transpose(NpArrDc, (2, 0, 1))  # axis transpose
    sitk_img = sitk.GetImageFromArray(NpArrDc, isVector=False)
    sitk_img.SetSpacing(Spacing)
    sitk_img.SetOrigin(Origin)
    sitk.WriteImage(sitk_img, os.path.join(output_path + ".mhd"))
    return



# ================ Use this version of the code to select where the mhd file will be saved using a tk window ======================
""" 
# Create a Tkinter root window
root = tk.Tk()
# Prompt the user to select a file using a file explorer
print("Please select input file...")
input_file = filedialog.askopenfile().name
input_file = str(input_file).split('_')[:-1]
input_file = "_".join(input_file)+"*.dcm"
print(' ')
# Prompt the user to select a path using a file explorer
print("Please select output folder...")
output_folder = filedialog.askdirectory() + '/'
print(f"selected output folder is : {output_folder}")
print(' ')
root.withdraw()
convert(input_path=input_file,output_path=output_folder+'skull-set1')
print('conversion succesfull')
"""


# ================ Use this version of the code to select where the mhd file to be saved where the python code is ======================

# Create a Tkinter root window
root = tk.Tk()
# Prompt the user to select a file using a file explorer
print("Please select input file...")
input_file = filedialog.askopenfile().name
root.withdraw()
input_file = str(input_file).split('_')[:-1]
input_file = "_".join(input_file)+"*.dcm"
print(' ')

#select the output folder where the mhd file will be saved: where this python file is saved
output_folder = os.getcwd()+'/'
print(f"output folder is : {output_folder}")
print(' ')

#call the convert function
convert(input_path=input_file,output_path=output_folder+'skull-set2')  #change the name of your mhd here!
print('conversion succesfull')














