import SimpleITK as sitk
import tkinter as tk
from tkinter import filedialog
import numpy as np
import ipywidgets
import matplotlib.pyplot as plt
from PIL import Image
import scipy
from ipywidgets import interact
from matplotlib.widgets import Slider, Button
from matplotlib import gridspec
import time

'''
This repositery is for functions used to visualize or analsis CT scans data
'''
#===========================================================================================================================
#============================================== list of functions ==========================================================
#===========================================================================================================================

#1 make_histogram
#2 browse_images
#3 browse_2_images
#4 blend_images
#5 browse_blended_images
#6 select_pixels


#===========================================================================================================================
#=================================================== function 1 ============================================================
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
#=================================================== function 2 ============================================================
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
    v_min = np.min(images)
    v_max = np.max(images)

    def histogram_values(image):
        # Exclude zero values
        image = image[image != 0]
        # Get unique values and their counts
        unique_values, counts = np.unique(image, return_counts=True)
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
        if event.inaxes == ax_image:
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
    img_display = ax_image.imshow(images[0], cmap='gray', vmin=v_min, vmax=v_max)
    ax_image.axis('off')

    unique_values, counts = histogram_values(images[0])
    ax_hist.plot(unique_values, counts, color='blue', alpha=0.7)
    ax_hist.set_xlabel('Pixel Value')
    ax_hist.set_ylabel('Frequency')

    # Slider axis
    ax_slider = plt.axes([0.1, 0.05, 0.8, 0.03], facecolor='lightgrey')  # left, bottom, width, height
    slice_slider = Slider(ax_slider, 'Slice', 0, n-1, valinit=0, valstep=1)

    # Update function
    def update_plot(val):
        slice = int(slice_slider.val)  # Get the current value of the slider
        temp = images[slice]
        img_display.set_data(temp)
        img_display.set_clim(vmin=v_min, vmax=v_max)  # Update the color limits
        fig.canvas.draw_idle()

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
#=================================================== function 3 ============================================================
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
#=================================================== function 4 ============================================================
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
#=================================================== function 5 ============================================================
#===========================================================================================================================

def browse_blended_images(images1, images2,block_value:bool):

    '''
    Lets you use the blend function to then plot these blended images in an interactive way. You can dinamically change the "blending factor"

    Args:
        images1 (sitk.Image): First image stack in SimpleITK format.
        images2 (sitk.Image): Second image stack in SimpleITK format.

    Other: -creates an interactive plot
    '''
    images1 = sitk.GetArrayFromImage(images1)
    images2 = sitk.GetArrayFromImage(images2)

    v_min = 0
    v_max = 255

    n = images1.shape[0]

    # Create a figure with gridspec
    fig, ax_image = plt.subplots(figsize=(14, 7))
    plt.subplots_adjust(left=0.1, bottom=0.25)

    # Initial display
    blended_image = blend_images(images1[0], images2[0], 50)
    img_display = ax_image.imshow(blended_image, cmap='gray', vmin=v_min, vmax=v_max)
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
#=================================================== function 6 ============================================================
#===========================================================================================================================

def select_pixels(images):

    '''
    Opens an interactive window to manually select pixels in a sitk image stack

    Args: 
        - 1 sitk image stack

    returns:
        - numpy array of the coordinates of all the slected pixels (slice, y, x)

    notes: 
        - Be very carefull !! We show images_rgb, but get grey and positions values from images!!! 2 diferrent variables
    
    '''
    selected_pixels = []
    images = sitk.GetArrayFromImage(images)
    n = images.shape[0]  # Number of slices

    temp_images = images
    temp_images = temp_images / np.max(images) #for rbg, values go from 0 to 1

    # Convert grayscale image to RGB for color modification
    images_rgb = np.stack([temp_images, temp_images, temp_images], axis=-1)  #in rgb, equal values will give a shade of grey
                                                                             # rgb is added as the fourth axis !


    # Plot update function
    def update_plot(val):
        slice = slice_slider.val  # Get the current value of the slider
        img_display.set_data(images_rgb[slice])
        fig.canvas.draw_idle()

    #function to get the grey value of a pixel in an image
    def greyvalue_at_coord(images, slice, x, y):
        numrows, numcols = images.shape[1], images.shape[2]
        col,row = int(x + 0.5), int(y + 0.5)
        if 0 <= col < numcols and 0 <= row < numrows:
            grey = images[slice, row, col]
            return grey
        else:
            return None

    def next_slice(event):
        current_slice = slice_slider.val
        if current_slice < n - 1:
            slice_slider.set_val(current_slice + 1)

    def prev_slice(event):
        current_slice = slice_slider.val
        if current_slice > 0:
            slice_slider.set_val(current_slice - 1)

    #function to change the button's color. Its color also controls the 3D on/off value of the brush
    def change_button_color(event):
        if button_3D_brush.color == "red":
            button_3D_brush.color = "blue"
        elif button_3D_brush.color == "blue":
            button_3D_brush.color = "red"

    def onscroll(event):
        current_slice = slice_slider.val
        
        if event.button == 'up' and current_slice < n - 1:
            slice_slider.set_val(current_slice + 1)
            
        elif event.button == 'down' and current_slice > 0:
            slice_slider.set_val(current_slice - 1)
        
        update_plot(slice_slider.val)


    def onclick(event):
        """
        function controlling what happens when the user clicks on a pixel
        it's in here that:
            - we check if the user click in an allowed area
            - we check wether the brush is in 3D mode or not and elect the pixels accordingly
            - after each click the color of selected pixels are turned to blue and the plot updated

        notes:
            - selected pixels are appended in the variable selected_pixels


        """
        if event.inaxes == ax_image and event.button == 1:          # Check if the click is within the image axes and not on the slider
            toolbar = plt.get_current_fig_manager().toolbar         # save the current zoom and position on the image
            if toolbar.mode == '':                                  # do not register if using any toolbar tool 
                x, y = int(event.xdata + 0.5), int(event.ydata + 0.5)       # save click position
                slice = int(slice_slider.val)
                grey = greyvalue_at_coord(images, slice, x, y)              # save  grey value at click position
                if grey is not None:                                        # insures that you clicked in a not non-defined pixel

                    #now looping through all the pixels according to the brush's thickness
                    for t in range(-int(brush_radius_slider.val), int(brush_radius_slider.val) + 1):        #thickness of the brush (x-axis)
                        for g in range(-int(brush_radius_slider.val), int(brush_radius_slider.val) + 1):    #height of the brush (y-axis)
                            
                            #============= 2D brush =============
                            if button_3D_brush.color == "red":      
                                if np.sqrt(t ** 2 + g ** 2) <= int(brush_radius_slider.val):            # make the brush round
                                    grey = greyvalue_at_coord(images, slice, x + t, y + g)
                                    if grey is not None:
                                        selected_pixels.append((int(x + t), int(y + g), int(slice)))    # append list of slected pixels
                                        images_rgb[slice, int(y + g), int(x + t)] = [0, 0, 255]         # Set the clicked pixel to blue (0, 0, 255)
                            
                            #============ 3D brush =============
                            elif button_3D_brush.color == "blue":  #on est en 3D
                                for k in range(-int(brush_radius_slider.val), int(brush_radius_slider.val) + 1):    # deepness of the brush (z-axis)
                                    if np.sqrt(t ** 2 + g ** 2 + k**2) <= int(brush_radius_slider.val):             # make the brush round
                                        grey = greyvalue_at_coord(images, slice, x + t, y + g)
                                        if grey is not None:                                                    # insures that you clicked in a not non-defined pixel
                                            selected_pixels.append((int(x + t), int(y + g), int(slice + k)))        # append list of slected pixels
                                            images_rgb[slice + k, int(y + g), int(x + t)] = [0, 0, 255]             # Set the clicked pixel to blue (0, 0, 255)
                update_plot(slice_slider.val)


    

    # Create a figure
    fig, ax_image = plt.subplots(figsize=(14, 7))
    plt.subplots_adjust(left=0.05, right=0.99, bottom=0.1, top=0.99)

    # Initial display
    img_display = ax_image.imshow(images_rgb[0], cmap='gray')
    ax_image.axis('off')

    # Sliders
    ax_slider = plt.axes([0.15, 0.05, 0.7, 0.03], facecolor='lightgrey')   # left, bottom, width, height
    slice_slider = Slider(ax_slider, 'Slice', 0, n-1, valinit=0, valstep=1)

    ax_brush_radius = plt.axes([0.03, 0.15, 0.03, 0.7], facecolor='lightgrey')  # left, bottom, width, height
    brush_radius_slider = Slider(ax_brush_radius, 'brush thickness', 0, 10, valinit=1, valstep=1, orientation='vertical')


    # Buttons
    ax_button_prev = plt.axes([0.02, 0.05, 0.05, 0.04])  # left, bottom, width, height
    button_prev = Button(ax_button_prev, 'Previous')
    button_prev.on_clicked(prev_slice)

    ax_button_next = plt.axes([0.9, 0.05, 0.05, 0.04])   # left, bottom, width, height
    button_next = Button(ax_button_next, 'Next')
    button_next.on_clicked(next_slice)

    ax_button_3D_brush = plt.axes([0.02, 0.9, 0.05, 0.05])     # left, bottom, width, height
    button_3D_brush = Button(ax_button_3D_brush, '3D brush')
    button_3D_brush.color = "red"
    button_3D_brush.on_clicked(change_button_color)

    # Register the update function as a callback for slider value changes
    slice_slider.on_changed(update_plot)
    fig.canvas.mpl_connect('scroll_event', onscroll)


    # Connect the event handler to the figure
    fig.canvas.mpl_connect('button_press_event', onclick)
    
    plt.show(block=True)
    return np.unique(np.array(selected_pixels),axis=0)      #delete all redondant pixel due to multi-click from the user
