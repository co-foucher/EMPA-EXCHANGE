import SimpleITK as sitk
import numpy as np
import matplotlib.pyplot as plt
#from PIL import Image
from matplotlib.widgets import Slider
from matplotlib import gridspec
from skimage import filters
import cv2 as cv
#from scipy import signal

'''
This repositery is for functions used to modify CT scans data
'''

#===========================================================================================================================
#============================================== list of functions ==========================================================
#===========================================================================================================================

#1 crop_images
#2 segment_from_threshold
#3 apply_threshold
#9 dilate_filter
#5 erode_filter
#6 connected_filter
#7 sobel_edge_filter
#8 watershed_algorithm
#9 crack_detection_algorithm
#10 find_small_holes


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

    elif direction =='front':
        start_index = [0, 0, 0]
        size = [x , y, point]
    
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


def segment_from_threshold(image,lower_threshold,upper_threshold):
    """
    Apply dual threshold to an image and return the binary result.

    Inputs: - lower threshold: pixels with a grey value bellow will be set to zero
            - upper threshold: pixels with a grey value above will be set to zero
            - image: the mhd stack (SimpleITK Image object)

    Outputs: - mhd stack (SimpleITK Image object). Binary version of your input image (225 or 0)
    """
    threshold_filter = sitk.BinaryThresholdImageFilter()
    threshold_filter.SetLowerThreshold(lower_threshold)  # Adjust these values based on your image
    threshold_filter.SetUpperThreshold(upper_threshold)
    threshold_filter.SetInsideValue(255)
    threshold_filter.SetOutsideValue(0)
    return threshold_filter.Execute(image)



#===========================================================================================================================
#=================================================== function 3 ============================================================
#===========================================================================================================================


def apply_threshold(image,lower_threshold,upper_threshold):
    """
    Apply dual threshold to an image and delete pixel (set equal to zero) outside of the range.
    THIS IS NOT SEGMENTATION

    Inputs: - lower threshold: pixels with a grey value bellow will be set to zero
            - upper threshold: pixels with a grey value above will be set to zero
            - image: the mhd stack (SimpleITK Image object)

    Outputs: - mhd stack (SimpleITK Image object). 
    """
    image_array = sitk.GetArrayFromImage(image)
    image_array[image_array > upper_threshold] = lower_threshold
    image_array[image_array <lower_threshold] = lower_threshold
    image_array = image_array - lower_threshold
    image = sitk.GetImageFromArray(image_array)
    
    return image
    

#===========================================================================================================================
#=================================================== function 4 ============================================================
#===========================================================================================================================


def dilate_filter(image, kernel):
    # create dilate filter
    dilate_filter = sitk.GrayscaleDilateImageFilter()
    dilate_filter.SetKernelRadius(kernel)
    return dilate_filter.Execute(image)


#===========================================================================================================================
#=================================================== function 5 ===========================================================
#===========================================================================================================================


def erode_filter(image, kernel):
    # create dilate filter
    erode_filter = sitk.GrayscaleErodeImageFilter()
    erode_filter.SetKernelRadius(kernel)
    return erode_filter.Execute(image)

#===========================================================================================================================
#=================================================== function 6 ===========================================================
#===========================================================================================================================
    

def connected_filter(x:int,y:int,z:int,images):
    # Use the connected component filter with the seed 
    connected_filter = sitk.ConnectedThresholdImageFilter()
    connected_filter.SetLower(1)
    connected_filter.SetUpper(255)
    connected_filter.SetReplaceValue(255)
    connected_filter.SetSeedList([(x, y, z)])

    return connected_filter.Execute(images)


#===========================================================================================================================
#=================================================== function 7 ===========================================================
#===========================================================================================================================
    
def sobel_edge_filter(images):
    image_array = sitk.GetArrayFromImage(images)
    sobel = filters.sobel(image_array)
    return sitk.GetImageFromArray(sobel)


#===========================================================================================================================
#=================================================== function 8 ===========================================================
#===========================================================================================================================

def watershed_algorithm(single_image, binary_image, alpha, beta):
    ''' 
    Lets you use a watershed algorithm to color edges of zones (touching or not) black.
    
    Inputs: - single image: np.array ; is used for the "topography of your zones
            - binary_image: np.array ; is used to define where the objects are
            - alpha ; is a control parameter from 0 to 1
            - beta ; is a control parameter. an integer from 0 to infinit..

    Outputs: - modified input image
    '''
    # Define a kernel for morphological operations
    kernel = np.ones((3, 3), np.uint8)

    # Convert SimpleITK image to NumPy array UINT8
    #single_image = sitk.GetArrayFromImage(single_image)
    single_image = cv.normalize(single_image, None, 0, 255, cv.NORM_MINMAX, cv.CV_8U)
    binary_image = cv.normalize(binary_image, None, 0, 255, cv.NORM_MINMAX, cv.CV_8U)

    # Dilate to get sure background area
    sure_bg = np.copy(binary_image)
    #sure_bg[single_image>threshold_level_max*1.25] = 0
    sure_bg = cv.dilate(sure_bg, kernel, iterations=beta).astype(np.uint8)  #the sure background appear as 0 !!on purpose because ou them substract the sure foreground to this mask to get the unknown area"
    
    
    # Apply distance transform and threshold to get sure foreground
    dist_transform = cv.distanceTransform(binary_image, cv.DIST_L2, 3)
    _, sure_fg = cv.threshold(dist_transform, alpha * dist_transform.max(), 255, 0) #the sure foreground appear as 255
    sure_fg = np.uint8(sure_fg)  # Convert sure foreground to uint8 type for compatibility

    # Identify unknown regions by subtracting sure foreground from background
    unknown = cv.subtract(sure_bg, sure_fg)     #the unknown regions appears as 255

    # Marker labeling
    number_of_zones, connection_markers = cv.connectedComponents(sure_fg)
    # Add one to ensure background is 1, not 0
    connection_markers = connection_markers + 1
    # Mark the unknown regions as 0
    connection_markers[unknown == 255] = 0

    #connection_markers_display = cv.normalize(connection_markers, None, 0, 65535, cv.NORM_MINMAX).astype(np.uint16)
    connection_markers_display = np.copy(connection_markers).astype(np.uint16)
    connection_markers_display = cv.normalize(connection_markers, None, 65535/5, 65535, cv.NORM_MINMAX, cv.CV_16U)
    connection_markers_display[connection_markers_display == connection_markers_display.min()] = 0

    # Ensure single_image is in color (3-channel) format for watershed
    single_image_color = cv.cvtColor(single_image, cv.COLOR_GRAY2BGR)

    # Apply watershed algorithm
    markers = cv.watershed(single_image_color, connection_markers)
    markers = cv.normalize(markers, None, 0, 65535, cv.NORM_MINMAX, cv.CV_32S)

    # Mark boundaries in red
    single_image[markers == 0] = 255

    # Uncomment these lines if running in a local environment with OpenCV GUI support
    """
    cv.imshow("Binary Image", binary_image)
    cv.waitKey(0)
    cv.imshow("Sure Background", sure_bg)
    cv.imshow("Sure Foreground", sure_fg)
    cv.imshow("Unknown Regions", unknown)
    
    cv.imshow("connection markers", connection_markers_display)
    cv.waitKey(0)
    cv.imshow("Markers", cv.normalize(markers, None, 0, 65535, cv.NORM_MINMAX, cv.CV_16U))
    cv.waitKey(0)
    cv.imshow("single_image", single_image)
    
    cv.waitKey(0)
    cv.destroyAllWindows()
    """
    return single_image, connection_markers_display



def custom_watershed_algorithm(single_image, binary_image, sure_fg, sure_bg):
    ''' 
    Lets you use a watershed algorithm to color edges of zones (touching or not) black.
    
    Inputs: - single image: np.array ; is used for the "topography of your zones
            - binary_image: np.array ; is used to define where the objects are
            - sure_fg: np.array ; the sure foreground appear as 255
            - sure_bg: np.array ; the sure background appear as 0 !!on purpose because ou them substract the sure foreground to this mask to get the unknown area"

    Outputs: - modified input image
    '''
    # Define a kernel for morphological operations
    kernel = np.ones((3, 3), np.uint8)

    # Convert SimpleITK image to NumPy array UINT8
    #single_image = sitk.GetArrayFromImage(single_image)
    single_image = cv.normalize(single_image, None, 0, 255, cv.NORM_MINMAX, cv.CV_8U)
    binary_image = cv.normalize(binary_image, None, 0, 255, cv.NORM_MINMAX, cv.CV_8U)
    sure_fg = cv.normalize(sure_fg, None, 0, 255, cv.NORM_MINMAX, cv.CV_8U)
    sure_bg = cv.normalize(sure_bg, None, 0, 255, cv.NORM_MINMAX, cv.CV_8U)


    # Identify unknown regions by subtracting sure foreground from background
    unknown = cv.subtract(sure_bg, sure_fg)     #the unknown regions appears as 255

    # Marker labeling
    number_of_zones, connection_markers = cv.connectedComponents(sure_fg)
    # Add one to ensure background is 1, not 0
    connection_markers = connection_markers + 1
    # Mark the unknown regions as 0
    connection_markers[unknown == 255] = 0

    #connection_markers_display = cv.normalize(connection_markers, None, 0, 65535, cv.NORM_MINMAX).astype(np.uint16)
    connection_markers_display = np.copy(connection_markers).astype(np.uint16)
    connection_markers_display = cv.normalize(connection_markers, None, 65535/5, 65535, cv.NORM_MINMAX, cv.CV_16U)
    connection_markers_display[connection_markers_display == connection_markers_display.min()] = 0

    # Ensure single_image is in color (3-channel) format for watershed
    single_image_color = cv.cvtColor(single_image, cv.COLOR_GRAY2BGR)

    # Apply watershed algorithm
    markers = cv.watershed(single_image_color, connection_markers)
    markers = cv.normalize(markers, None, 0, 65535, cv.NORM_MINMAX, cv.CV_32S)

    # Mark boundaries in red
    single_image[markers == 0] = 255

    # Uncomment these lines if running in a local environment with OpenCV GUI support
    """
    cv.imshow("Binary Image", binary_image)
    cv.waitKey(0)
    cv.imshow("Sure Background", sure_bg)
    cv.imshow("Sure Foreground", sure_fg)
    cv.imshow("Unknown Regions", unknown)
    
    cv.imshow("connection markers", connection_markers_display)
    cv.waitKey(0)
    cv.imshow("Markers", cv.normalize(markers, None, 0, 65535, cv.NORM_MINMAX, cv.CV_16U))
    cv.waitKey(0)
    cv.imshow("single_image", single_image)
    
    cv.waitKey(0)
    cv.destroyAllWindows()
    """
    return single_image, connection_markers_display


#===========================================================================================================================
#============================================ function 9 ====================================================
#===========================================================================================================================


def detect_crack(images, max_crack_heigth, max_crack_width, max_relative_thickness):
    print("starting 3D convolution")

    class pixel:
        def __init__(self,found,value):
            self.found = found
            self.value = value

    #images = sitk.GetArrayFromImage(images)
    
    N = images.shape[0]  # Number of slices
    Y = images.shape[1]  # height of slices
    X = images.shape[2]  # width of slices
    start = 0
    #N=1400

    #max_crack_heigth = 60
    #max_crack_width = 40

    max_relative_thickness = 0.5

    I = (N-start)*X*Y
    i=0
    skip_next_pixel = False
    print(f"we need to analyse {I} pixels. Across {N} images, {Y} rows, {X} columns.")
    
    #sweep accross all pixels
    print("starting primary sweep")
    for n in range(start,N):                             
        loadingbar.main(i, I, bar_length=30)
        for x in range(0,X):
            skip_next_pixel = False
            for y in range(1,Y):
                i=i+1
                if images[n,y,x] != 0:
                    skip_next_pixel = False
                    continue
                if skip_next_pixel == True:
                    continue
                pixel_above = pixel(False, 0)
                pixel_below = pixel(False, 0)
                #print(f"working on image {n}, rows {y}, columns {x}.")
                for p in range(0, min(Y-y,y,max_crack_heigth)):             #look verticaly for the closest 2 pixels (1 above and 1 below)
                    skip_next_pixel = True
                    if pixel_above.found==False:
                        pixel_above.value = images[n,y+p,x]
                        if pixel_above.value!=0:
                            pixel_above.found = True
                    if pixel_below.found==False:
                        pixel_below.value = images[n,y-p,x]
                        if pixel_below.value!=0 :
                            pixel_below.found = True                        
                    
                    if pixel_above.found == True and pixel_below.found == True:
                        if pixel_below.value == pixel_above.value and pixel_above.value != 99:      #if you are in-between same pixels
                            break                                                                       #this pixel is NOT in a crack
                        elif pixel_below.value == pixel_above.value and pixel_above.value == 99:    #if you are in-between keratine pixels
                            skip_next_pixel = False                                                     #this pixel is in a crack
                            images[n,y,x] = 128
                            break
                        elif pixel_below.value != pixel_above.value:                                #if you are in-between different pixels
                            skip_next_pixel = False                                                     #this pixel is in a crack
                            images[n,y,x] = 128
                            break

    print(' ')
    CT_visualization_functions.browse_images(sitk.GetImageFromArray(images))
    print("starting cleaning loop")
    I = (N-start)*X
    i=0
    for n in range(0,N):        # this loop is for removing columns of crack pixels significantly longer than the horn above them
        #print(f"Working on image {n}...")
        loadingbar.main(i, I, bar_length=30)
        for x in range(0,X):
            column_pixel = np.array(images[n,:,x])
            i=i+1
            keratine_amount = np.count_nonzero(column_pixel == 99)
            crack_amount = np.count_nonzero(column_pixel == 128)

            if crack_amount > max_relative_thickness*keratine_amount:
                column_pixel[column_pixel==128] = 0
                images[n,:,x] = column_pixel
    I=(N-start)*X*Y
    i=0
    CT_visualization_functions.browse_images(sitk.GetImageFromArray(images))
    
    print(" ")
    print("starting secondary sweep")
    for n in range(start,N):
        #print(f"Working on image {n}...")
        loadingbar.main(i, I, bar_length=30)
        for x in range(0,X):
            skip_next_pixel = False                        #reset the skip pixel variable such that the first pixel in each column is not passed
            for y in range(0,Y):                           #with the three loop you go through all the pixels in the image stack
                i=i+1
                if images[n,y,x] != 0:                      #if pixel is non-zero, continue to the next pixel, but do not skip the next
                    skip_next_pixel = False
                    continue
                if skip_next_pixel == True:                 #if at the previous pixel, you defined that this pixel should be skipped, skip it
                    continue

                pixel_left = pixel(False, 0)    #setup variables
                pixel_right = pixel(False, 0)
                for k in range(0, min(X-x,x,max_crack_width)):          #look horizontaly around the main pixel, at 2 other pixels (1 left and 1 right), each iteration you look further away
                    skip_next_pixel = True                         #you start by assuming that the next pixel can be skipped

                    if pixel_left.found==False:                    #if the left pixel has not been found
                        pixel_left.value = images[n,y,x-k]
                        if pixel_left.value!=0:                          #check if this one could be it. aka is it not nul?
                            pixel_left.found = True                         #if yes, indicate that you found it
                            #print("left pixel found")

                    if pixel_right.found==False:                   #if the right pixel has not been found
                        pixel_right.value = images[n,y,x+k]
                        if pixel_right.value!=0:                          #check if this one could be it. aka is it not nul?
                            pixel_right.found = True                         #if yes, indicate that you found it
                            #print("right pixel found")
                        

                    if pixel_left.found == True and pixel_right.found == True:         #if both left and right pixels have been found
                        #print("looking at one pixel")
                        skip_next_pixel = False                                           #do not skip next pixel
                        if pixel_right.value==128 or pixel_left.value==128:             #check if the main pixel is in-between already found in crack pixel and another pixel of any color
                            images[n,y,x] = 128                                              #if yes, this pixel is in a crack: color it
                            break
                        elif pixel_right.value!=128 and pixel_left.value!=128 and pixel_right.value!=pixel_left.value:                  #elif, the pixel is in-between bone and keratine
                            if k<max_crack_width/3:                                                                                         #if the bone and keratin are really close
                                images[n,y,x] = 128                                                                                             #then this pixel is bone in a crack
                                break
                            else:                                                                                                           #otherwise, this pixel is probably not in a crack
                                break
                        else:
                            break

    
    print("stuff done")
    return images






#===========================================================================================================================
#============================================ function 10 ====================================================
#===========================================================================================================================



def find_small_holes(binary_image, max_hole_size):
    """
    find small holes from a binary image with foreground=255 (uint8 format).

    Parameters:
    - binary_image: sitk.Image
        A binary image (foreground=255, background=0).
    - max_hole_size: int
        is actual the "rank" of the biggest hole to fill: 0 is the foreground of your image, 1 your biggest hole, 2 your second biggest hole, 3 ......

    Returns:
    - sitk.Image: Binary image with small holes (foreground=255, background=0).
    """
    # Rescale image to binary (foreground=1, background=0)
    binary_image_rescaled = sitk.Cast(binary_image > 0, sitk.sitkUInt8)
    
    # Invert the binary image
    inverted_image = sitk.InvertIntensity(binary_image_rescaled, maximum=1)
    
    # Connected component analysis on the inverted image
    connected_components = sitk.ConnectedComponent(inverted_image)  #create a list of all islands
    print(f"{sitk.GetArrayFromImage(connected_components).max()} holes found")
          
    if sitk.GetArrayFromImage(connected_components).max() < max_hole_size:
        print(f"error: hole size too big. maximum should be {sitk.GetArrayFromImage(connected_components).max()} and you entered {max_hole_size}...")
        return
    
    # Relabel components by size and filter based on size
    relabeled_components = sitk.RelabelComponent(connected_components, sortByObjectSize=True)   #re-order the holes by size: the small the holes, the higher its rank

    #extract only the small holes
    small_holes = sitk.BinaryThreshold(                                                  #find all the holes above the thresshold. They have a value of 0 and outside a value of 1  
        relabeled_components,
        lowerThreshold=max_hole_size,           
        upperThreshold=int(sitk.GetArrayFromImage(connected_components).max()),   # get all the other holes
        insideValue=1,
        outsideValue=0
    )

    # Rescale back to uint8 format (foreground=255)
    final_image = sitk.Cast(small_holes, sitk.sitkUInt8) * 255
    
    return final_image
