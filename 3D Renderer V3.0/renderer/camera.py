from renderer.renderer import *

class Camera:
    def __init__(self, x, y, z, resolution=(20, 20), fov=3):
        rend_info['CAMERAS'].append(self)

        self.x, self.y, self.z = x, y, z
        self.prev_xangle, self.prev_yangle, self.prev_zangle = None, None, None
        self.xangle, self.yangle, self.zangle = 0, 0, 0
        self.displaying = False
        self.is_on = False
        self.visible = False
        self.ray_tracer_visible = False
        self.box_size = 5

        self.resolution = resolution
        self.fov = fov
        self.volumetric_checks = 1  # Dust-collision-checks per distance-unit
        self.max_volumetric_distance = 50
        self.volumetric_particle = DustParticle(fill=[150, 150, 155], density=0)
        self.volumetric_activated = False  # Set to True if density gets procedurally changed from 0 to other values!

        self.hdri = None

        self.photo = None
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

    def init_frame(self, width, height, return_=False):
        self.color = rend_info["WINDOWS"][self.displaying][1]["background"]
        if type(self.color) == str:
            self.color = np.array(rend_info["WINDOWS"][self.displaying][1].winfo_rgb(self.color)) / 257
        rend_info["WINDOWS"][self.displaying][1].color = self.color

        if return_:
            return np.full((height, width, 3), 255)
        else:
            self.frame = np.full((height, width, 3), 255)
            self.frame_filled_in = np.zeros((height, width), dtype=np.bool)

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
