from renderer.renderer import *

class Cube:
    def __init__(self, x, y, z, size=1, textures=[None for _ in range(6)], resolution=1,
                 fill=['red', 'pink', 'green', 'blue', 'purple', 'yellow'], alpha=[100 for n in range(6)],
                 x_angle=0, y_angle=0, z_angle=0):
        self.visible = True
        self.size = size
        self.x, self.y, self.z = x, y, z
        self.prev_xangle, self.prev_yangle, self.prev_zangle = None, None, None

        x -= size / 2
        y -= size / 2
        z -= size / 2

        self.plates = []
        self.plates.append(Plate([(x, y, z), (size + x, size + y, z)],
                                 texture=textures[0], fill=fill[0], orientation=1, resolution=resolution, alpha=alpha[0]))
        self.plates.append(Plate([(x, y, size + z), (size + x, size + y, size + z)],
                                 texture=textures[1], fill=fill[1], orientation=1, resolution=resolution, alpha=alpha[1]))
        self.plates.append(Plate([(x, y, z), (x, size + y, size + z)],
                                 texture=textures[2], fill=fill[2], orientation=1, resolution=resolution, alpha=alpha[2]))
        self.plates.append(Plate([(size + x, y, z), (size + x, size + y, size + z)],
                                 texture=textures[3], fill=fill[3], orientation=1, resolution=resolution, alpha=alpha[3]))
        self.plates.append(Plate([(x, size + y, z), (size + x, size + y, size + z)],
                                 texture=textures[4], fill=fill[4], orientation=2, resolution=resolution, alpha=alpha[4]))
        self.plates.append(Plate([(x, y, z), (size + x, y, size + z)],
                                 texture=textures[5], fill=fill[5], orientation=2, resolution=resolution, alpha=alpha[5]))

        self.rotate(x_angle, y_angle, z_angle)

    def delete(self):
        for p in self.plates:
            p.delete()

    def make_visible(self):
        self.visible = True
        for p in self.plates:
            p.make_visible()

    def make_invisible(self):
        self.visible = False
        for p in self.plates:
            p.make_invisible()

    def rotate(self, x_angle, y_angle, z_angle):
        if (x_angle, y_angle, z_angle) != (0, 0, 0):
            if ((self.prev_xangle, self.prev_yangle, self.prev_zangle) != (x_angle, y_angle, z_angle)):
                self.xrot, self.yrot, self.zrot = calc_matrixes(x_angle, y_angle, z_angle)
                self.prev_xangle, self.prev_yangle, self.prev_zangle = x_angle, y_angle, z_angle

            for p in self.plates:
                p.rotate(x_angle, y_angle, z_angle, [self.x, -self.y, self.z], self.xrot, self.yrot, self.zrot)
