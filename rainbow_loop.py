from time import sleep
from lifxtools import return_interface, get_lights, list_lights, blink_light, managedLight
from lifxlan import RED, GREEN, BLUE

def create_managed_lights(_lights):
    _managedLights = []
    for light in _lights:
        _managedLights.append(managedLight(light))
    return(_managedLights)

# custom colours [hue (0-65535), saturation (0-65535), brightness (0-65535), Kelvin (2500-9000)]
def GEN_C(hue_perc,saturation_perc,brightness_perc,kelvin):
    hue = 65535 * hue_perc
    sat = 65535 * saturation_perc
    bri = 65535 * brightness_perc
    kel = kelvin
    return((hue,sat,bri,kel))

#(65535, 0, 65535, 6500)
def gen_rainbow_colors(divisions):
    max_hue = 1 # change to 1 if you want compatibility with GEN_C function, or use 65535 in other cases
    hue_increments = max_hue / divisions
    colors = []

    for i in range(divisions):
        hue = (i*hue_increments)
        colors.append(
            GEN_C(hue,0.8,1,6500)
        )

    return(colors)

lifx = return_interface(None)
lights = get_lights(lifx)

#colors = [RED,GREEN,BLUE]
color_resolution = 12
colors = gen_rainbow_colors(3*color_resolution)
cycle_time = 3*6 # seconds
time_per_color = cycle_time/len(colors) # seconds
time_per_color_ms = time_per_color * 1000 # milliseconds

for light in lights:
    managedLights = create_managed_lights(lights)

try:

    for ml in managedLights:
        print(ml.light.get_color())
        ml.ssave()
        ml.light.set_power(True)

    while True:
        for color in colors:
            for light in lights:
                print(color)
                light.set_color(color,time_per_color_ms,rapid=True)
                sleep(time_per_color)

finally:

    for ml in managedLights:
        sleep(0.3)
        ml.sload()
