#!/usr/bin/env python3

# change all lifx globes to an average of the colors on-screen
# based on the excellent LifxLAN library https://github.com/mclarkk/lifxlan
# adapted to python3 and improved upon from the screenlifx example script https://github.com/MarcoPon/screenlifx

# note:
# programs such as Flux or other 'Night Light' alternatives may impact colours.
# I can confirm this is the case for Night Light in the Gnome flavour of Debian 10 Buster.

from lifxtools import return_interface, get_lights, list_lights, blink_light, managedLight
from mss import mss
from PIL import Image
from time import sleep, process_time
from colorsys import rgb_to_hsv

# static options
fade_modes = {'game': 0, 'movie': 150, 'desktop': 300, 'slow': 1000, 'super-slow': 2000, 'ultra-slow': 5000}

# preferences
factor = 0.75
fade_mode = fade_modes['game'] # default:'desktop'
monitor_color_temp = 5500 # normal:5500, NightLightMode:3000
max_brightness = 100 # default:100
selected_monitor = 1 # 0:all-monitors combined (+black?), 1:primary only, 2: secondary only, etc.

# split image filename into name and extension
#name, ext = os.path.splitext(image_file)

# create a new file name for saving the result
#new_image_file = "%s%s%s" % (name, str(factor), ext)
#img_anti.save(new_image_file)
#print("resized file saved as %s" % new_image_file)

def create_managed_lights(_lights):
    _managedLights = []
    for light in _lights:
        _managedLights.append(managedLight(light))
    return(_managedLights)

def rgb2hsv(r, g, b):
    ''' helper for colors conversion/scaling '''
    h, s, v = rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
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

    with mss() as sct:
#        for num, monitor in enumerate(sct.monitors[1:], 1): # Get rid of the first, as it represents the "All in One" monitor
        sct_img = sct.grab(sct.monitors[selected_monitor]) # Get raw pixels from the screen
        img_org = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX") # Create the Image
    width_org, height_org = img_org.size

    width = int(width_org * factor)
    height = int(height_org * factor)

    img = img_org.resize((width, height), Image.NEAREST) # quickest down-sizing filter

    t1 = process_time() # take first snapshot of processing time

    resized_img = img.resize((sample_x, sample_y)) # Shrink the image to a more manageable size with PIL
                                                   # (just a few ms on the average machine)
    average_red, average_green, average_blue = get_color_averages(resized_img,totpixels) # get the averages of each color in the image

    t2 = process_time() # take second snapshot of processing time

    print("\rRGB {:.1f} {:.1f} {:.1f}".format(average_red, average_green, average_blue))
    print("- Time {}".format(t2-t1))

    return((average_red, average_green, average_blue))

def main():
    '''main function for scanning screen colors and applying color average to lifx lights'''
    # the block of data to analyze.
    # PIL resizing to 1x1 seems to do strange things; a bigger box works better
    # and still plenty fast...
    sample_x = int(1920/30)
    sample_y = int(1080/30)

    while True:
        average_red, average_green, average_blue = scan_screen(sample_x,sample_y)
        h, s, v = rgb2hsv(average_red, average_green, average_blue)
        color = (h, s, v*(max_brightness/100), monitor_color_temp)
        for light in lights:
            light.set_color(color,fade_mode,rapid=True)

        sleep(1/60)

# get lifx interface and lights
lifx = return_interface(None)
lights = get_lights(lifx)
list_lights(lights)
managedLights = create_managed_lights(lights)

if __name__ == '__main__':
    try:
        for ml in managedLights:
            ml.ssave()
            ml.light.set_power(True)
            # blink_light(ml.light)
        main()
    finally:
        sleep(0.3)
        for ml in managedLights:
            # blink_light(ml.light)
            ml.sload()
