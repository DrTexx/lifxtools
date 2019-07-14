#!/usr/bin/env python3

# change all lifx globes to an average of the colors on-screen
# based on the excellent LifxLAN library https://github.com/mclarkk/lifxlan
# adapted to python3 and improved upon from the screenlifx example script https://github.com/MarcoPon/screenlifx

from lifxtools import return_interface, get_lights, list_lights
from mss import mss
from PIL import Image
import time, os, colorsys

# preferences
factor = 0.75

# split image filename into name and extension
#name, ext = os.path.splitext(image_file)

# create a new file name for saving the result
#new_image_file = "%s%s%s" % (name, str(factor), ext)
#img_anti.save(new_image_file)
#print("resized file saved as %s" % new_image_file)

# helper for colors conversion/scaling
def rgb2hsv(r, g, b):
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    h = h * 0xffff
    s = s * 0xffff
    v = v * 0xffff
    return(h, s, v)

def main():
    # start with the LIFX business...
    lifx = return_interface(None)
    lights = get_lights(lifx)
    list_lights(lights)

    # the block of data to analyze.
    # PIL resizing to 1x1 seems to do strange things; a bigger box works better
    # and still plenty fast...
    rx = int(1920/30)
    ry = int(1080/30)
    totpixels = rx * ry

    # screen scanning loop
    while True:

        with mss() as sct: image_file = sct.shot() # take screenshot
        img_org = Image.open(image_file) # open image in python
        width_org, height_org = img_org.size

        width = int(width_org * factor)
        height = int(height_org * factor)

        img = img_org.resize((width, height), Image.NEAREST) # quickest down-sizing filter

        t1 = time.process_time()
        # let PIL shrink the image into a more manageable size
        # (just few ms on the average machine)
        img = img.resize((rx, ry))
        red = green = blue = 0
        for y in range(0, img.size[1]):
            for x in range(0, img.size[0]):
                c = img.getpixel((x,y))
                print(c)
                red = red + c[0]
                green = green + c[1]
                blue = blue + c[2]
        red = red / totpixels
        green = green / totpixels
        blue = blue / totpixels
        t2 = time.process_time()

        print("\rRGB {:.1f} {:.1f} {:.1f}".format(red, green, blue))
        print("- Time {}".format(t2-t1))

        h, s, v = rgb2hsv(red, green, blue)
        color = (h, s, v, 5500)
        for light in lights:
            light.set_color(color)

        time.sleep(1/60)

if __name__ == '__main__':
    try:
        main()
    finally:
        print("goodbye")
