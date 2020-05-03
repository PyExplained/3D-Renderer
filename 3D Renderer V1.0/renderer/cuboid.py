from renderer.renderer import *

class Cuboid:
    def __init__(self, x1, y1, z1, x2, y2, z2, textures=[None for _ in range(6)],
                 fill=['red', 'pink', 'green', 'blue', 'purple', 'yellow'], alpha=[100 for n in range(6)],
                 x_angle=0, y_angle=0, z_angle=0):

        self.x, self.y, self.z = x1 + abs(x1 - x2) / 2, y1 + abs(y1 - y2) / 2, z1 + abs(z1 - z2) / 2

        self.prev_xangle, self.prev_yangle, self.prev_zangle = None, None, None

        self.visible = True
        self.plates = []
        self.plates.append(Plate([(x1, y1, z1), (x2, y2, z1)], texture=textures[0], fill=fill[0], orientation=1, alpha=alpha[0]))
        self.plates.append(Plate([(x1, y1, z2), (x2, y2, z2)], texture=textures[1], fill=fill[1], orientation=1, alpha=alpha[1]))
        self.plates.append(Plate([(x1, y1, z1), (x1, y2, z2)], texture=textures[2], fill=fill[2], orientation=1, alpha=alpha[2]))
        self.plates.append(Plate([(x2, y1, z1), (x2, y2, z2)], texture=textures[3], fill=fill[3], orientation=1, alpha=alpha[3]))
        self.plates.append(Plate([(x1, y2, z1), (x2, y2, z2)], texture=textures[4], fill=fill[4], orientation=2, alpha=alpha[4]))
        self.plates.append(Plate([(x1, y1, z1), (x2, y1, z2)], texture=textures[5], fill=fill[5], orientation=2, alpha=alpha[5]))

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