import lifxtools
import numpy as np
import lifxlan
from time import sleep

# ---- classes ----

class TileFrame:

    def __init__(self,x_size,y_size):
        self.x_size = x_size
        self.y_size = y_size
        self.frame = self._gen_empty_frame()

    def _gen_empty_frame(self):
        empty_frame = np.zeros((self.x_size,self.y_size), dtype=object)
        empty_color = (0,0,0,6500)

        for y in range(len(empty_frame)):
            for x in range(len(empty_frame[y])):
                empty_frame[x][y] = empty_color

        return(empty_frame)

    def set_pixel(self,x,y,color):
        self.frame[x][y] = color

    def print_frame(self):
        print(self.frame)

    def return_frame(self):
        frame = []
        for y in self.frame:
            for x in y:
                frame.append(x)
        return(frame)

# ---- settings (for script) ----

x_size, y_size = (8,8)
color_a = (0,65535,65535,6500)

# ---- script ----

# instantiate a frame object
frame1 = TileFrame(x_size,y_size)

# set a each pixel of frame based on these conditions
for y in range(frame1.y_size):
    for x in range(frame1.x_size):

        x_perc = x/frame1.x_size
        y_perc = y/frame1.y_size

        h = 65535 * x_perc
        s = 65535
        v = 65535 * y_perc
        k = 6500

        color = (h, s, v, k)
        frame1.set_pixel(x,y,color)

frame1.print_frame() # print frame data to CLI

frames = [frame1]

# ---- lifx ----
lifx = lifxlan.LifxLAN()
tilechains = lifx.get_tilechain_lights()

# tilechain.set_tile_colors(start_index, colors, [duration], [tile_count], [x], [y], [width], [rapid])

min_brightness = 0
max_brightness = 65535
segs_brightness = 20



while True:
    for frame in frames:
        for tilechain in tilechains:
            tilechain.set_tile_colors(0, frame.return_frame(), 0, rapid=True)
        sleep(0.1)
