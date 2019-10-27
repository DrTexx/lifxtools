import lifxtools
import pyaudio
import pytest

mlifx = lifxtools.ManagedLifx(lifxtools.return_interface(None))

update_Hz=120
fade=20
lal = lifxtools.LightShow(mlifx,pyaudio,update_Hz,fade)


# store volume before tests
# _volume_before_tests = mc.gvol()
# _mute_before_tests = mc.gmute()

class Test_LightShow():

    def test_running_status(self):

        assert lal.running == False

    def test_start(self):

        lal.start()
        assert lal.running == True

    def test_stop(self):

        lal.stop()
        assert lal.running == False

#     def test_svol_TypeErrors(self):
#         with pytest.raises(TypeError):
#             mc.svol(4.5) # no floats
#         with pytest.raises(TypeError):
#             mc.svol("30") # no strings

print("end of tests")
