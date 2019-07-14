'''
lt module from lifxtools package
'''

print("lifxtools/lt/__init__.py")

from lifxtools import *

def start():
    lifx = return_interface()
    devices = lifx.get_lights()
    num_lights = return_num_lights(devices)
    list_devices(devices)
    # blink_devices(devices)

    root = Tk()

    class Window(Frame):

        def __init__(self,master=None):
            Frame.__init__(self,master)
            self.master = master
            self._init_window()

        def _init_window(self):
            m = self.master
            m.title = "Lifx Tk Controller"

            test_frame = Frame(m)
            test_frame.pack()

            live_data_frame = Frame(test_frame)
            live_data_frame.pack()

            live_data_checkbox = Checkbutton(live_data_frame, text="Enable live data", var=live_data)
            live_data_checkbox.var = live_data
            live_data_checkbox.pack()

            test_text = Label(test_frame,text="Lights discovered")
            test_text.pack()

            self.light_settings = []
            i = 0
            for device in devices:
                self.light_settings.append({'device': device, 'frame': Frame(test_frame)}) # add frames and all relevant things here
                # configure frames and relevant items here
                self.light_settings[i]['frame'].config(padding=5,relief=SUNKEN)
                self.light_settings[i]['frame'].pack(fill=X)

                _light_device = self.light_settings[i]['device']
                _light_frame = self.light_settings[i]['frame']

                light_label = Label(_light_frame, text=str(_light_device.get_label()))
                light_label.pack(side=LEFT)

                light_toggle = Button(_light_frame, text="toggle power", command=lambda: toggle_light(_light_device))
                light_toggle.pack(side=LEFT)

                # light_brightness = Scale(_light_frame, from_=0, to=65535, orient=HORIZONTAL) # this needs to be accessible outside of for loop, right now it is not
                # light_brightness.pack(side=LEFT)

                light_profile_default = Button(_light_frame, text="default color", command=lambda: set_light_color(_light_device,default_color))
                light_profile_default.pack(side=LEFT)

                light_profile_bedtime = Button(_light_frame, text="bedtime color", command=lambda: set_light_color(_light_device,bedtime_color))
                light_profile_bedtime.pack(side=LEFT)

                light_profile_white = Button(_light_frame, text="white color", command=lambda: set_light_color(_light_device, WHITE))
                light_profile_white.pack(side=LEFT)

                light_profile_red = Button(_light_frame, text="red color", command=lambda: set_light_color(_light_device, RED))
                light_profile_red.pack(side=LEFT)
                i += 1

            if (debug == True): print(self.light_settings)
            light0_frame = self.light_settings[0]['frame'] # TEMPORARY UNTIL CODE BELOW MIGRATED TO ITERABLE FORMAT

            self.light0_brightness = Scale(light0_frame, from_=0, to=65535,orient=HORIZONTAL)
            self.light0_brightness.pack(side=LEFT)

        def _update_brightness(self): self.light0_brightness.set(get_light_brightness(devices[0]))

        def _update_loop(self,ms_per_loop=1000):
            if (live_data == True):
                self._update_brightness()
            self.after(ms_per_loop,self._update_loop) # repeat _update_loop()

        def _exit_app(self,event):
            exit()

    app = Window(root)
    app._update_loop() # must be before main loop
    root.mainloop()
