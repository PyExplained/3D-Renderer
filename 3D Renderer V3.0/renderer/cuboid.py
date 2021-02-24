from renderer.renderer import *

class Cuboid(object_parent):
    def __init__(self, x1, y1, z1, x2, y2, z2, textures=[None for _ in range(6)],
                 fill=['red', 'pink', 'green', 'blue', 'purple', 'yellow'], alpha=[100 for n in range(6)],
                 x_angle=0, y_angle=0, z_angle=0, shading=False, outline=None, outline_thickness=1):
        self.shading = shading
        self.visible = True
        self.x, self.y, self.z = x1 + abs(x1 - x2) / 2, y1 + abs(y1 - y2) / 2, z1 + abs(z1 - z2) / 2
        self.prev_xangle, self.prev_yangle, self.prev_zangle = None, None, None
        self.xangle = x_angle
        self.yangle = y_angle
        self.zangle = z_angle
        self.plates = []

        self.plates.append(Plate([(x1, y1, z1), (x2, y2, z1)], texture=textures[0], fill=fill[0], orientation=1, alpha=alpha[0], shading=shading, outline=outline, outline_thickness=outline_thickness))
        self.plates.append(Plate([(x1, y1, z2), (x2, y2, z2)], texture=textures[1], fill=fill[1], orientation=1, alpha=alpha[1], shading=shading, outline=outline, outline_thickness=outline_thickness))
        self.plates.append(Plate([(x1, y1, z1), (x1, y2, z2)], texture=textures[2], fill=fill[2], orientation=1, alpha=alpha[2], shading=shading, outline=outline, outline_thickness=outline_thickness))
        self.plates.append(Plate([(x2, y1, z1), (x2, y2, z2)], texture=textures[3], fill=fill[3], orientation=1, alpha=alpha[3], shading=shading, outline=outline, outline_thickness=outline_thickness))
        self.plates.append(Plate([(x1, y2, z1), (x2, y2, z2)], texture=textures[4], fill=fill[4], orientation=2, alpha=alpha[4], shading=shading, outline=outline, outline_thickness=outline_thickness))
        self.plates.append(Plate([(x1, y1, z1), (x2, y1, z2)], texture=textures[5], fill=fill[5], orientation=2, alpha=alpha[5], shading=shading, outline=outline, outline_thickness=outline_thickness))

        self.rotate(x_angle, y_angle, z_angle)