from renderer.renderer import *

class Light:
    def __init__(self, x, y, z, brightness=50, color=[255, 255, 255], x_angle=0, y_angle=0, z_angle=0):
        self.prev_xangle, self.prev_yangle, self.prev_zangle = None, None, None
        self.xangle = x_angle
        self.yangle = y_angle
        self.zangle = z_angle

        rend_info['LIGHTS'].append(self)

        self.x, self.y, self.z = x, y, z
        self.is_on = True
        self.visible = False
        self.brightness = brightness
        self.color = color

        self.rotate(x_angle, y_angle, z_angle)

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

            center = [self.x, self.y, self.z] if center == 'self' else center
            self.x, self.y, self.z = rotate([self.x, self.y, self.z], self.xrot, self.yrot, self.zrot, center=np.array([center[0],
                                                                                            -center[1],
                                                                                            center[2]]))

    def delete(self):
        del rend_info['LIGHTS'][rend_info['LIGHTS'].index(self)]
