# -*- coding: utf-8 -*-

import pydicom
import numpy as np

"""
Created on Thu Apr 18 10:59:07 2024

@author: cofo

"""


def to_jpg(file_path, output_path):
    '''
    takes one compress dicomm image and un-compress it into a jpg

    libraries:
            import pydicom
            import numpy as np


    Args: - file_path : the path (with file name) to the compressed dicom file
          - output_path : the path (with file name) where the jpg is to be saved

    Returns: nothing
           
    Actions : it saves a jpg into the direction you gave as input

    notes : - 
    '''

    # Load the compressed DICOM file
    ds = pydicom.filereader.dcmread(file_path)
    # Apply VOI LUT (Value of Interest Lookup Table) if available
    data = pydicom.pixel_data_handlers.util.apply_voi_lut(ds.pixel_array, ds)
    
    # Convert the pixel data to a format that Pillow can use
    image_array = ds.pixel_array
    image_array = np.uint8((image_array / np.max(image_array)) * 255)  # Normalize to 0-255
    
    # Create a PIL image from the array
    image = Image.fromarray(image_array)
    
    # Save the image as JPEG
    image.save(output_path)
    
    print(f"no Metadata saving option available for jpg output")



def to_dicom(file_path, output_path, metadata_print):
    """
    takes one compress DICOM image and un-compress it into a DICOM

        libraries:
                import pydicom


        Args: - file_path : the path (with file name) to the compressed dicom file
              - output_path : the path (with file name) where the jpg is to be saved
              - metadata_print

        Returns: ds, the dicom file

        actions: and it saves a DICOM into the direction you gave as input
                 and a text file containing its metadata if the argument "metadata _print" is true.

        notes : - 
    """

    # Load the compressed DICOM file
    ds = pydicom.filereader.dcmread(file_path)
    
    # Check if Pixel Data is compressed
    if ds.file_meta.TransferSyntaxUID.is_compressed:
        # Use GDCM to decompress the image
        ds.decompress()
        
    # Save the decompressed DICOM file
    ds.save_as(output_path)
    
    if metadata_print == True:
        #==================== Saving its metadata in a text file ==========================
        output_metadata_file_path = output_path + "-METADATA.txt"
        with open(output_metadata_file_path, 'w') as file:
            # Write the metadata to the file
            file.write(str(ds))
                
        print(f"Metadata of file {file_path.split('/')[-1]} saved to {output_path}")
    
    return ds
    
    
if __name__ == "__main__":
    print("this script is meant to be imported as a module, not run as a standalone.")