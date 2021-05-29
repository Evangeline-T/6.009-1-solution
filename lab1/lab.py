#!/usr/bin/env python3

import math

from PIL import Image as Image

# NO ADDITIONAL IMPORTS ALLOWED!


def get_pixel(image, x, y):
    return image['pixels'][x + y*image['width']]                    #Gets pixel by going down array and then moving across


def get_correlated_pixel(image, x, y):
    if x < 0:                                                       #If x is less than 0, set x = 0
        x = 0
    elif x >= image['width']:                                       #If x is the same value as width or greater, it is not in the picture, so set it to the higest x coordinate
        x = image['width'] - 1
    if y < 0:                                                       #If y is less than 0, set y = 0
        y = 0
    elif y >= image['height']:                                      #If y is greater than or equal to height, it is no longer in the picture, so set it to the lowest y  coordinate    
        y = image['height'] - 1
    return get_pixel(image, x, y)                                   #Apply get_pixel on the updated x and y if x and y were updated, else call get_pixel on the original x, y

def set_pixel(image, x, y, c):
    image['pixels'][x + y*image['width']] = c                       #Gets pixel and lets it = c


def apply_per_pixel(image, func):
    result = {                                                      #Creates new pixel
        'height': image['height'],
        'width': image['width'],
        'pixels': image['pixels'][:],
    }
    for x in range(image['width']):
        for y in range(image['height']):
            color = get_pixel(image, x, y)
            newcolor = func(color)
            set_pixel(result, x, y, newcolor)                       #Sets colour of pixel to new colour
    return result


def inverted(image):
    return apply_per_pixel(image, lambda c: 255-c)                  #Turn 256 to 255


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
    result = {'height' : image['height'], 'width' : image['width'], 'pixels' : image['pixels'][:]}                  #Create new pixel
    new_kernel = []
    for j in kernel:
        for i in j:
            new_kernel.append(i)                                                                                    #Turn 2d kernel into 1d array
    
    for x in range(image['width']):
        for y in range(image['height']):                                                                            #Iterate over each pixel
            count = 0                                                                                               #This keeps count of what the correlated pixel will sum to
            index = 0                                                                                               #This keeps count of how far into the kernel we go
            for b in range(0, len(kernel)):
                for a in range(0, len(kernel)):                                                                     #We move to the coordinate to the top left of the pixel we are on corresponding to the size of the pixel
                    new_pixel = get_correlated_pixel(image, x - len(kernel)//2 + a, y - len(kernel)//2 + b)         #We go left to right, then down, getting to each pixel around the centre pixel
                    count += new_pixel * new_kernel[index]                                                          #Multiply the pixel we are on with the correct value from kernel, and add it to count
                    index += 1                                                                                      #Add 1 to the index so that we go to the next value in kernel
            set_pixel(result, x, y, count)                                                                          #Set the pixel in result to the correlated pixel with value of count, and then reset count and index to 0
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
    for pixel in range(0, len(image['pixels'])):                                                                    #Index through each pixel
        image['pixels'][pixel] = round(image['pixels'][pixel])                                                      #Round each pixel
        if image['pixels'][pixel] < 0:
            image['pixels'][pixel] = 0                                                                              #Any pixel less that 0 is now equal to 0
        if image['pixels'][pixel] > 255:
            image['pixels'][pixel] = 255                                                                            #Any pixel greater than 255 is now equal to 255
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
    result = {'height' : image['height'], 'width' : image['width'], 'pixels' : image['pixels'][:]}                  #Create new pixel
    x = 1/(n**2)                                                                                                    #Each value of kernel will sum to n, and since there are n^2 values, set each value to 1/n^2    
    kernel = []
    for i in range(0, n):
        kernel.append(n*[x])                                                                                        #Append empty kernel with lists of values to create 2d kernel
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
    result = {'height' : image['height'], 'width' : image['width'], 'pixels' : image['pixels'][:]}                  #Create new pixel with copied values from original 
    
    kx = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
    ky = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]                                                                       #Create desired kernels
    
    result_kx = correlate(image, kx)
    result_ky = correlate(image, ky)                                                                                #Correlated the image on both kernels serparately
    
    for y in range(image['height']):
        for x in range(image['width']):                                                                             #Index into each pixel of the copy of the original    
            pixel_x = get_correlated_pixel(result_kx, x, y)
            pixel_y = get_correlated_pixel(result_ky, x, y)                                                         #Get the corresponding correlated pixels from the correlated images
            set_pixel(result, x, y, round((pixel_x**2 + pixel_y**2)**(1/2)))                                        #Set the pixel from the copied image to the magnitude of the 2 correlated pixels
    return round_and_clip_image(result)                                                                             #Turn the image into a valid one
# HELPER FUNCTIONS FOR LOADING AND SAVING IMAGES

def load_image(filename):
    """
    Loads an image from the given file and returns a dictionary
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_image('test_images/cat.png')
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


def save_image(image, filename, mode='PNG'):
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
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place for
    # generating images, etc.
    pigbird = load_image('test_images/pigbird.png')
    pigbird = correlate(pigbird, [[0, 0, 0, 0, 0, 0, 0, 0, 0],
                                  [0, 0, 0, 0, 0, 0, 0, 0, 0],
                                  [1, 0, 0, 0, 0, 0, 0, 0, 0],
                                  [0, 0, 0, 0, 0, 0, 0, 0, 0],
                                  [0, 0, 0, 0, 0, 0, 0, 0, 0],
                                  [0, 0, 0, 0, 0, 0, 0, 0, 0],
                                  [0, 0, 0, 0, 0, 0, 0, 0, 0],
                                  [0, 0, 0, 0, 0, 0, 0, 0, 0],
                                  [0, 0, 0, 0, 0, 0, 0, 0, 0]])
    save_image(pigbird, 'pigbird.png')
    
    
    cat = load_image('test_images/cat.png')
    cat = blurred(cat, 5)
    save_image(cat, 'cat.png')


    python = load_image('test_images/python.png')
    python = sharpened(python, 11)
    save_image(python, 'python.png')
    
    construct = load_image('test_images/construct.png')
    construct = edges(construct)
    save_image(construct, 'construct.png')