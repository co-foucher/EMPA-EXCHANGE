"""
Created on Thu Apr 18 10:59:07 2024

@author: cofo

Nice interface to uncompress one or several compressed-DICOM files into a jpg or dicom

    Args: 

    Returns: 

    notes : - 
"""

import tools.decompress_dicom
import tools.loading_bar
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


#==================   Path variables definition   =============================

# Create a Tkinter root window
root = tk.Tk()

# Prompt the user to select a file using a file explorer
print("Please select input folder...")
input_folder = filedialog.askdirectory() + '/'
print(f"selected input folder is : {input_folder}")
print(' ')

# Prompt the user to select a path using a file explorer
print("Please select output folder...")
output_folder = filedialog.askdirectory() + '/'
print(f"selected output folder is : {output_folder}")
print(' ')

root.withdraw()

#automatically detect the number of files in the input directory
number_of_files = sum(1 for file in os.listdir(input_folder) if os.path.isfile(os.path.join(input_folder, file)))


#============================ uncompressing and saving  in
#     a temporary folder which is created to store all the un-compressed but not organized files
#                                   it is later deleted ===============================================


df = pd.DataFrame(                          #this dataframe saves a few key metadata usefull to re-organize the files later
    {"original dicom number" : [],
     "SeriesDescription" : [],
     "SliceLocation" : [],
     "new numbering system" : []}
    )

temp_folder = output_folder + 'temp/'           # temporary folder to store all the un-compressed but not organized files
os.makedirs(temp_folder)                


print('Sarting un-compressing DICOMs...')
for i in range(2,number_of_files):
    tools.loading_bar.main(i, number_of_files, bar_length=30)
    #here, the uncompressed dicomm is saved in the output_path
    file_path = input_folder + f"{i:04}"
    disorganized_output_path = temp_folder + "uncompressed" + f"{i:04}" + ".dcm"
    ds=tools.decompress_dicom.to_dicom(file_path, disorganized_output_path, False)    
    
    #saving usefull metadata
    df2 = pd.DataFrame({"original dicom number" : [i],
         "SeriesDescription" : [str(ds.SeriesDescription)],
         "SliceLocation" : [float(ds.SliceLocation)],
         "new numbering system" : [0]})
    df = pd.concat([df,df2], ignore_index = True) 


#%%
#=================== using saved metadata in df to reorganize the files' numbering
#            The un-gornized files are copied with the right number in the defnitive output path
#                           at the end, the temp folder is deleted =====================
#Iam am also changing the file names depending on which series they belong to

print('listing all the different SeriesDescription in your files...')

image_set = 0
for serie_name in df['SeriesDescription'].unique():
    image_set = image_set + 1
    print(' ')
    print(f'reorganizing files in the serie : {serie_name}')
    #re-organize df by seriesdescription and slicelocation
    df_reorganized = df.loc[df['SeriesDescription'] == serie_name].sort_values("SliceLocation")
    
    #update the new numbering system : now one line give the original number and the wished new number
    df_reorganized.reset_index(drop=True, inplace=True)
    df_reorganized["new numbering system"] = df_reorganized.index+1
    
    for i in range(1,df_reorganized['SeriesDescription'].count()):
        tools.loading_bar.main(i, df_reorganized['SeriesDescription'].count(), bar_length=30)
        image_description = 'ImageSet' + str(image_set)
        mask = df_reorganized['new numbering system'] == i
        j = int(df_reorganized.loc[mask]['original dicom number']) #j is the old number
        
        disorganized_output_path = temp_folder +"uncompressed"  + f"{j:04}" + ".dcm"
        reorganized_output_path = output_folder + "dicom_uncompressed_" + image_description + f"_{i:04}" + ".dcm"
        
        shutil.copyfile(disorganized_output_path, reorganized_output_path)  #!every file ends up duplicated: once with the original name and once with the new name

    ds = pydicom.filereader.dcmread(reorganized_output_path)
    output_metadata_file_path = output_folder + "-METADATA-ImageSet" + str(image_set) + ".txt"
    with open(output_metadata_file_path, 'w') as file:
        # Write the metadata to the file
        file.write(str(ds))
    print(f"Metadata of {serie_name} saved to {output_metadata_file_path}")
        
        
shutil.rmtree(temp_folder)
