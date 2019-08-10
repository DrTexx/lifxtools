#!/usr/bin/env python3
'''
change all lifx globes to the on-screen color average of a monitor/s of your choice
'''
# based on the excellent LifxLAN library https://github.com/mclarkk/lifxlan
# adapted to python3 and improved upon from the screenlifx example script https://github.com/MarcoPon/screenlifx

# note:
# programs such as Flux or other 'Night Light' alternatives may impact colours.
# I can confirm this is the case for Night Light in the Gnome flavour of Debian 10 Buster.

from lifxtools import return_interface, get_lights, list_lights, blink_light, managedLight, d_benchmark
from mss import mss
from PIL import Image
from time import sleep
from colorsys import rgb_to_hsv

# static options
fade_modes = {'game': 0, 'smooth': 5, 'movie': 150, 'desktop': 300, 'slow': 1000, 'super-slow': 2000, 'ultra-slow': 5000}
monitor_color_temps = {'default': 6500, 'nightLight': 4000} # always match monitor colour tempreture to this setting (in kelvin)

# preferences
factor = 1 # 1: good PC performance, 0.75: average PC performance (may cause colour artifacting)
fade_mode = fade_modes['game'] # default:'desktop'
monitor_color_temp = monitor_color_temps['default']
max_brightness = 100 # default:100
monitor_num = 1 # 0:all-monitors combined (+black?), 1:primary only, 2: secondary only, etc.

# functions
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

    red = total_red / _totpixels
    green = total_green / _totpixels
    blue = total_blue / _totpixels

    return((average_red, average_green, average_blue))

def return_screengrab(_monitor_num):
    with mss() as sct:
        monitors = sct.monitors[_monitor_num] # get monitor object
        img_raw = sct.grab(monitors) # get raw pixels from the selected monitor
        _img = Image.frombytes("RGB", img_raw.size, img_raw.bgra, "raw", "BGRX") # create an image from raw pixels
        return(_img)

def return_new_dimensions(_img,factor):
    og_width, og_height = _img.size
    width = int(og_width * factor)
    height = int(og_height * factor)
    return((width,height))

def scan_screen(sample_x,sample_y,totpixels):
    img = return_screengrab(monitor_num)
    resized_img = img.resize(return_new_dimensions(img,factor), Image.NEAREST)
    shrunk_img = resized_img.resize((sample_x, sample_y)) # Shrink the image to a more manageable size with PIL (just a few ms on the average machine)
    average_red, average_green, average_blue = get_color_averages(shrunk_img,totpixels) # get the averages of each color in the image
    print("({:.1f},{:.1f},{:.1f})".format(average_red, average_green, average_blue))

    return((average_red, average_green, average_blue))

@d_benchmark
def main_loop(sample_x,sample_y,totpixels):
    average_red, average_green, average_blue = scan_screen(sample_x,sample_y,totpixels)
    h, s, v = rgb2hsv(average_red, average_green, average_blue)
    color = (h, s, v*(max_brightness/100), monitor_color_temp)
    for light in lights:
        light.set_color(color,fade_mode,rapid=True)

    sleep(1/60)

def main():
    '''main function for scanning screen colors and applying color average to lifx lights'''
    # the block of data to analyze.
    # PIL resizing to 1x1 seems to do strange things; a bigger box works better
    # and still plenty fast...
    sample_x = int(1920/30)
    sample_y = int(1080/30)
    totpixels = sample_x * sample_y
    while True:
        main_loop(sample_x,sample_y,totpixels)

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
