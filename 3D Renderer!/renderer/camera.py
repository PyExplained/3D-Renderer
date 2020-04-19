from renderer.renderer import *

class Camera:
    def __init__(self, x, y, z):
        rend_info['CAMERAS'].append(self)

        self.x, self.y, self.z = x, y, z
        self.xangle, self.yangle, self.zangle = 0, 0, 0
        self.controllable = False
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