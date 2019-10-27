import lifxtools
from time import sleep

lifx = lifxtools.return_interface(None)

devices = lifx.get_devices()

managed_devices = [lifxtools.ManagedDevice(device) for device in devices]

print(managed_devices)

for device in managed_devices:
    print("color of [{}] = {}".format(device.label,device.color))

sleep(2)

for device in managed_devices:
    print("saving state of [{}] in object...".format(device.label))
    device.ssave()

sleep(2)

for device in managed_devices:
    print("color of [{}] = {}".format(device.label,device.color))

sleep(2)

for device in managed_devices:
    print("setting color of [{}] to 'bedtime_color'".format(device.label))
    device.device.set_color(lifxtools.bedtime_color)

sleep(2)

for device in managed_devices:
    print("loading state of [{}] in object...".format(device.label))
    device.sload()
