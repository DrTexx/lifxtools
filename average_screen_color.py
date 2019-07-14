#!/usr/bin/env python3

# change all lifx globes to an average of the colors on-screen
# based on the excellent LifxLAN library https://github.com/mclarkk/lifxlan
# adapted to python3 and improved upon from the screenlifx example script https://github.com/MarcoPon/screenlifx

# note:
# programs such as Flux or other 'Night Light' alternatives may impact colours.
# I can confirm this is the case for Night Light in the Gnome flavour of Debian 10 Buster.

from lifxtools import return_interface, get_lights, list_lights
from mss import mss
from PIL import Image
import time, os, colorsys

# static options
fade_modes = {'game': 0, 'movie': 150, 'desktop': 300}

# preferences
factor = 0.75
fade_mode = fade_modes['desktop']

# split image filename into name and extension
#name, ext = os.path.splitext(image_file)

# create a new file name for saving the result
#new_image_file = "%s%s%s" % (name, str(factor), ext)
#img_anti.save(new_image_file)
#print("resized file saved as %s" % new_image_file)

def rgb2hsv(r, g, b):
    ''' helper for colors conversion/scaling '''
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    h = h * 0xffff
    s = s * 0xffff
    v = v * 0xffff
    return(h, s, v)

def get_color_averages(img,totpixels):
    '''get averages of colors in image'''
    total_red = total_green = total_blue = 0
    for y in range(0, img.size[1]):
        for x in range(0, img.size[0]):
            pixel = img.getpixel((x,y))

            pixel_RED = pixel[0]
            pixel_GREEN = pixel[1]
            pixel_BLUE = pixel[2]

            total_red += pixel_RED
            total_green += pixel_GREEN
            total_blue += pixel_BLUE

            average_red = total_red / totpixels
            average_green = total_green / totpixels
            average_blue = total_blue / totpixels

    return((average_red, average_green, average_blue))

def scan_screen(sample_x,sample_y):
    totpixels = sample_x * sample_y

    with mss() as sct: image_file = sct.shot() # take screenshot
    img_org = Image.open(image_file) # open image in python
    width_org, height_org = img_org.size

    width = int(width_org * factor)
    height = int(height_org * factor)

    img = img_org.resize((width, height), Image.NEAREST) # quickest down-sizing filter

    t1 = time.process_time() # take first snapshot of processing time

    resized_img = img.resize((sample_x, sample_y)) # Shrink the image to a more manageable size with PIL
                                                   # (just a few ms on the average machine)
    average_red, average_green, average_blue = get_color_averages(resized_img,totpixels) # get the averages of each color in the image

    t2 = time.process_time() # take second snapshot of processing time

    print("\rRGB {:.1f} {:.1f} {:.1f}".format(average_red, average_green, average_blue))
    print("- Time {}".format(t2-t1))

    return((average_red, average_green, average_blue))

def main():
    # start with the LIFX business...
    lifx = return_interface(None)
    lights = get_lights(lifx)
    list_lights(lights)

    # the block of data to analyze.
    # PIL resizing to 1x1 seems to do strange things; a bigger box works better
    # and still plenty fast...
    sample_x = int(1920/30)
    sample_y = int(1080/30)


    # screen scanning loop
    while True:
        average_red, average_green, average_blue = scan_screen(sample_x,sample_y)
        h, s, v = rgb2hsv(average_red, average_green, average_blue)
        color = (h, s, v, 5500)
        for light in lights:
            light.set_color(color,fade_mode,rapid=True)

        time.sleep(1/60)

if __name__ == '__main__':
    try:
        main()
    finally:
        print("goodbye")
