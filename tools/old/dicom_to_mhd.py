'''
-----------------------------------------------
File Name: convert_dcm_to_mhd$
Description: convert dicom files into mhd file
Author: Jing$
Date: 16/11/2022$
-----------------------------------------------
'''
import tools.imaging_functions as imaging_functions
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
    Image = pydicom.read_file(DICOM_directory[0])
    Dimension = (int(Image.Rows), int(Image.Columns), len(DICOM_directory))
    Spacing = (float(Image.PixelSpacing[0]), float(Image.PixelSpacing[1]), float(Image.SliceThickness))
    Origin = Image.ImagePositionPatient
    NpArrDc = np.zeros(Dimension, dtype=Image.pixel_array.dtype)
    for filename in DICOM_directory:
        df = pydicom.read_file(filename)
        NpArrDc[:, :, DICOM_directory.index(filename)] = df.pixel_array
        print(f"{filename} extracted")
    print("now saving as mhd")
    NpArrDc = np.transpose(NpArrDc, (2, 0, 1))  # axis transpose
    sitk_img = sitk.GetImageFromArray(NpArrDc, isVector=False)
    sitk_img.SetSpacing(Spacing)
    sitk_img.SetOrigin(Origin)
    sitk.WriteImage(sitk_img, os.path.join(output_path + ".mhd"))
    return
'''
# Create a Tkinter root window
root = tk.Tk()
# Prompt the user to select a file using a file explorer
print("Please select input file...")
input_file = filedialog.askopenfile().name
input_file = str(input_file).split('_')[:-1]
input_file = "_".join(input_file)+"*.dcm"
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
map_image = sitk.ReadImage(output_folder+'skull c326i.mhd')
#image_array = sitk.GetArrayFromImage(map_image)
imaging_functions.browse_images(map_image)
'''
input_file = "D:/EmpaData/COFO - HP/01 PhD research/202406 - Basel skulls/WP2 - skull 9254/01 - Original Data/012 - uncompressed/dicom_uncompressed_ImageSet2_0001.dcm"
output_folder = "D:/EmpaData/COFO - HP/01 PhD research/202406 - Basel skulls/WP2 - skull 9254/02 - Images Processing/021 - Saved as raw/"
input_file = str(input_file).split('_')[:-1]
input_file = "_".join(input_file) 
print(f"starting work on {input_file}")
convert(input_path=input_file+"*.dcm",output_path=output_folder+'skull9254-set2')
map_image = sitk.ReadImage(output_folder+'skull9254-set2.mhd')
imaging_functions.browse_images(map_image)
input_file = "D:/EmpaData/COFO - HP/01 PhD research/202406 - Basel skulls/WP3 - skull 9255/01 - Original Data/012 - uncompressed/dicom_uncompressed_ImageSet2_0001.dcm"
output_folder = "D:/EmpaData/COFO - HP/01 PhD research/202406 - Basel skulls/WP3 - skull 9255/02 - Images Processing/021 - Saved as raw/"
input_file = str(input_file).split('_')[:-1]
input_file = "_".join(input_file) 
print(f"starting work on {input_file}")
convert(input_path=input_file+"*.dcm",output_path=output_folder+'skull9255-set2')
map_image = sitk.ReadImage(output_folder+'skull9255-set2.mhd')
imaging_functions.browse_images(map_image)
input_file = "D:/EmpaData/COFO - HP/01 PhD research/202406 - Basel skulls/WP4 - skull 11152/01 - Original Data/012 - uncompressed/dicom_uncompressed_ImageSet2_0001.dcm"
output_folder = "D:/EmpaData/COFO - HP/01 PhD research/202406 - Basel skulls/WP4 - skull 11152/02 - Images Processing/021 - Saved as raw/"
input_file = str(input_file).split('_')[:-1]
input_file = "_".join(input_file) 
print(f"starting work on {input_file}")
convert(input_path=input_file+"*.dcm",output_path=output_folder+'skull11152-set2')
map_image = sitk.ReadImage(output_folder+'skull11152-set2.mhd')
imaging_functions.browse_images(map_image)
input_file = "D:/EmpaData/COFO - HP/01 PhD research/202406 - Basel skulls/WP5 - skull 17940/01 - Original Data/012 - uncompressed/dicom_uncompressed_ImageSet2_0001.dcm"
output_folder = "D:/EmpaData/COFO - HP/01 PhD research/202406 - Basel skulls/WP5 - skull 17940/02 - Images Processing/021 - Saved as raw/"
input_file = str(input_file).split('_')[:-1]
input_file = "_".join(input_file) 
print(f"starting work on {input_file}")
convert(input_path=input_file+"*.dcm",output_path=output_folder+'skull17940-set2')
map_image = sitk.ReadImage(output_folder+'skull17940-set2.mhd')
imaging_functions.browse_images(map_image)
input_file = "D:/EmpaData/COFO - HP/01 PhD research/202406 - Basel skulls/WP6 - skull c326i/01 - Original Data/012 - uncompressed/dicom_uncompressed_ImageSet2_0001.dcm"
output_folder = "D:/EmpaData/COFO - HP/01 PhD research/202406 - Basel skulls/WP6 - skull c326i/02 - Images Processing/021 - Saved as raw/"
input_file = str(input_file).split('_')[:-1]
input_file = "_".join(input_file) 
print(f"starting work on {input_file}")
convert(input_path=input_file+"*.dcm",output_path=output_folder+'skullc326i-set2')
map_image = sitk.ReadImage(output_folder+'skullc326i-set2.mhd')
imaging_functions.browse_images(map_image)