# =======================================================================================================
# ========================================= rainbow colors =============================================
# =======================================================================================================

def rainbow_colors(event):
    global images_rgb, images, slice
    global fig_rainbow,r,g,b,rgb_scale
    start_time_rainbow_colors = time.time() 
    # Ensure the condition checks the values properly
    if (images_rgb[:,:,:,0] == images_rgb[:,:,:,1]).all():
        logging.info("Changing color set to rainbow")
        rgb_scale = np.copy(images_rgb[:,:,:,0], dtype=np.uint8)

        if not plt.fignum_exists(fig_histo.number):     # creating the rainbow scale interaction window
            global rainbow_slider_min, rainbow_slider_max, button_apply_rainbow_all
            print('opening sliders window')
            fig_rainbow, ax_rainbow = plt.subplots(figsize=(10, 1))
            ax_rainbow.axis('off')
            ax_rainbow_min = plt.axes([0.3, 0.6, 0.6, 0.1], facecolor='lightgrey')  # left, bottom, width, height
            rainbow_slider_min = Slider(ax_rainbow_min, 'min rainbow value', 0, 255, valinit=0, valstep=1)

            ax_rainbow_max = plt.axes([0.3, 0.3, 0.6, 0.1], facecolor='lightgrey')  # left, bottom, width, height
            rainbow_slider_max = Slider(ax_rainbow_max, 'max rainbow value', 0, 255, valinit=255, valstep=1)

            ax_button_apply_rainbow_all = plt.axes([0.025, 0.35, 0.05, 0.3])     # left, bottom, width, height
            button_apply_rainbow_all = Button(ax_button_apply_rainbow_all, 'Apply all')
            button_apply_rainbow_all.color = "green"
            button_apply_rainbow_all.on_clicked(lambda event: apply_rainbow_all(event))
            
            plt.show()
            rainbow_slider_min.on_changed(lambda event: update_rainbow(event,'min_slider'))
            rainbow_slider_max.on_changed(lambda event: update_rainbow(event,'max_slider'))
        
    else : 
        del rgb_scale, r, g, b, rainbow_slider_min, rainbow_slider_max, button_apply_rainbow_all
        logging.info("changing colorset to grey-scale")
        plt.close(fig_rainbow)
        make_greyscale_inRGB(images)
        del fig_rainbow
    
    logging.debug(f"new color scale applied in {time.time() - start_time_rainbow_colors} seconds.")

def calculate_rainbow_masks(min_rainbow,max_rainbow,rgb_scale):
    increment_rainbow = (max_rainbow-min_rainbow)/4
    mask_0_25 = np.array((rgb_scale >= min_rainbow) & (rgb_scale < increment_rainbow), dtype=np.bool)
    mask_25_50 = np.array((rgb_scale >= increment_rainbow) & (rgb_scale < increment_rainbow*2), dtype=np.bool)
    mask_50_75 = np.array((rgb_scale >= increment_rainbow*2) & (rgb_scale < increment_rainbow*3), dtype=np.bool)
    mask_75_100 = np.array((rgb_scale >= increment_rainbow*3) & (rgb_scale <= max_rainbow), dtype=np.bool)
    return mask_0_25, mask_25_50, mask_50_75, mask_75_100

def update_rainbow(event,event_name):
    global rgb_scale, images_rgb,r,g,b, slice
    min_val = rainbow_slider_min.val
    max_val = rainbow_slider_max.val

    r_temp = r[slice,:,:]
    g_temp = g[slice,:,:]
    b_temp = b[slice,:,:]
    scale_temp = rgb_scale[slice,:,:]

    # Reapply the rainbow mapping but restrict the values according to the sliders
    mask_0_25, mask_25_50, mask_50_75, mask_75_100 = calculate_rainbow_masks(min_rainbow,max_rainbow,scale_temp)
    quarter_rainbow = (max_rainbow-min_rainbow)/4

    multiplier = 255 / quarter_rainbow
    new_rgbscale = scale_temp - min_val
    r_temp[mask_0_25] = (new_rgbscale[mask_0_25]) * multiplier
    g_temp[mask_0_25] = 255
    del mask_0_25

    multiplier = (quarter_rainbow + min_val) * 255
    r_temp[mask_25_50] = 255
    g_temp[mask_25_50] = 255 - (new_rgbscale[mask_25_50] - quarter_rainbow) * multiplier

    r_temp[mask_50_75] = 255
    b_temp[mask_50_75] = (new_rgbscale[mask_50_75] - 2*quarter_rainbow) * multiplier
    del mask_50_75

    r_temp[mask_75_100] = 255 - (new_rgbscale[mask_75_100] - 3*quarter_rainbow) * multiplier
    b_temp[mask_75_100] = 255
    del mask_75_100, new_rgbscale

    outside_mask = (not mask_0_25) & (not mask_25_50) & (not mask_50_75) & (not mask_75_100)
    r_temp[outside_mask] = scale_temp[outside_mask]
    g_temp[outside_mask] = scale_temp[outside_mask]
    b_temp[outside_mask] = scale_temp[outside_mask]

    # Combine channels into images_rgb
    images_rgb[slice,:,:,0] = r_temp  # Red channel
    images_rgb[slice,:,:,1] = g_temp  # Green channel
    images_rgb[slice,:,:,2] = b_temp  # Blue channel

    update_plot(slice)

def apply_rainbow_all(event):
    global rgb_scale, images_rgb,r,g,b, slice
    min_val = rainbow_slider_min.val
    max_val = rainbow_slider_max.val

    # Reapply the rainbow mapping but restrict the values according to the sliders
    mask_0_25, mask_25_50, mask_50_75, mask_75_100 = calculate_rainbow_masks(min_rainbow,max_rainbow,rgb_scale)
    quarter_rainbow = (max_rainbow-min_rainbow)/4

    multiplier = 255 / quarter_rainbow
    new_rgbscale = rgb_scale - min_val
    r[mask_0_25] = (new_rgbscale[mask_0_25]) * multiplier
    g[mask_0_25] = 255
    del mask_0_25

    multiplier = (quarter_rainbow + min_val) * 255
    r[mask_25_50] = 255
    g[mask_25_50] = 255 - (new_rgbscale[mask_25_50] - quarter_rainbow) * multiplier

    r[mask_50_75] = 255
    b[mask_50_75] = (new_rgbscale[mask_50_75] - 2*quarter_rainbow) * multiplier
    del mask_50_75

    r[mask_75_100] = 255 - (new_rgbscale[mask_75_100] - 3*quarter_rainbow) * multiplier
    b[mask_75_100] = 255
    del mask_75_100, new_rgbscale

    outside_mask = (not mask_0_25) & (not mask_25_50) & (not mask_50_75) & (not mask_75_100)
    r[outside_mask] = rgb_scale[outside_mask]
    g[outside_mask] = rgb_scale[outside_mask]
    b[outside_mask] = rgb_scale[outside_mask]

    # Combine channels into images_rgb
    images_rgb[:,:,:,0] = r  # Red channel
    images_rgb[:,:,:,1] = g  # Green channel
    images_rgb[:,:,:,2] = b  # Blue channel

    update_plot(slice)

