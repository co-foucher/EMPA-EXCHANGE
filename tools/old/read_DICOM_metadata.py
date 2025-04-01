import pydicom
import numpy as np
from PIL import Image
import pandas as pd
import shutil
import sys
import tkinter as tk
from tkinter import filedialog
import inspect
import os
import SimpleITK as sitk

root = tk.Tk()
# Prompt the user to select a file using a file explorer
input_file_path = filedialog.askopenfilename() # this is the mhd file contnaing the whole image, no filter, no segmentation
root.withdraw()

print(' ')
print('==============================================================')
print('================starting matadata extraction==================')
print('==============================================================')
print(' ')
'''
#ds = pydicom.filereader.dcmread(input_file_path)
ds = pydicom.dcmread(input_file_path)

# Check if Pixel Data is compressed
if ds.file_meta.TransferSyntaxUID.is_compressed:
    print('================ uncompressing file ==================')
    print(f"Metadata of file before uncompressing:")
    print(f"Patient's Name: {ds.get('PatientName', 'Unknown')}")
    print(f"Patient ID: {ds.get('PatientID', 'Unknown')}")
    print(f"Modality: {ds.get('Modality', 'Unknown')}")
    print(f"Study Date: {ds.get('StudyDate', 'Unknown')}")
    print(f"Slice Thickness: {ds.get('SliceThickness', 'Not available')}")
    print('================ file uncompressed ==================')
    # Use GDCM to decompress the image
    ds.decompress()

#==================== printing metadata =========================
#print(f"Metadata of file : {ds.slicethickness}")


# Accessing and printing specific metadata attributes
print(f"Resulting Metadata of file:")
print(f"Patient's Name: {ds.get('PatientName', 'Unknown')}")
print(f"Patient ID: {ds.get('PatientID', 'Unknown')}")
print(f"Modality: {ds.get('Modality', 'Unknown')}")
print(f"Study Date: {ds.get('StudyDate', 'Unknown')}")
print(f"Slice Thickness: {ds.get('SliceThickness', 'Not available')}")



#==================== Saving its metadata in a text file ==========================
output_metadata_file_path = output_path + "-METADATA.txt"
with open(output_metadata_file_path, 'w') as file:
    # Write the metadata to the file
    file.write(str(ds))
        
print(f"Metadata of file {file_path.split('/')[-1]} saved to {output_path}")

'''
# Read the DICOM file
image = sitk.ReadImage(input_file_path)

# Access metadata

slice_thickness = image.GetMetaData("0018|0050") if image.HasMetaDataKey("0018|0050") else "Not available"
patient_name = image.GetMetaData("0010|0010") if image.HasMetaDataKey("0010|0010") else "Unknown"
patient_id = image.GetMetaData("0010|0020") if image.HasMetaDataKey("0010|0020") else "Unknown"
modality = image.GetMetaData("0008|0060") if image.HasMetaDataKey("0008|0060") else "Unknown"
study_date = image.GetMetaData("0008|0020") if image.HasMetaDataKey("0008|0020") else "Unknown"

print(f"Metadata of file:")
print(f"Patient's Name: {patient_name}")
print(f"Patient ID: {patient_id}")
print(f"Modality: {modality}")
print(f"Study Date: {study_date}")
print(f"Slice Thickness: {slice_thickness}")

# Optionally, access the image data
image_array = sitk.GetArrayFromImage(image)
print(f"Image shape: {image_array.shape}")

