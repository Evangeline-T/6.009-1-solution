#!/usr/bin/env python3

# NO ADDITIONAL IMPORTS!
# (except in the last part of the lab; see the lab writeup for details)
import math
from PIL import Image


# VARIOUS FILTERS

def get_pixel(image, x, y):
    return image['pixels'][x + y*image['width']]                    


def get_correlated_pixel(image, x, y):
    if x < 0:                                                       
        x = 0
    elif x >= image['width']:                                       
        x = image['width'] - 1
    if y < 0:                                                       
        y = 0
    elif y >= image['height']:                                          
        y = image['height'] - 1                                 
    return get_pixel(image, x, y)                                                                                #Fix out of bounds pixels    

def set_pixel(image, x, y, c):
    image['pixels'][x + y*image['width']] = c                       


def apply_per_pixel(image, func):
    result = {                                                      
        'height': image['height'],
        'width': image['width'],
        'pixels': image['pixels'][:],
    }
    for x in range(image['width']):
        for y in range(image['height']):
            color = get_pixel(image, x, y)
            newcolor = func(color)
            set_pixel(result, x, y, newcolor)                       
    return result


def inverted(image):
    return apply_per_pixel(image, lambda c: 255-c)                                                                  #Turn 256 to 255



# HELPER FUNCTIONS

def correlate(image, kernel):
    """
    Compute the result of correlating the given image with the given kernel.

    The output of this function should have the same form as a 6.009 image (a
    dictionary with 'height', 'width', and 'pixels' keys), but its pixel values
    do not necessarily need to be in the range [0,255], nor do they need to be
    integers (they should not be clipped or rounded at all).

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    
    The kernel is a 2D array: a list of lists.
    """
    result = {'height' : image['height'], 'width' : image['width'], 'pixels' : image['pixels'][:]}                  
    new_kernel = []
    for j in kernel:
        for i in j:
            new_kernel.append(i)                                                                                    #Turn 2d kernel into 1d array
    
    for x in range(image['width']):
        for y in range(image['height']):                                                                           
            correlated_pixel_sum = 0                                                                                #This keeps count of what the correlated pixel will sum to
            kernel_index = 0                                                                                        #This keeps count of how far into the kernel we go
            for b in range(0, len(kernel)):
                for a in range(0, len(kernel)):                                                                     #We move to the coordinate to the top left of the pixel we are on corresponding to the size of the pixel
                    new_pixel = get_correlated_pixel(image, x - len(kernel)//2 + a, y - len(kernel)//2 + b)         #We go left to right, then down, getting to each pixel around the centre pixel
                    correlated_pixel_sum += new_pixel * new_kernel[kernel_index]                                    #Multiply the pixel we are on with the correct value from kernel, and add it to count
                    kernel_index += 1                                                                               #Add 1 to the index so that we go to the next value in kernel
            set_pixel(result, x, y, correlated_pixel_sum)                                                           
    return result
    
def round_and_clip_image(image):
    """
    Given a dictionary, ensure that the values in the 'pixels' list are all
    integers in the range [0, 255].

    All values should be converted to integers using Python's `round` function.

    Any locations with values higher than 255 in the input should have value
    255 in the output; and any locations with values lower than 0 in the input
    should have value 0 in the output.
    """
    for pixel in range(0, len(image['pixels'])):                                                                    
        image['pixels'][pixel] = round(image['pixels'][pixel])                                                      
        if image['pixels'][pixel] < 0:
            image['pixels'][pixel] = 0                                                                              
        if image['pixels'][pixel] > 255:
            image['pixels'][pixel] = 255                                                                            #All out of bouunds pixels are now set to 0 or 255
    return image


# FILTERS

def blurred(image, n):
    """
    Return a new image representing the result of applying a box blur (with
    kernel size n) to the given input image.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    """
    # first, create a representation for the appropriate n-by-n kernel (you may
    # wish to define another helper function for this)
    x = 1/(n**2)
    kernel = []
    for i in range(0, n):
        kernel.append(n*[x])
    # then compute the correlation of the input image with that kernel
    result = correlate(image, kernel)

    # and, finally, make sure that the output is a valid image (using the
    # helper function from above) before returning it.
    result = round_and_clip_image(result)
    
    return result



def sharpened(image, n):
    """
    Returns a new image representing the result of of subtracting an "unsharp"
    (blurred) version of the image from a scaled version of the original image.
   
    This creates a new image rather than mutating the original.
    """
    result = {'height' : image['height'], 'width' : image['width'], 'pixels' : image['pixels'][:]}                  
    x = 1/(n**2)                                                                                                    #Each value of kernel will sum to n, and since there are n^2 values, set each value to 1/n^2    
    kernel = []
    for i in range(0, n):
        kernel.append(n*[x])                                                                                        
    blurred_image = correlate(image, kernel)                                                                        #Create blurred image with appropriate kernel
    scaled_image = apply_per_pixel(image, lambda c: 2*c)                                                            #Create scaled image using earlier function and multiplying each pixel by 2
    for y in range(result['height']):
        for x in range(result['width']):
            blurred_pixel = get_correlated_pixel(blurred_image, x, y)
            scaled_pixel = get_correlated_pixel(scaled_image, x, y)
            set_pixel(result, x, y, scaled_pixel - blurred_pixel)                                                   #Get the same indexed pixel from both images and subtract to create sharpened pixel, which is put into result
    return round_and_clip_image(result)                                                                             #Return result in correct format
    

def edges(image):
    """
    Returns the edges of an image clearly visible.
    Does not mutate the original image, but returns a new result
    """
    result = {'height' : image['height'], 'width' : image['width'], 'pixels' : image['pixels'][:]}                   
    
    kx = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
    ky = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]                                                                       
    
    result_kx = correlate(image, kx)
    result_ky = correlate(image, ky)                                                                                
    
    for y in range(image['height']):
        for x in range(image['width']):                                                                                 
            pixel_x = get_correlated_pixel(result_kx, x, y)
            pixel_y = get_correlated_pixel(result_ky, x, y)                                                         
            set_pixel(result, x, y, round((pixel_x**2 + pixel_y**2)**(1/2)))                                        #Set the pixel from the copied image to the magnitude of the 2 correlated pixels
    return round_and_clip_image(result)


def get_red_pixels(image):
    """
    Takes in an image, and returns a similar image with only red pixels
    """
    red_image = {'height' : image['height'], 'width' : image['width'], 'pixels' : image['pixels'][:]}
    for x in range(image['width']):
        for y in range(image['height']):
            red_pixel = get_pixel(image, x, y)[0]                                                                   #We index into each tuple to its first element, which will be the red pixel.
            set_pixel(red_image, x, y, red_pixel)
    return red_image

def get_green_pixels(image):
    """
    Takes in an image, and returns a similar image with only green pixels
    """
    green_image = {'height' : image['height'], 'width' : image['width'], 'pixels' : image['pixels'][:]}
    for x in range(image['width']):
        for y in range(image['height']):
            green_pixel = get_pixel(image, x, y)[1]                                                                 #We index into each tuple to its second element, which will be the green pixel.
            set_pixel(green_image, x, y, green_pixel)
    return green_image


def get_blue_pixels(image):
    """
    Takes in an image, and returns a similar image with only blue pixels
    """
    blue_image = {'height' : image['height'], 'width' : image['width'], 'pixels' : image['pixels'][:]}
    for x in range(image['width']):
        for y in range(image['height']):
            blue_pixel = get_pixel(image, x, y)[2]                                                                   #We index into each tuple to its last element, which will be the blue pixel.       
            set_pixel(blue_image, x, y, blue_pixel)
    return blue_image


def color_filter_from_greyscale_filter(filt):
    """
    Given a filter that takes a greyscale image as input and produces a
    greyscale image as output, returns a function that takes a color image as
    input and produces the filtered color image.
    """
    def colour_filter(image):
        red_image = get_red_pixels(image)
        green_image = get_green_pixels(image)
        blue_image = get_blue_pixels(image)
        
        filtered_red_image = filt(red_image)
        filtered_green_image = filt(green_image)
        filtered_blue_image = filt(blue_image)
        
        filtered_image = {'height' : image['height'], 'width' : image['width'], 'pixels' : image['pixels'][:]}
        for x in range(image['width']):
            for y in range(image['height']):
                filtered_red_pixel = get_pixel(filtered_red_image, x, y)
                filtered_green_pixel = get_pixel(filtered_green_image, x, y)
                filtered_blue_pixel = get_pixel(filtered_blue_image, x, y)
                set_pixel(filtered_image, x, y, (filtered_red_pixel,) + (filtered_green_pixel,) + (filtered_blue_pixel,)) #We add each pixel, which has been filtered, into a valid tuple to create a valid image
        return filtered_image
    return colour_filter


def make_blur_filter(n):
    """
    Creates a blurry filter of a fixed kernel that can be used with greyscale image and coloured
    """
    def blurry_filter(image):
        return blurred(image, n)
    return blurry_filter


def make_sharpen_filter(n):
    """
    Creates a sharpened filter of a fixed kernel that can be used with any iamge
    """
    def sharpened_filter(image):
        return sharpened(image, n)
    return sharpened_filter


def filter_cascade(filters):
    """
    Given a list of filters (implemented as functions on images), returns a new
    single filter such that applying that filter to an image produces the same
    output as applying each of the individual ones in turn.
    """
    def cascaded_image(image):
        for fil in filters:
            image = fil(image)
        return image
    return cascaded_image
        

# SEAM CARVING

# Main Seam Carving Implementation

def seam_carving(image, ncols):
    """
    Starting from the given image, use the seam carving technique to remove
    ncols (an integer) columns from the image.
    """
    
    result = {'height' : image['height'], 'width' : image['width'], 'pixels' : image['pixels'][:]}
    for i in range(ncols):
        grey_image = greyscale_image_from_color_image(result)
    
        energy_image = compute_energy(grey_image)
    
        energy_map = cumulative_energy_map(energy_image)
    
        removed_indices = minimum_energy_seam(energy_map)
    
        result = image_without_seam(result, removed_indices)
    return result
    
    
# Optional Helper Functions for Seam Carving

def greyscale_image_from_color_image(image):
    """
    Given a color image, computes and returns a corresponding greyscale image.

    Returns a greyscale image (represented as a dictionary).
    """
    
    red_image = get_red_pixels(image)
    green_image = get_green_pixels(image)
    blue_image = get_blue_pixels(image)
    
    greyscale_image = {'height' : image['height'], 'width' : image['width'], 'pixels' : image['pixels'][:]}
    for x in range(image['width']):
        for y in range(image['height']):
            red_pixel = get_pixel(red_image, x, y)
            green_pixel = get_pixel(green_image, x, y)
            blue_pixel = get_pixel(blue_image, x, y)
            set_pixel(greyscale_image, x, y, round((0.299*red_pixel)+(0.587*green_pixel)+(0.114*blue_pixel)))               #Multiply each coloured pixel by the appropriate number, and add together to create a greyscale pixel for the new picture
    return greyscale_image

def compute_energy(grey):
    """
    Given a greyscale image, computes a measure of "energy", in our case using
    the edges function from last week.

    Returns a greyscale image (represented as a dictionary).
    """
    return edges(grey)


def cumulative_energy_map(energy):
    """
    Given a measure of energy (e.g., the output of the compute_energy
    function), computes a "cumulative energy map" as described in the lab 2
    writeup.

    Returns a dictionary with 'height', 'width', and 'pixels' keys (but where
    the values in the 'pixels' array may not necessarily be in the range [0,
    255].
    """
    cumulative_energy_map = {'height' : energy['height'], 'width' : energy['width'], 'pixels' : energy['pixels'][:]}
    w = energy['width']
    for y in range(energy['height']):
        for x in range(energy['width']):
            if y == 0:
                set_pixel(cumulative_energy_map, x, y, energy['pixels'][x])                                                 #For the top row of pixels, we leave them be
                continue
            if x == 0:
                set_pixel(cumulative_energy_map, x, y, get_pixel(energy, x, y) + 
                          min(get_pixel(cumulative_energy_map, x, y - 1), get_pixel(cumulative_energy_map, x + 1, y - 1)))  #For each pixel on the left most side, we find the min of the one directly below and below on the right to add to the pixel
                continue
            if x == w - 1:
                set_pixel(cumulative_energy_map, x, y, get_pixel(energy, x, y) + 
                          min(get_pixel(cumulative_energy_map, x, y - 1), get_pixel(cumulative_energy_map, x - 1, y - 1)))  #For each pixel on the right most side, we find the min of the one directly below and below on the left to add to the pixel
                continue
            set_pixel(cumulative_energy_map, x, y, get_pixel(energy, x, y) + 
                      min(get_pixel(cumulative_energy_map, x - 1, y - 1),  get_pixel(cumulative_energy_map, x, y - 1),      #For the other general pixels, we find the min of the 3 below to add to the pixel
                          get_pixel(cumulative_energy_map, x + 1, y - 1)))
    return cumulative_energy_map

def minimum_energy_seam(cem):
    """
    Given a cumulative energy map, returns a list of the indices into the
    'pixels' list that correspond to pixels contained in the minimum-energy
    seam (computed as described in the lab 2 writeup).
    """
    h = cem['height']
    w = cem['width']
    
    to_be_removed = [0]                                                                                                     #This will be a list of each index from each row, treating the beginnning of each row at index 0, of the image that we are going to remove
    
    for x in range(0 , w):
        if get_pixel(cem, x, h - 1) < get_pixel(cem, to_be_removed[0], h - 1):                                              #We find the x coordinate of the  smallest element in the bottom row of pixels
            to_be_removed[0] = x
    for y in range(h - 1, 0, -1):
        index = to_be_removed[-1] + 1                                                                                       #We analyse the three pixels above by beginning with the one on the right, hence adding 1 to the current index
        j = 3
        
        if (index == w):                                                                                                    #If we are at the the right boundary, we set j = 2 so we don't look at an invalid coordinate when making comparisons, and we assume the coordinate above is the smallest
            index -= 1
            j = 2
        
        to_be_removed.append(index)                                                                                         #We append the current x coordinate to to_be_removed, but this can change after comparisons  
        
        for i in range(1, j):
            if index - i >= 0:                                                                                              #This conditions ensures we don't index out of the picture to the left
                is_larger = get_pixel(cem, index - i, y - 1) <= get_pixel(cem, to_be_removed[-1], y - 1)  
                if is_larger:                                                                                               #If the coordinate to the left is smaller, we change the current corresponding value in to_be_removed to that x coordinate, and continue comparing
                     to_be_removed[-1] = index - i                      
    
    for i in range(h):
        to_be_removed[i] = to_be_removed[i] + (h - 1 - i)*w                                                                 #To turn the x coordinates into the correct indices, we add the corret multiple of width, and we return a list in reverse order
    return to_be_removed

def image_without_seam(image, seam):
    """
    Given a (color) image and a list of indices to be removed from the image,
    return a new image (without modifying the original) that contains all the
    pixels from the original image except those corresponding to the locations
    in the given list.
    """
    result = {'height' : image['height'], 'width' : image['width'], 'pixels' : image['pixels'][:]}
    for i in range(0, len(seam)):
        del result['pixels'][seam[i]]                                                                                       #We delete the pixels starting from the right, this ensures that the indexing of all the pixels before the one we deleted does not change
    result['width'] = result['width'] - 1
    return result
    
def colour_boost(image, colour, factor):
    """
    For a certain colour r,g or b, if selected.a new image will return
    of the original but boosted in that colour. We do this by dividing the pixel 
    of each other colour by a factor.
    Note that colour must be a string
    """
    result = {'height' : image['height'], 'width' : image['width'], 'pixels' : image['pixels'][:]} 
    red_image = get_red_pixels(result)
    green_image = get_green_pixels(result)
    blue_image = get_blue_pixels(result)
    
    for x in range(image['width']):
            for y in range(image['height']):
                red_pixel = get_pixel(red_image, x, y)
                green_pixel = get_pixel(green_image, x, y)
                blue_pixel = get_pixel(blue_image, x, y)
                if colour == 'r':
                    set_pixel(result, x, y, (red_pixel,) + (green_pixel//factor,) + (blue_pixel//factor,))                 #For whatever the user input, we divide the other coloured pixels by the factor, and recombine to create a colour boosted image
                if colour == 'g':
                    set_pixel(result, x, y, (red_pixel//factor,) + (green_pixel,) + (blue_pixel//factor,))
                if colour == 'b':
                    set_pixel(result, x, y, (red_pixel//factor,) + (green_pixel//factor,) + (blue_pixel,))
    return result

# HELPER FUNCTIONS FOR LOADING AND SAVING COLOR IMAGES

def load_color_image(filename):
    """
    Loads a color image from the given file and returns a dictionary
    representing that image.

    Invoked as, for example:
       i = load_color_image('test_images/cat.png')
    """
    with open(filename, 'rb') as img_handle:
        img = Image.open(img_handle)
        img = img.convert('RGB')  # in case we were given a greyscale image
        img_data = img.getdata()
        pixels = list(img_data)
        w, h = img.size
        return {'height': h, 'width': w, 'pixels': pixels}


def save_color_image(image, filename, mode='PNG'):
    """
    Saves the given color image to disk or to a file-like object.  If filename
    is given as a string, the file type will be inferred from the given name.
    If filename is given as a file-like object, the file type will be
    determined by the 'mode' parameter.
    """
    out = Image.new(mode='RGB', size=(image['width'], image['height']))
    out.putdata(image['pixels'])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


def load_greyscale_image(filename):
    """
    Loads an image from the given file and returns an instance of this class
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_greyscale_image('test_images/cat.png')
    """
    with open(filename, 'rb') as img_handle:
        img = Image.open(img_handle)
        img_data = img.getdata()
        if img.mode.startswith('RGB'):
            pixels = [round(.299 * p[0] + .587 * p[1] + .114 * p[2])
                      for p in img_data]
        elif img.mode == 'LA':
            pixels = [p[0] for p in img_data]
        elif img.mode == 'L':
            pixels = list(img_data)
        else:
            raise ValueError('Unsupported image mode: %r' % img.mode)
        w, h = img.size
        return {'height': h, 'width': w, 'pixels': pixels}


def save_greyscale_image(image, filename, mode='PNG'):
    """
    Saves the given image to disk or to a file-like object.  If filename is
    given as a string, the file type will be inferred from the given name.  If
    filename is given as a file-like object, the file type will be determined
    by the 'mode' parameter.
    """
    out = Image.new(mode='L', size=(image['width'], image['height']))
    out.putdata(image['pixels'])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


if __name__ == '__main__':
    # cat = load_color_image('test_images/cat.png')
    # inverted_colour = color_filter_from_greyscale_filter(inverted)
    # inverted_cat = inverted_colour(cat)
    # save_color_image(inverted_cat, 'inverted_cat.png', mode='PNG')
    
    # blurry9 = color_filter_from_greyscale_filter(make_blur_filter(9))
    # python = load_color_image('test_images/python.png')
    # blurry_python = blurry9(python)
    # save_color_image(blurry_python, 'blurry_python.png')
    
    # sharpened7 = color_filter_from_greyscale_filter(make_sharpen_filter(7))
    # sparrowchick = load_color_image('test_images/sparrowchick.png')
    # sharpened_sparrowchick = sharpened7(sparrowchick)
    # save_color_image(sharpened_sparrowchick, 'sharpened_sparrowchick.png')
    
    # filter1 = color_filter_from_greyscale_filter(edges)
    # filter2 = color_filter_from_greyscale_filter(make_blur_filter(5))
    # filt = filter_cascade([filter1, filter1, filter2, filter1])
    
    # frog = load_color_image('test_images/frog.png')
    # cascaded_frog = filt(frog)
    # save_color_image(cascaded_frog, 'cascaded_frog.png')
    
    # two_cats = load_color_image('test_images/twocats.png')
    # seamed_cats = seam_carving(two_cats, 100)
    # save_color_image(seamed_cats, 'seamed_cats.png')
    
    # two_cats = load_color_image('test_images/twocats.png')
    # red_boosted_cats = colour_boost(two_cats, 'r', 200)
    # save_color_image(red_boosted_cats, 'red_boosted_cats.png')
    
    # two_cats = load_color_image('test_images/twocats.png')
    # green_boosted_cats = colour_boost(two_cats, 'g', 56)
    # save_color_image(green_boosted_cats, 'green_boosted_cats.png')
    
    # two_cats = load_color_image('test_images/twocats.png')
    # blue_boosted_cats = colour_boost(two_cats, 'b', 10000)
    # save_color_image(blue_boosted_cats, 'blue_boosted_cats.png')
    
    pass
    

    