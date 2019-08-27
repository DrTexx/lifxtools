import new_detect_taps
import lifxtools
from time import sleep
import matplotlib.pyplot as plt
import math

# ---- lifxtools code starts ----
lifx = lifxtools.return_interface(None)
lights = lifx.get_lights()

managedLights = lifxtools.create_managed_lights(lights)

# input("press any key to continue onto tap recog.")
# ---- lifxtools code ends ----

# ---- tap tester code starts ----
tt = new_detect_taps.TapTester()
# ---- tap tester code ends ----

for ml in managedLights:
    ml.ssave()
    ml.light.set_power(True)

try:

    hue = 0

    plt.axis([0, 1000, 0.005, 0.015])

    for i in range(1000):

        tap_was_detected, amplitude = tt.listen()

        if (tap_was_detected == True):
            plt.scatter(i,amplitude)
            plt.pause(0.05)
    plt.show()



        # if (tap_was_detected == True):
        #     print("tap!")
        #     # for light in lights:
        #     #     lifxtools.toggle_light(light)
        #     print(hue)
        #     for light in lights:
        #         light.set_color((hue, 65535/4, 65535/2, 5500),100,rapid=True)
        #     sleep(100/1000)
        #     for light in lights:
        #         light.set_color((hue, 65535/4, 65535, 5500),100,rapid=True)
        #
        #     if (hue < (65535*0.9)):
        #         hue += 65535*0.1
        #     else:
        #         hue = 0

except Exception as err:
    print("ERROR!")
    print(err)

finally:

    for ml in managedLights:
        ml.sload()
