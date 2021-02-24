from renderer.renderer import *


class Cube(object_parent):
    def __init__(self, x, y, z, size=1, textures=[None for _ in range(6)], resolution=1,
                 fill=['red', 'pink', 'green', 'blue', 'purple', 'yellow'], alpha=[100 for n in range(6)],
                 x_angle=0, y_angle=0, z_angle=0, shading=False, outline=None, outline_thickness=1):
        self.visible = True
        self.shading = shading
        self.size = size
        self.x, self.y, self.z = x, y, z
        self.prev_xangle, self.prev_yangle, self.prev_zangle = None, None, None
        self.xangle = x_angle
        self.yangle = y_angle
        self.zangle = z_angle

        x -= size / 2
        y -= size / 2
        z -= size / 2

        self.plates = []
        self.plates.append(Plate([(x, y, z), (size + x, size + y, z)], shading=shading,
                                 texture=textures[0], fill=fill[0], orientation=1, resolution=resolution, alpha=alpha[0],
                                 outline=outline, outline_thickness=outline_thickness))
        self.plates.append(Plate([(x, y, size + z), (size + x, size + y, size + z)], shading=shading,
                                    texture=textures[1], fill=fill[1], orientation=1, resolution=resolution, alpha=alpha[1],
                                    outline=outline, outline_thickness=outline_thickness))
        self.plates.append(Plate([(x, y, z), (x, size + y, size + z)], shading=shading,
                                 texture=textures[2], fill=fill[2], orientation=1, resolution=resolution, alpha=alpha[2],
                                 outline=outline, outline_thickness=outline_thickness))
        self.plates.append(Plate([(size + x, y, z), (size + x, size + y, size + z)], shading=shading,
                                 texture=textures[3], fill=fill[3], orientation=1, resolution=resolution, alpha=alpha[3],
                                 outline=outline, outline_thickness=outline_thickness))
        self.plates.append(Plate([(x, size + y, z), (size + x, size + y, size + z)], shading=shading,
                                 texture=textures[4], fill=fill[4], orientation=2, resolution=resolution, alpha=alpha[4],
                                 outline=outline, outline_thickness=outline_thickness))
        self.plates.append(Plate([(x, y, z), (size + x, y, size + z)], shading=shading,
                                 texture=textures[5], fill=fill[5], orientation=2, resolution=resolution, alpha=alpha[5],
                                 outline=outline, outline_thickness=outline_thickness))

        self.rotate(x_angle, y_angle, z_angle)
