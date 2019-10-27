#!/home/denver/venvs/lifxtools/bin/python3 -E

import lifxtools
from time import sleep

mlifx = lifxtools.ManagedLifx(lifxtools.return_interface(None))

saturation = 0

[device.ssave() for device in mlifx.managed_devices]

input("waiting...")

try:
    while True:
        while saturation < 65535:
            saturation += 65535/20
            for mdevice in mlifx.managed_devices:

                if mdevice.is_light == True:

                    mdevice.device.set_color((0, saturation, 65535/2, 6500),0,rapid=True)

            sleep(1/20)
        sleep(5)

        while saturation > 0:
            saturation -= 65535/120
            for mdevice in mlifx.managed_devices:

                if mdevice.is_light == True:

                    mdevice.device.set_color((0, saturation, 65535/2, 6500),0,rapid=True)

            sleep(1/120)
        sleep(5)
finally:
    [device.sload() for device in mlifx.managed_devices]


sleep(1)
