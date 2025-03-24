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
import numpy as np
import glob
import sys
import tkinter as tk
from tkinter import filedialog
import tifffile as tiff
import numpy as np
'''
# Add the directory to the sys.path
sys.path.append('D:/EmpaData/COFO - HP/03 - Github/dvpt-at-EMPA/HappyBisons/image analysis')
# Now you can import modules from that directory
import tools.CT_modification_functions as CT_modification_functions
import tools.CT_visualization_functions as CT_visualization_functions
import tools.CT_visualization_window as CT_visualization_window
'''

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
    
    tiff_directory = glob.glob(input_path)
    print(f"{len(tiff_directory)} images found.")
    Image = tiff.imread(tiff_directory[0])
    Dimension = (int(Image.shape[0]), int(Image.shape[1]), len(tiff_directory))
    Spacing = (float(0.2), float(0.2), float(0.2))
    Origin = (0,0,0)
    NpArrDc = np.zeros(Dimension, dtype=np.float32)
    for filename in tiff_directory:
        image_array = tiff.imread(filename)
        NpArrDc[:, :, tiff_directory.index(filename)] = image_array
        print(f"{filename} extracted")
    print("now saving as mhd")
    NpArrDc = np.transpose(NpArrDc, (2, 0, 1))  # axis transpose
    sitk_img = sitk.GetImageFromArray(NpArrDc, isVector=False)
    sitk_img.SetSpacing(Spacing)
    sitk_img.SetOrigin(Origin)
    sitk.WriteImage(sitk_img, os.path.join(output_path + ".mhd"))
    return


# Create a Tkinter root window
root = tk.Tk()
# Prompt the user to select a file using a file explorer
print("Please select input file...")
input_file = filedialog.askopenfile().name
input_file = str(input_file).split('_')[:-1]
input_file = "_".join(input_file)+"*.tif"
print(f"selected input file is : {input_file}")
print(' ')

# Prompt the user to select a path using a file explorer
print("Please select output folder...")
output_folder = filedialog.askdirectory() + '/'
print(f"selected output folder is : {output_folder}")
print(' ')
root.withdraw()



convert(input_path=input_file,output_path=output_folder+'skull c326i')
print('conversion succesfull')
