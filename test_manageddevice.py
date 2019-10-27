import lifxtools
import lifxlan

mlifx = lifxtools.ManagedLifx(lifxtools.return_interface(None))

mdevice = lifxtools.ManagedDevice(mlifx.devices[0])

class Test_ManagedDevice:

    def test_device_type(self):

        assert type(mdevice) == lifxtools.ManagedDevice
