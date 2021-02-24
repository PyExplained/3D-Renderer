from renderer.renderer import *


class object_parent:
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


    def change_var(self, var_name, value):
        for p in self.plates:
            setattr(p, var_name, value)


    def move(self, x, y, z):
        self.x += x
        self.y += y
        self.z += z

        for p in self.plates:
            p.move(x, -y, z)


    def rotate(self, x_angle, y_angle, z_angle, center='self'):
        self.xangle -= x_angle
        self.yangle -= y_angle
        self.zangle -= z_angle

        if abs(x_angle) + abs(y_angle) + abs(z_angle) != 0:
            if ((self.prev_xangle, self.prev_yangle, self.prev_zangle) != (x_angle, y_angle, z_angle)):
                self.xrot, self.yrot, self.zrot = calc_matrixes(x_angle, y_angle, z_angle)
                self.prev_xangle, self.prev_yangle, self.prev_zangle = x_angle, y_angle, z_angle

            if center != 'self':
                prev_x, prev_y, prev_z = self.x, self.y, self.z
                self.x, self.y, self.z = rotate([self.x, self.y, self.z], self.xrot, self.yrot, self.zrot,
                                                center=np.array([center[0],
                                                                 -center[1],
                                                                 center[2]]))
                diff_x, diff_y, diff_z = self.x - prev_x, self.y - prev_y, self.z - prev_z

            ori_cent = center
            center = [self.x, self.y, self.z]
            for p in self.plates:
                if ori_cent != 'self':
                    p.move(diff_x, diff_y, diff_z)
                p.rotate(x_angle, y_angle, z_angle, center, self.xrot, self.yrot, self.zrot)