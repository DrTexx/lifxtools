import numpy as np
import lifxlan

# ---- classes ----
class HSVKPixel:

    def __init__(self,hsvk_tuple):

        self.h, self.s, self.v, self.k = hsvk_tuple

    def write(self,hsvk_tuple):

        self.h, self.s, self.v, self.k = hsvk_tuple

    def read(self):

        return( (self.h, self.s, self.v, self.k) )

class ManagedTilechain:

    def __init__(self,TileChain_Object):
        self.TileChain = TileChain_Object
        self.size = TileChain_Object.get_canvas_dimensions()
        self.size_all_values = (self.size[0], self.size[1], 4)
        self.num_tiles = TileChain_Object.get_tile_count()
        self.off_pixel = (0,0,0,6500)
        self.canvas = self._gen_empty_frame()

    def _gen_empty_frame(self):

        empty_frame = np.full(self.size_all_values, self.off_pixel, dtype=object)

        return(empty_frame)

    def read_HSVK_2D(self):

        HSVK_list = []

        # for each cell of self.canvas
        for y in self.canvas:
            for x in y:
                # store the output of cell.read() in 1D array
                HSVK_list.append(x)

        # convert the 1D array to 2D (the third dimension is HSVK data)
        HSVK_2D = np.reshape(HSVK_list, (self.size[0], self.size[1], 4))

        return(HSVK_2D)

    def read_HSVK_tiles(self):

        HSVK_list = []

        # for each cell of self.canvas
        for y in self.canvas:
            for x in y:
                # store the output of cell.read() in 1D array
                HSVK_list.append(x)

        # convert the 1D array to a 2D array of 64 pixels per tile
        HSVK_tiles = np.reshape(HSVK_list, (self.num_tiles, 64, 4))

        return(HSVK_tiles)

# ---- script ----
if __name__ == "__main__":
    lifx = lifxlan.LifxLAN()
    tilechains = lifx.get_tilechain_lights()
    tilechain = tilechains[0]

    my_mtc = ManagedTilechain(tilechain)
    HSVK_list = my_mtc.read_HSVK_2D()
    print(HSVK_list)

    tilechain.set_tilechain_colors(HSVK_list,0,rapid=True)
