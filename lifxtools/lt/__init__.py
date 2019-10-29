"""
lt module from lifxtools package
"""

print("lifxtools/lt/__init__.py")

# UI imports
import tkinter as tk  # for UI
from tkinter import ttk  # for not ugly UI

# Backend imports
import lifxtools  # for controlling lights

class Navbar(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        print(self._name,"PARENT =",self.parent)


        self.notebook = ttk.Notebook(self.parent)

        self.page_lightcontrol = tk.Frame(self.notebook)
        self.page_scenemanager = tk.Frame(self.notebook)

        self.devices_found = tk.Listbox(self.page_lightcontrol, selectmode=tk.EXTENDED)
        self.devices_found.pack()

        print("devices",self.parent.mlifx.devices) # print found devices to console

        for index, mdevice in enumerate(self.parent.mlifx.managed_devices, 0): # add each found device to the GUI list
            self.devices_found.insert(index, mdevice.label)

        print_selected_device = tk.Button(self.page_lightcontrol, text="print selected devices index to console", command=self._print_selected_devices)
        print_selected_device.pack()

        toggle_device_power = tk.Button(self.page_lightcontrol, text="toggle device power", command=self._toggle_device_power)
        toggle_device_power.pack()

        set_to_default = tk.Button(self.page_lightcontrol, text="set to default", command=self._set_to_default)
        set_to_default.pack()

        set_to_bedtime = tk.Button(self.page_lightcontrol, text="set to bedtime", command=self._set_to_bedtime)
        set_to_bedtime.pack()

        save_state = tk.Button(self.page_lightcontrol, text="save state", command=self._save_state)
        save_state.pack()

        load_state = tk.Button(self.page_lightcontrol, text="load state", command=self._load_state)
        load_state.pack()



        self.notebook.add(self.page_lightcontrol, text="Light Control")
        self.notebook.add(self.page_scenemanager, text="Scene Manager")

        self.notebook.pack(expand=1, fill="both")

    def _print_selected_devices(self):
        print(self.devices_found.curselection()) # return a tuple of indexes for selected items

    def _get_selected_mdevices(self):
        device_indexes = self.devices_found.curselection()
        devices_to_return = []
        for device_i in device_indexes:
            devices_to_return.append(self.parent.mlifx.managed_devices[device_i])
        return devices_to_return # return a tuple of indexes for selected items

    def _toggle_device_power(self):
        mdevices = self._get_selected_mdevices()
        print("toggling power of mdevices:",mdevices)
        for mdevice in mdevices:
            mdevice.device.set_power(not mdevice.device.get_power())

    def _set_to_default(self):
        mdevices = self._get_selected_mdevices()
        print("setting mdevices to default:",mdevices)
        for mdevice in mdevices:
            mdevice.device.set_color(lifxtools.default_color)

    def _set_to_bedtime(self):
        mdevices = self._get_selected_mdevices()
        print("setting mdevices to bedtime:",mdevices)
        for mdevice in mdevices:
            mdevice.device.set_color(lifxtools.bedtime_color)

    def _save_state(self):
        mdevices = self._get_selected_mdevices()
        print("saving state of mdevices:",mdevices)
        for mdevice in mdevices:
            mdevice.ssave()

    def _load_state(self):
        mdevices = self._get_selected_mdevices()
        print("loading state of mdevices:",mdevices)
        for mdevice in mdevices:
            mdevice.sload()


class DeviceFrameRep(tk.Frame):
    def __init__(self,device_obj,parent,*args,**kwargs):
        tk.Frame.__init__(self,parent,*args,**kwargs)
        self.parent = parent

        self.device = device_obj

        self.placeholder = tk.Label(self,text="DEVICE PREVIEW PLACEHOLDER")
        self.placeholder.pack()


class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        print(self._name,"PARENT =",self.parent)

        # <create the rest of your GUI here>
        self._init_mlifx()
        self._init_GUI()
        print("finished preparing program!")

    def _init_mlifx(self):

        print("_init_mlifx...")
        self.mlifx = lifxtools.ManagedLifx(lifxtools.return_interface(None))
        self.mlifx.add_device(lifxtools.VirtualDevice())
        print(self.mlifx.devices)

    def _init_GUI(self):

        print("_init_GUI...")
        self.navbar = Navbar(self)
        self.navbar.pack(side="left", fill="y")
        self.device_test = DeviceFrameRep(self.mlifx.managed_devices[0],self) # create a frame for the first device
        self.device_test.pack()

    def _update_loop(self, ms_per_loop=1000):
        # if live_data == True:
        #     pass
        #                self._update_brightness()
        self.after(ms_per_loop, self._update_loop)  # repeat _update_loop()

    def _exit_app(self, event):
        exit()


if __name__ == "lifxtools.lt":

    root = tk.Tk()
    mainApp = MainApplication(root)
    mainApp.pack(side="top", fill="both", expand=True)
    mainApp._update_loop()  # must be before main loop
    root.mainloop()

    # lifx = return_interface(num_lights)
    # devices = lifx.get_lights()
    # list_devices(devices)
    # blink_devices(devices)
