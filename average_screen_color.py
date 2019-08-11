#!/usr/bin/env python3
'''
change all lifx globes to the on-screen color average of a monitor/s of your choice
'''
# based on the excellent LifxLAN library https://github.com/mclarkk/lifxlan
# adapted to python3 and improved upon from the screenlifx example script https://github.com/MarcoPon/screenlifx

# note:
# programs such as Flux or other 'Night Light' alternatives may impact colours.
# I can confirm this is the case for Night Light in the Gnome flavour of Debian 10 Buster.

from lifxtools import return_interface, get_lights, list_lights, blink_light, managedLight, d_benchmark, create_managed_lights, rgbk2hsvk
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
def normal_scan(_img,_totpixels):
    '''returns the color average for the entire screen'''
    total_red = total_green = total_blue = 0
    for y in range(0, _img.size[1]):
        for x in range(0, _img.size[0]):
            pixel = _img.getpixel((x,y))

            pixel_RED = pixel[0]
            pixel_GREEN = pixel[1]
            pixel_BLUE = pixel[2]

            total_red += pixel_RED
            total_green += pixel_GREEN
            total_blue += pixel_BLUE

    red = total_red / _totpixels
    green = total_green / _totpixels
    blue = total_blue / _totpixels

    return((red, green, blue))

def FPS_scan(_img,_totpixels,start_perc=0.25,end_perc=0.75):
    ''' only returns the color average for the middle 50% of the screen (vertically and horizontally), also a likely boost in performance but further testing needed'''
    total_red = total_green = total_blue = 0
    # get length of y (total monitor width in pixels)
    y_length = _img.size[1]
    x_length = _img.size[0]

    y_min = y_length*start_perc
    y_max = y_length*end_perc
    y_range = y_max - y_min # new range is the new maximum minus the new minimum

    x_min = x_length*start_perc
    x_max = x_length*end_perc
    x_range = x_max - x_min # new range is the new maximum minus the new minimum

    # print("min:{} max:{} range:{}".format(y_min,y_max,y_range))

    for y in range(0,y_length): # for each pixel on why

        if (y > y_min and y < y_max): # if the pixel is in the range

            for x in range(0,x_length): # iterate through x

                if (x > x_min and x < x_max): # if the pixel is in x's range

                    pixel = _img.getpixel((x,y))

                    total_red += pixel[0]
                    total_green += pixel[1]
                    total_blue += pixel[2]

    red = total_red / _totpixels
    green = total_green / _totpixels
    blue = total_blue / _totpixels

    return((red,green,blue))

    # raise NotImplementedError()

def get_color_averages(img,totpixels):
    '''get averages of colors in image'''
    red, green, blue = scan_method(img,totpixels)

    return((red, green, blue))

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

# static options requiring functions
scan_methods = {'default': normal_scan, 'game-FPS': FPS_scan}

# preferences requiring functions
scan_method = scan_methods['game-FPS']

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
