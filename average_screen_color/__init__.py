#!/home/denver/venvs/lifxtools/bin/python3 -E

'''
change all lifx globes to the on-screen color average of a monitor/s of your choice
'''
# based on the excellent LifxLAN library https://github.com/mclarkk/lifxlan
# adapted to python3 and improved upon from the screenlifx example script https://github.com/MarcoPon/screenlifx

# note:
# programs such as Flux or other 'Night Light' alternatives may impact colours.
# I can confirm this is the case for Night Light in the Gnome flavour of Debian 10 Buster.

from lifxtools import return_interface, get_lights, list_lights, blink_light, ManagedLight, d_benchmark, create_managed_lights, rgbk2hsvk, ManagedLifx
from mss import mss
from PIL import Image, ImageFilter
from time import sleep, process_time

# functions
def scan_img_average_color(_img):
    '''returns the color average for the entire screen'''

    total_red = total_green = total_blue = 0

    y_length = _img.size[1]
    x_length = _img.size[0]
    totpixels = y_length * x_length

    for y in range(0, y_length):

        for x in range(0, x_length):

            pixel = _img.getpixel((x,y))

            total_red += pixel[0]
            total_green += pixel[1]
            total_blue += pixel[2]

    r = total_red / totpixels
    g = total_green / totpixels
    b = total_blue / totpixels

    # print("({:.1f},{:.1f},{:.1f})".format(r, g, b))

    return((r, g, b))

def scan_img_average_color_ignore_black(_img):
    '''returns the color average for the entire screen'''

    total_red = total_green = total_blue = total_ignored = 0

    y_length = _img.size[1]
    x_length = _img.size[0]
    totpixels = y_length * x_length

    for y in range(0, y_length):

        for x in range(0, x_length):

            pixel = _img.getpixel((x,y))

            pixel_r, pixel_g, pixel_b = pixel

            if (pixel_r < 12.75 and pixel_g < 12.75 and pixel_b < 12.75): # if there is less than 5% of r, g and b
                total_ignored += 1
            else:
                total_red += pixel_r
                total_green += pixel_g
                total_blue += pixel_b

    divider = totpixels - total_ignored

    if (divider == 0):
        r = 5
        g = 5
        b = 5
    else:
        r = total_red / (totpixels - total_ignored)
        g = total_green / (totpixels - total_ignored)
        b = total_blue / (totpixels - total_ignored)

    print("({:.1f},{:.1f},{:.1f})".format(r, g, b))
    print("ignored {} pixels ({:.2f}%)".format(total_ignored,total_ignored/totpixels*100))

    return((r, g, b))

def scan_img_average_color_top_only(_img):
    '''returns the color average for the entire screen'''

    total_red = total_green = total_blue = 0

    y_length = _img.size[1]
    x_length = _img.size[0]
    totpixels = (y_length/2) * x_length

    for y in range(0, y_length):

        if (y < y_length/2):

            for x in range(0, x_length):

                pixel = _img.getpixel((x,y))

                total_red += pixel[0]
                total_green += pixel[1]
                total_blue += pixel[2]

    r = total_red / totpixels
    g = total_green / totpixels
    b = total_blue / totpixels

    # print("({:.1f},{:.1f},{:.1f})".format(r, g, b))

    return((r, g, b))

def FPS_scan(_img,_monitor_range=(0.25,0.75),verbose=False):
    ''' only returns the color average for the middle 50% of the screen (vertically and horizontally), also a likely boost in performance but further testing needed'''
    total_red = total_green = total_blue = 0

    y_length = _img.size[1]
    x_length = _img.size[0]

    y_min = y_length*_monitor_range[0]
    y_max = y_length*_monitor_range[1]
    y_range = y_max - y_min # new range is the new maximum minus the new minimum

    x_min = x_length*_monitor_range[0]
    x_max = x_length*_monitor_range[1]
    x_range = x_max - x_min # new range is the new maximum minus the new minimum

    total_range = y_range * x_range

    if (verbose == True): print("y-min:{} y-max:{} x-min:{} x-max:{} y-range:{} x-range:{} total-range:{}".format(y_min, y_max, x_min, x_max, y_range, x_range, total_range))

    for y in range(0,y_length): # for each pixel on why

        if (y > y_min and y < y_max): # if the pixel is in the range

            for x in range(0,x_length): # iterate through x

                if (x > x_min and x < x_max): # if the pixel is in x's range

                    pixel = _img.getpixel((x,y))

                    total_red += pixel[0]
                    total_green += pixel[1]
                    total_blue += pixel[2]

    r = total_red / total_range
    g = total_green / total_range
    b = total_blue / total_range

    # print("({:.1f},{:.1f},{:.1f})".format(r, g, b))

    return((r,g,b))

    # raise NotImplementedError()

def return_screengrab(_monitor_num):
    with mss() as sct:
        monitors = sct.monitors[_monitor_num] # get monitor object
        img_raw = sct.grab(monitors) # get raw pixels from the selected monitor
        _img = Image.frombytes("RGB", img_raw.size, img_raw.bgra, "raw", "BGRX") # create an image from raw pixels
        return(_img)

def return_new_dimensions(_img,_factor):

    og_width, og_height = _img.size
    width = int(og_width * _factor)
    height = int(og_height * _factor)
    return((width,height))

def resize_img_by_factor(_img,_factor):

    return(_img.resize(return_new_dimensions(_img,_factor), Image.NEAREST)) # shrink the image

def resize_img_to_size(_img,_sample_size):

    return(_img.resize(_sample_size)) # Shrink the image to a more manageable size with PIL (just a few ms on the average machine)

def scan_img(_img,_scan_method):

    r, g, b = _scan_method(_img) # get the averages of each color in the image


    return((r, g, b))

# static options requiring functions
scan_methods = {
    'default': scan_img_average_color,
    'ignore-black': scan_img_average_color_ignore_black,
    'top-only': scan_img_average_color_top_only,
    'game-FPS': FPS_scan
}

# @d_benchmark
def scan_set_loop(_scan_method,_sample_size,_lights,_monitor_num,_factor,_fade_mode,_monitor_color_temp,_min_brightness,_max_brightness):

    # get a screengrab of the selected monitor/s
    img = return_screengrab(_monitor_num)

    # resize screengrab to a more manageable size
    img_resized = resize_img_by_factor(img,_factor)

    # shrink resized image to sampling size
    img_shrunk = resize_img_to_size(img_resized,_sample_size)

    # blur tiny image
    # img_blurred = img_shrunk.filter(ImageFilter.BoxBlur(1))

    # get colour averages
    r, g, b = _scan_method(img_shrunk)

    # convert rgb values to hsvk
    h, s, v, k = rgbk2hsvk (r, g, b, _monitor_color_temp)

    # adjust the colours to user preferences
    v_calc = v*(_max_brightness/100)

    # color = (h, s, v*(_max_brightness/100), k)
    if (v_calc > _min_brightness):
        # max values are 65535 for h, s and v. k is between 1500 and 7000 for color mini
        color = (h, s, v*(_max_brightness/100), k)

    else:
        color = (0, 65535, 1, _monitor_color_temp) # a very dim red

    # set each light to the colour just generated
    for light in _lights:
        light.set_color(color,_fade_mode,rapid=True)

def main():
    '''main function for scanning screen colors and applying color average to lifx lights'''

    # static options
    fade_modes = {'game': 0, 'smooth': 5, 'movie': 150, 'desktop': 300, 'slow': 1000, 'super-slow': 2000, 'ultra-slow': 5000}
    monitor_color_temps = {'default': 6500, 'nightLight': 4000} # always match monitor colour tempreture to this setting (in kelvin)

    # preferences
    num_lights = None # None: slower, automatic detection of all network lights, [integer]: specify number of lights, quicker discovery
    factor = 0.75 # 1: good PC performance, 0.75: average PC performance (may cause colour artifacting)
    fade_mode = fade_modes['movie'] # default:'movie'
    monitor_color_temp = monitor_color_temps['default']
    min_brightness = 0 # default: 1
    max_brightness = 100 # default:100
    monitor_w = 1920
    monitor_h = 1080
    monitor_sample_scale = 30 # default: 30 (lower numbers give more accurate averages but are harder to calculate)
    monitor_num = 1 # 0:all-monitors combined (+black?), 1:primary only, 2: secondary only, etc.
    scan_method = scan_methods['default']
    target_Hz = 30

    # get lifx interface and lights
    mlifx = ManagedLifx(return_interface(None))
    mlifx.print_device_labels()

    # the block of data to analyze. PIL resizing to 1x1 seems to do strange things; a bigger box works better (and still plenty fast)
    sample_size = (int(monitor_w/monitor_sample_scale), int(monitor_h/monitor_sample_scale))

    try:

        for ml in mlifx.managed_lights:

            ml.ssave()
            ml.light.set_power(True)
            # blink_light(ml.light)

        while True:
            t1 = process_time()
            scan_set_loop(scan_method,sample_size,mlifx.lights,monitor_num,factor,fade_mode,monitor_color_temp,min_brightness,max_brightness)
            t2 = process_time()

            while ((t2-t1) < (1/target_Hz)):
                t2 = process_time()

            actual_Hz = int(1/(t2-t1))
            print("TARGET:{:>3} Hz ACTUAL:{:>3} Hz DELTA:{:>3} Hz".format(target_Hz, actual_Hz, actual_Hz-target_Hz))

    finally:

        sleep(0.3)

        for ml in mlifx.managed_lights:
            # blink_light(ml.light)
            ml.sload()
            
