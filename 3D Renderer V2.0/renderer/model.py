from renderer.renderer import *
import trimesh

class Model(object_parent):
    def __init__(self, x, y, z, path, size=1, fill='blue', outline=None, outline_thickness=1, alpha=100,
                 x_angle=0, y_angle=0, z_angle=0, shading=False, recenter=True):
        self.visible = True
        self.shading = shading
        self.size = size
        self.plates = []
        self.x, self.y, self.z = x, y, z
        self.prev_xangle, self.prev_yangle, self.prev_zangle = None, None, None
        self.xangle = x_angle
        self.yangle = y_angle
        self.zangle = z_angle

        mesh = trimesh.load(path)
        if recenter:
            mesh.vertices -= mesh.center_mass
        for tri in mesh.triangles:
            self.plates.append(Plate(tri * size + np.array([x, y, z]), fill=fill, alpha=alpha, smart_coords=False,
                               shading=shading, outline=outline, outline_thickness=outline_thickness))

        self.rotate(x_angle, y_angle, z_angle)