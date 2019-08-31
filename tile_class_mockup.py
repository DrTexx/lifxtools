import numpy as np

# ---- classes ----

class TileFrame:

    def __init__(self,x_size,y_size):
        self._x_size = x_size
        self._y_size = y_size
        self.frame = self._gen_empty_frame()

    def _gen_empty_frame(self):
        empty_frame = np.zeros((x_size,y_size), dtype=object)
        empty_color = (0,0,0,6500)

        for y in range(len(empty_frame)):
            for x in range(len(empty_frame[y])):
                empty_frame[x][y] = empty_color

        return(empty_frame)

    def set_pixel(self,x,y,color):
        self.frame[x][y] = color

    def print_frame(self):
        print(self.frame)

# ---- settings (for script) ----

x_size, y_size = (8,8)
color_a = (65535,65535,65535,6500)

# ---- script ----

# instantiate a frame object
my_frame = TileFrame(x_size,y_size)

# print new empty frame object
my_frame.print_frame()

# set a single pixel of frame
my_frame.set_pixel(0,0,color_a)

# print frame with set pixel
my_frame.print_frame()

# change pixel by access
my_frame.frame[0][1] = color_a

# print frame with set pixel
my_frame.print_frame()

# ---- lifx ----
