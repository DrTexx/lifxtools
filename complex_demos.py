from lifxtools import return_interface, get_lights, list_lights, blink_light, managedLight # used for network discovery and control
from time import sleep # used for delays
from lifxlan import RED,GREEN,BLUE,WHITE # just an instance of the color

# settings
num_lights = None
BPM = 120*4

enable_loop_BPM = False

enable_loop_rainbow = False
rainbow_loop_saturation = 65535 * 0.25
rainbow_loop_brightness = 65535 * 0.5

enable_loop_strobe = True
strobe_hz = 60

# custom brightnesses
def B_GEN(_perc): return(65535*(_perc/100))
B100 = int(65535*1)
B25 = int(65535*0.25)
B1 = int(65535*0.01)

# custom colours [hue (0-65535), saturation (0-65535), brightness (0-65535), Kelvin (2500-9000)]
def GEN_C(hue_perc,saturation_perc,brightness_perc,kelvin_perc):
    hue = 65535 * hue_perc
    sat = 65535 * saturation_perc
    bri = 65535 * brightness_perc
    kel = 65535 * kelvin_perc
    return((hue,sat,bri,kel))
DAYLIGHT_B100 = (65535, 0, B_GEN(100), 5600)
DAYLIGHT_B50 = (65535, 0, B_GEN(50), 5600)
DAYLIGHT_B25 = (65535, 0, B25, 5600)
DAYLIGHT_B1 = (65535, 0, B1, 5600)
SOFT_DAYLIGHT_B50 = (65535, 0, B_GEN(50), 4500)
WHITE_ULTRADIM = (58275, 0, B_GEN(1), 5500)

# static configuration
BPS = BPM/60
HZ = 1/BPS
HUE_MAX = 65535

# define functions
def rainbow_loop(_light,cycle_time=1):
    sleepfor = 1/(HUE_MAX/cycle_time)
    for i in range(HUE_MAX):
        _light.set_color((i, rainbow_loop_saturation, 65535, 5600),rapid=True)
        sleep(sleepfor)

def strobe(_light,_hz,_colors=[WHITE, WHITE_ULTRADIM]):
    for color in _colors:
        _light.set_color(color,rapid=True)
        sleep(1/_hz)

def fade_out_and_in(_light):
    _light.set_power(False)
    sleep(0.5)
    _light.set_power(True)


# primary code
lifx = return_interface(num_lights,debug=True)
lights = get_lights(lifx,debug=True)
list_lights(lights,debug=True) # list all lights found on the network
ceiling_light = lifx.get_device_by_name("Office Ceiling")

ceiling_light_state = managedLight(ceiling_light,debug=True) # create a new managed light (supports saving/loading state and more)

try:
    ceiling_light_state.ssave() # save the lights state
    ceiling_light_state.print_saved_state() # print the saved light state
    print("Break this function (Ctrl + C) to reset lights to their original color")

    fade_out_and_in(ceiling_light)

    if (enable_loop_BPM == True):

        while True:
            for color in [RED,GREEN,BLUE,WHITE]:
                ceiling_light.set_color(color,rapid=True)
                sleep(HZ)

    if (enable_loop_rainbow == True):
        rainbow_loop_brightness = ceiling_light_state.color[2]
        while True:
            rainbow_loop(ceiling_light)

    if (enable_loop_strobe == True):
        while True:
            strobe(ceiling_light,strobe_hz)

finally:
    sleep(0.2) # wait a moment before resetting to avoid errors from overwhelming the bulb with requests
    try:
        fade_out_and_in(ceiling_light)
        ceiling_light_state.sload() # load the lights state
    except:
        sleep(1)
        print("--[AN ERROR OCCURED WHILE EXITTING]--")
        ceiling_light.set_color(RED)
        sleep(3)
        ceiling_light.set_color(DAYLIGHT_B50)
