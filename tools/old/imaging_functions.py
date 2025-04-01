import SimpleITK as sitk
import tkinter as tk
from tkinter import filedialog
import numpy as np
import ipywidgets
import matplotlib.pyplot as plt
from PIL import Image
import scipy
from ipywidgets import interact
from matplotlib.widgets import Slider
from matplotlib import gridspec

#===========================================================================================================================
#============================================== list of functions ==========================================================
#===========================================================================================================================

#1 crop_images
#2 make_histogram
#3 browse_images
#4 browse_2_images
#5 blend_images
#6 browse_blended_images
#7 segment_from_threshold
#8 apply_threshold
#9 dilate_filter
#10 erode_filter


#===========================================================================================================================
#=================================================== function 1 ============================================================
#===========================================================================================================================



def crop_images(point, direction, images):
    ''' 
    Lets you crop images in an mhd stack.
    The crop is always a straight line vertical or horizontal.
    
    Inputs: - point: an integer value at which the crop will happen
            - direction: a string ('up', 'down', 'right', 'left') indicating which part of the images around the point will be KEPT
            - images: the mhd stack (SimpleITK Image object)

    Outputs: - cropped_image: a cropped image as a SimpleITK Image object
    '''

    print('Cropping image')
    images_array = sitk.GetArrayFromImage(images)
    n = images_array.shape[0]
    y = images_array.shape[1]
    x = images_array.shape[2]
    print(f"Current size is {n}, {y}, {x}")

    if direction == 'down':
        start_index = [0, point, 0]
        size = [x, y - point, n]

    elif direction == 'up':
        start_index = [0, 0, 0]
        size = [x, point, n]

    elif direction == 'right':
        start_index = [point, 0, 0]
        size = [x - point, y, n]

    elif direction == 'left':
        start_index = [0, 0, 0]
        size = [point, y, n]

    elif direction =='back':
        start_index = [0, 0, point]
        size = [x , y, n - point]
    
    else:
        raise ValueError("Invalid direction. Must be one of 'up', 'down', 'right', 'left'.")

    extract_filter = sitk.ExtractImageFilter()
    extract_filter.SetSize(size)
    extract_filter.SetIndex(start_index)
    
    # Apply the filter to crop the image
    cropped_image = extract_filter.Execute(images)
    print("Image cropped")
    
    cropped_images_array = sitk.GetArrayFromImage(cropped_image)
    n = cropped_images_array.shape[0]
    y = cropped_images_array.shape[1]
    x = cropped_images_array.shape[2]
    print(f"New size is {n}, {y}, {x}")
    
    return cropped_image

#===========================================================================================================================
#=================================================== function 2 ============================================================
#===========================================================================================================================


def make_histogram(image):
    '''
    Inputs: - mhd stack (SimpleITK image)

    Outputs: - matplotlib plot
    '''
    # Convert the SimpleITK image to a NumPy array
    array = sitk.GetArrayFromImage(image)
    
    # Exclude zero values
    array = array[array != 0]

    # Get unique values and their counts
    unique_values, counts = np.unique(array, return_counts=True)
    
    # Create the histogram plot
    plt.figure(figsize=(10, 6))
    plt.bar(unique_values, counts, color='blue', alpha=0.7)
    plt.xlabel('Pixel Value')
    plt.ylabel('Frequency')
    plt.title('Histogram of Pixel Values (Excluding Zeros)')
    plt.grid(True)
    plt.show()


#===========================================================================================================================
#=================================================== function 3 ============================================================
#===========================================================================================================================


def browse_images(images):
    ''' 
    Lets you browse through an mhd stack using an interactive slider within the figure. 
    When clicking somewhere in the picture, it will print the value and position of the pixel you selected.
    The image is opened in another window in order to be interactive.
    
    Inputs: -mhd stack

    Outputs: -none

    Other: -creates an interactive plot
           - !!!!! you need %matplotlib qt !!!! in your code
    '''
    images = sitk.GetArrayFromImage(images)
    n = images.shape[0]  # Number of slices

    def histogram_values(image):
        # Exclude zero values
        image = image[image != 0]
        # Get unique values and their counts
        unique_values, counts = np.unique(image, return_counts=True)
        #counts = np.delete(counts, 0)
        #unique_values = np.delete(unique_values, 0)
        return unique_values, counts

    def greyvalue_at_coord(images, slice, x, y):
        numrows, numcols = images.shape[1], images.shape[2]
        col = int(x + 0.5)
        row = int(y + 0.5)
        if 0 <= col < numcols and 0 <= row < numrows:
            grey = images[slice, row, col]
            return grey
        else:
            return None

    def onclick(event):
        if event.inaxes:
            x, y = event.xdata, event.ydata
            slice = int(slice_slider.val)
            grey = greyvalue_at_coord(images, slice, x, y)
            if grey is not None:
                print(f"Clicked at coordinates: x={x}, y={y}, in slice {slice}, Pixel value: {grey}")
    
    # Create a figure with gridspec
    fig = plt.figure(figsize=(14, 7))
    gs = gridspec.GridSpec(1, 2, width_ratios=[3, 1])  # Make first subplot twice the width of the second

    # Create subplots
    ax_image = fig.add_subplot(gs[0])
    ax_hist = fig.add_subplot(gs[1])

    plt.subplots_adjust(left=0.1, right=0.9, bottom=0.15, top=0.85, wspace=0.3)

    # Initial display
    ax_image.imshow(images[0], cmap='gray')
    ax_image.axis('off')

    unique_values, counts = histogram_values(images[0])
    ax_hist.plot(unique_values, counts, color='blue', alpha=0.7)
    ax_hist.set_xlabel('Pixel Value')
    ax_hist.set_ylabel('Frequency')

    # Slider axis
    ax_slider = plt.axes([0.1, 0.05, 0.8, 0.03], facecolor='lightgrey')  # Increased height of the slider for better interaction
    slice_slider = Slider(ax_slider, 'Slice', 0, n-1, valinit=0, valstep=1)

    # Update function
    def update_plot(val):
        slice = int(slice_slider.val)  # Get the current value of the slider
        temp = images[slice]
        ax_image.clear()
        ax_image.imshow(temp, cmap='gray')
        ax_image.axis('off')

        ax_hist.clear()
        unique_values, counts = histogram_values(temp)
        ax_hist.plot(unique_values, counts, color='blue', alpha=0.7)
        ax_hist.set_xlabel('Pixel Value')
        ax_hist.set_ylabel('Frequency')

        fig.canvas.draw_idle()

    # Register the update function as a callback for slider value changes
    slice_slider.on_changed(update_plot)

    # Connect the event handler to the figure
    fig.canvas.mpl_connect('button_press_event', onclick)

    plt.show()


#===========================================================================================================================
#=================================================== function 4 ============================================================
#===========================================================================================================================


def browse_2_images(images_1, images_2):
    ''' 
    let's you browse through 2 mhd stack using an interactive slider. They are displayed next to each other
    
    inputs: -mhd stack

    outputs: -none

    other: -creates an interactive plot
    '''
    n = images_1.shape[0]  # Number of slices
    
    def view_2_image(slice):
        plt.figure()
        f, axarr = plt.subplots(1,2) 
        axarr[0].imshow(images_1[slice], cmap='gray')
        axarr[0].set_title('images_1')
        axarr[0].axis('off')  # Turn off axis numbering and ticks

        axarr[1].imshow(images_2[slice], cmap='gray')
        axarr[1].set_title('images_2')
        axarr[1].axis('off')  # Turn off axis numbering and ticks
        plt.show()
    ipywidgets.interact(view_2_image, slice=ipywidgets.IntSlider(min=0, max=n-1, step=1, value=0))


#===========================================================================================================================
#=================================================== function 5 ============================================================
#===========================================================================================================================



def blend_images(image1: np.ndarray, image2: np.ndarray, blend: float) -> np.ndarray:
    """
    Blends two images according to the input blend factor.

    Args:
        image1 (np.ndarray): First image as a numpy array.
        image2 (np.ndarray): Second image as a numpy array.
        blend (float): Blend factor, goes from 0 to 100.

    Returns:
        np.ndarray: Blended image as a numpy array.
    """
    alpha = blend / 100

    # Level the two images
    image1 = image1 / np.max(image1) * 255
    image2 = image2 / np.max(image2) * 255

    # Perform alpha blending
    blended_image = alpha * image1 + (1 - alpha) * image2
    blended_image = np.clip(blended_image, 0, 255).astype(np.uint8)

    return blended_image


#===========================================================================================================================
#=================================================== function 6 ============================================================
#===========================================================================================================================



def browse_blended_images(images1, images2,block_value:bool):

    '''
    Lets you use the blend function to then plot these blended images in an interactive way.

    Args:
        images1 (sitk.Image): First image stack in SimpleITK format.
        images2 (sitk.Image): Second image stack in SimpleITK format.

    other: -creates an interactive plot
    '''

    images1 = sitk.GetArrayFromImage(images1)
    images2 = sitk.GetArrayFromImage(images2)

    n = images1.shape[0]

    # Create a figure with gridspec
    fig, ax_image = plt.subplots(figsize=(14, 7))
    plt.subplots_adjust(left=0.1, bottom=0.25)

    # Initial display
    blended_image = blend_images(images1[0], images2[0], 50)
    img_display = ax_image.imshow(blended_image, cmap='gray')
    ax_image.axis('off')

    # Slider axis
    ax_slider_slice = plt.axes([0.1, 0.15, 0.8, 0.03], facecolor='lightgrey')   # left, bottom, width, height
    slice_slider = Slider(ax_slider_slice, 'Slice', 0, n - 1, valinit=0, valstep=1)

    ax_slider_alpha = plt.axes([0.1, 0.05, 0.8, 0.03], facecolor='lightgrey')
    transparency_slider = Slider(ax_slider_alpha, 'Transparency', 0, 100, valinit=50, valstep=1)

    # Update function
    def update_plot(val):
        slice_idx = int(slice_slider.val)  # Get the current value of the slice slider
        alpha = transparency_slider.val    # Get the current value of the transparency slider
        blended_image = blend_images(images1[slice_idx], images2[slice_idx], alpha)
        img_display.set_data(blended_image)
        fig.canvas.draw_idle()

    # Register the update function as a callback for slider value changes
    slice_slider.on_changed(update_plot)
    transparency_slider.on_changed(update_plot)

    plt.show(block=block_value)


#===========================================================================================================================
#=================================================== function 7 ============================================================
#===========================================================================================================================


def segment_from_threshold(image,lower_threshold,upper_threshold):
    """
    Apply dual threshold to an image and return the binary result.
    takes in an mhd file !!
    """
    threshold_filter = sitk.BinaryThresholdImageFilter()
    threshold_filter.SetLowerThreshold(lower_threshold)  # Adjust these values based on your image
    threshold_filter.SetUpperThreshold(upper_threshold)
    threshold_filter.SetInsideValue(255)
    threshold_filter.SetOutsideValue(0)
    return threshold_filter.Execute(image)
    '''
    output = (image >= lower_threshold) & (image <= upper_threshold)
    return output * 254 
    '''


#===========================================================================================================================
#=================================================== function 8 ============================================================
#===========================================================================================================================


def apply_threshold(image,lower_threshold,upper_threshold):
    """
    Apply dual threshold to an image and return the result. !! not binaray
    takes in an array !!!

    """
    print('c PT')
    '''
    output = (image >= lower_threshold) & (image <= upper_threshold)
    return output * 254 
    '''

#===========================================================================================================================
#=================================================== function 9 ============================================================
#===========================================================================================================================



def dilate_filter(image, kernel):
    # create dilate filter
    dilate_filter = sitk.GrayscaleDilateImageFilter()
    dilate_filter.SetKernelRadius(kernel)
    return dilate_filter.Execute(image)


#===========================================================================================================================
#=================================================== function 10 ===========================================================
#===========================================================================================================================


def erode_filter(image, kernel):
    # create dilate filter
    dilate_filter = sitk.GrayscaleErodeImageFilter()
    dilate_filter.SetKernelRadius(kernel)
    return dilate_filter.Execute(image)

#===========================================================================================================================
#=================================================== function 11 ===========================================================
#===========================================================================================================================
    

def connected_filter(x:int,y:int,z:int,images):
    #print(binary_image[x, y, z])

    # Use the connected component filter with the seed 
    connected_filter = sitk.ConnectedThresholdImageFilter()
    connected_filter.SetLower(1)
    connected_filter.SetUpper(255)
    connected_filter.SetReplaceValue(255)
    connected_filter.SetSeedList([(x, y, z)])

    return connected_filter.Execute(images)