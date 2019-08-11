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

# static options
fade_modes = {'game': 0, 'smooth': 5, 'movie': 150, 'desktop': 300, 'slow': 1000, 'super-slow': 2000, 'ultra-slow': 5000}
monitor_color_temps = {'default': 6500, 'nightLight': 4000} # always match monitor colour tempreture to this setting (in kelvin)

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

def resize_img_by_factor(_img,_factor):

    return(_img.resize(return_new_dimensions(_img,_factor), Image.NEAREST)) # shrink the image

def resize_img_to_size(_img,_sample_size):

    return(_img.resize(_sample_size)) # Shrink the image to a more manageable size with PIL (just a few ms on the average machine)

def get_img_rgb(_img,_scan_method,totpixels):

    r, g, b = _scan_method(_img,totpixels) # get the averages of each color in the image

    print("({:.1f},{:.1f},{:.1f})".format(r, g, b))

    return((r, g, b))

# static options requiring functions
scan_methods = {'default': normal_scan, 'game-FPS': FPS_scan}

@d_benchmark
def scan_set_loop(_scan_method,sample_size,totpixels,_lights,_monitor_num,_factor,_fade_mode,_monitor_color_temp,_max_brightness):

    # get a screengrab of the selected monitor/s
    img = return_screengrab(_monitor_num)

    # resize screengrab to a more manageable size
    img_resized = resize_img_by_factor(img,_factor)

    # shrink resized image to sampling size
    img_shrunk = resize_img_to_size(img_resized,sample_size)

    # get colour averages
    r, g, b = get_img_rgb(img_shrunk,_scan_method,totpixels)

    # convert rgb values to hsvk
    h, s, v, k = rgbk2hsvk (r, g, b, _monitor_color_temp)

    # adjust the colours to user preferences
    color = (h, s, v*(_max_brightness/100), k)

    # set each light to the colour just generated
    for light in _lights:
        light.set_color(color,_fade_mode,rapid=True)

def main():
    '''main function for scanning screen colors and applying color average to lifx lights'''

    # preferences
    num_lights = 3 # None: slower, automatic detection of all network lights, [integer]: specify number of lights, quicker discovery
    factor = 1 # 1: good PC performance, 0.75: average PC performance (may cause colour artifacting)
    fade_mode = fade_modes['game'] # default:'desktop'
    monitor_color_temp = monitor_color_temps['default']
    max_brightness = 100 # default:100
    monitor_num = 1 # 0:all-monitors combined (+black?), 1:primary only, 2: secondary only, etc.
    scan_method = scan_methods['game-FPS']
    colorScan_Hz = 60

    # get lifx interface and lights
    lifx = return_interface(num_lights)
    lights = get_lights(lifx)
    list_lights(lights)
    managedLights = create_managed_lights(lights)

    # the block of data to analyze. PIL resizing to 1x1 seems to do strange things; a bigger box works better (and still plenty fast)
    sample_x = int(1920/30)
    sample_y = int(1080/30)
    sample_size = (sample_x, sample_y)
    totpixels = sample_x * sample_y

    try:
        for ml in managedLights:
            ml.ssave()
            ml.light.set_power(True)
            # blink_light(ml.light)
        while True:
            # get a screengrab
            # scan average RGB values
            # convert RGB averages to HSVK
            # apply user modifiers
            # set light to new colour
            scan_set_loop(scan_method,sample_size,totpixels,lights,monitor_num,factor,fade_mode,monitor_color_temp,max_brightness)
            sleep(1/colorScan_Hz) # TODO: this shouldn't be static, make it a preference
    finally:
        sleep(0.3)
        for ml in managedLights:
            # blink_light(ml.light)
            ml.sload()

if __name__ == '__main__':
    main()
