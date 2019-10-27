import lifxtools
import lifxlan

lifx = lifxtools.return_interface(None)
mlifx = lifxtools.ManagedLifx(lifx)

class Test_ManagedLifx:

    def test_lifx_type(self):

        assert type(mlifx.lifx) == lifxlan.LifxLAN

    def test_verbose_type(self):

        assert (type(mlifx.verbose)) == bool
