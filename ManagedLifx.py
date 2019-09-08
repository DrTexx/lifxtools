class ManagedLifx:

    def __init__(self,lifx):

        self.lifx = lifx
        self.devices = self.lifx.get_devices()

    def refresh_devices(self):

        self.devices = self.lifx.get_devices()

    def print_device_labels(self):

        for device in self.devices:

            print(device.get_label())
