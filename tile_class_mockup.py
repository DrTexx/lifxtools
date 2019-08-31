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
frame_1 = TileFrame(x_size,y_size)
frame_2 = TileFrame(x_size,y_size)

frame_1.print_frame() # print frame data to CLI
frame_2.print_frame() # print frame data to CLI

# set a each pixel of frame based on these conditions
for y in range(frame_1.y_size):
    for x in range(frame_1.x_size):
        if (y % 2 == 0):
            if (x % 2 == 0):
                frame_1.set_pixel(x,y,color_a)

# set a each pixel of frame based on these conditions
for y in range(frame_2.y_size):
    for x in range(frame_2.x_size):
        if not (y % 2 == 0):
            if not (x % 2 == 0):
                frame_2.set_pixel(x,y,color_a)

frame_1.print_frame() # print frame data to CLI
frame_2.print_frame() # print frame data to CLI

frames = [frame_1, frame_2]

# ---- lifx ----
lifx = lifxlan.LifxLAN()
tilechains = lifx.get_tilechain_lights()

# tilechain.set_tile_colors(start_index, colors, [duration], [tile_count], [x], [y], [width], [rapid])

while True:
    for frame in frames:
        for tilechain in tilechains:
            tilechain.set_tile_colors(0, frame.return_frame(), 0, rapid=True)
        sleep(0.1)
