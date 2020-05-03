from renderer.renderer import *

class Camera:
    def __init__(self, x, y, z):
        rend_info['CAMERAS'].append(self)

        self.x, self.y, self.z = x, y, z
        self.prev_xangle, self.prev_yangle, self.prev_zangle = None, None, None
        self.xangle, self.yangle, self.zangle = 0, 0, 0
        self.displaying = False
        self.is_on = False
        self.visible = False

        self.draw = []
        self.glob_coords = {}

        self.oro_x, self.oro_y, self.oro_z = x, y, z

    def reset(self):
        self.x, self.y, self.z = self.oro_x, self.oro_y, self.oro_z
        self.xangle, self.yangle, self.zangle = 0, 0, 0

    def on(self):
        self.is_on = True

    def off(self):
        self.is_on = False

    def move(self, x, y, z):
        self.x += x
        self.y += y
        self.z += z

    def rotate(self, x_angle, y_angle, z_angle, center='self'):
        self.xangle -= x_angle
        self.yangle -= y_angle
        self.zangle -= z_angle

        if (x_angle, y_angle, z_angle) != (0, 0, 0) and center != 'self':
            if ((self.prev_xangle, self.prev_yangle, self.prev_zangle) != (x_angle, y_angle, z_angle)):
                self.xrot, self.yrot, self.zrot = calc_matrixes(x_angle, y_angle, z_angle)
                self.prev_xangle, self.prev_yangle, self.prev_zangle = x_angle, y_angle, z_angle

            self.x, self.y, self.z = rotate([self.x, self.y, self.z], self.xrot, self.yrot, self.zrot,
                                            center=np.array([center[0],
                                                             -center[1],
                                                             center[2]]))
