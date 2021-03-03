from renderer.renderer import *
import renderer.renderer as rn


class Plate:
    def __init__(self, co, texture=None, resolution=1, fill='blue', outline=None, outline_thickness=1, radius=0.1,
                 smart_coords=True, orientation=1, alpha=100, shading=False):
        self.shading = shading
        self.fill = fill
        self.outline = outline
        self.outline_thickness = outline_thickness
        self.radius = radius
        self.alpha = alpha
        self.visible = True
        self.ray_tracer_visible = True
        self.is_camera_box = False
        self.is_sphere_indicator = False
        self.xangle = 0
        self.yangle = 0
        self.zangle = 0

        # Ray-tracing
        self.shadows = 100
        self.unbounded = False
        self.roughness = 0
        self.num_ray_splits = 1
        self.reflectiveness = 0
        self.transparency = 0
        self.ior = 1
        self.volume = False
        self.thickness = 1
        self.project_color = 100

        if not self.alpha in [25, 50, 75, 100]:
            raise ValueError('Alpha value should be 25, 50, 75 or 100. Not ' + str(self.alpha))

        self.init_coords(co, texture, smart_coords, orientation, resolution)

        self.share_coords()

    def init_coords(self, co, texture, smart_coords, orientation, resolution):
        n_co = []
        for p in co:
            n_co.append((p[0], -p[1], p[2]))
        co = n_co

        if not texture:
            rend_info['PLATES'].append(self)

        self.co = co
        if smart_coords:
            x1, y1, z1, x2, y2, z2 = co[0] + co[1]
            if orientation == 1:
                self.co = [(x2, y1, z2),
                           (x2, y2, z2),
                           (x1, y2, z1),
                           (x1, y1, z1)]
            elif orientation == 2:
                self.co = [(x1, y1, z2),
                           (x2, y2, z2),
                           (x2, y2, z1),
                           (x1, y1, z1)]

        if texture:
            self.init_texture(texture, resolution, orientation, co)

    def init_texture(self, texture, resolution, orientation, *co):
        x1, y1, z1, x2, y2, z2 = co[0][0] + co[0][1]
        img = cv2.imread(texture)
        step_size = round(1 / resolution)
        if abs(y1 - y2) > 0 and abs(z1 - z2):
            pix_dir = 'x'
            pix_w = abs(z1 - z2) / len(img[0])
            pix_h = abs(y1 - y2) / len(img)
        elif abs(x1 - x2) > 0 and abs(z1 - z2):
            pix_dir = 'y'
            pix_w = abs(x1 - x2) / len(img[0])
            pix_h = abs(z1 - z2) / len(img)
        elif abs(x1 - x2) > 0 and abs(y1 - y2):
            pix_dir = 'z'
            pix_w = abs(x1 - x2) / len(img[0])
            pix_h = abs(y1 - y2) / len(img)
        y1 *= -1
        for c1 in range(0, len(img), step_size):
            for c2 in range(0, len(img[0]), step_size):
                b, g, r = img[len(img) - c1 - 1][c2]
                if pix_dir == 'x':
                    Plate([(x1, y1 + c2 * pix_h, z1 + c1 * pix_w),
                           (x1, y1 + c2 * pix_h + pix_h * step_size,
                            z1 + c1 * pix_w + pix_w * step_size)],
                          fill='#{:02x}{:02x}{:02x}'.format(r, g, b), smart_coords=True, orientation=orientation)
                elif pix_dir == 'y':
                    Plate([(x1 + c1 * pix_w, y1, z1 + c2 * pix_h),
                           (x1 + c1 * pix_w + pix_w * step_size, y1,
                            z1 + c2 * pix_h + pix_h * step_size)],
                          fill='#{:02x}{:02x}{:02x}'.format(r, g, b), smart_coords=True, orientation=orientation)
                elif pix_dir == 'z':
                    Plate([(x1 + c2 * pix_w, y1 + c1 * pix_h, z1),
                           (x1 + c2 * pix_w + pix_w * step_size, y1 + c1 * pix_h + pix_h * step_size,
                            z1)],
                          fill='#{:02x}{:02x}{:02x}'.format(r, g, b), smart_coords=True, orientation=orientation)

    def update(self, camera):
        res = []
        for i, pp in enumerate(self.co):
            # try:
            res.append(camera.glob_coords[pp])
        # except KeyError:
        #     pass
        zz = []
        x_list = []
        y_list = []
        z_list = []
        final_list = []
        for point in res:
            x_list.append(point[1][0])
            y_list.append(point[1][1])
            z_list.append(point[0])
            final_list.append(point[1])

        for i, c in enumerate(z_list):
            if c < 0:
                zz.append(False)
            else:
                zz.append(True)

        width = rend_info['WINDOWS'][camera.displaying][1].winfo_width() if camera.displaying else 1280
        height = rend_info['WINDOWS'][camera.displaying][1].winfo_height() if camera.displaying else 720
        if ((max(x_list) > width and min(x_list) < 0) or (max(y_list) > height and min(y_list) < 0)) and \
                min(z_list) < 0:
            zz = [False, False, False, False]

        if zz.count(False) < len(self.co):
            self.init_draw(camera, mean(z_list), final_list, True)
        else:
            self.init_draw(camera, mean(z_list), final_list, False)

    def init_draw(self, camera, co1, co2, dr):
        if dr:
            if type(self.fill) == str:
                self.fill = color2rgb(self.fill)

            if type(self.fill) in [list, tuple, np.ndarray]:
                color = self.fill.copy()
            else:
                color = self.fill
            if self.shading:
                light = False
                for l in rend_info['LIGHTS']:
                    if l.is_on:
                        light = True
                        distance = sqrt(
                            (l.x - self.co[0][0]) ** 2 + (-l.y - self.co[0][1]) ** 2 + (l.z - self.co[0][2]) ** 2)
                        color = (np.array(l.color) + np.array(color)) * l.brightness / (distance * 100)


                if not light:
                    color = [0, 0, 0]

            if type(color) == list or type(color) == tuple or type(color) == np.ndarray:
                color = color2hex(*color)  # RGB to HEX

            # camera.draw.append([co1, co2, color, self.alpha, self.is_camera_box, self.outline, self.width])
            camera.draw.append([co1, co2, color, self])

    def share_coords(self):
        if len(self.co) > 2:
            # Calculate normal
            A = np.array(self.co[1]) - np.array(self.co[0])
            B = np.array(self.co[2]) - np.array(self.co[0])
            Nx = A[1] * B[2] - A[2] * B[1]
            Ny = A[2] * B[0] - A[0] * B[2]
            Nz = A[0] * B[1] - A[1] * B[0]
            self.planeNormal = np.array([Nx, Ny, Nz])
            self.planeNormal = np.round(self.planeNormal / np.linalg.norm(self.planeNormal), 5)

        # Share coordinates
        for c in rend_info['CAMERAS']:
            for p in self.co:
                c.glob_coords[p] = None

    def delete(self):
        del rend_info['PLATES'][rend_info['PLATES'].index(self)]

    def make_visible(self):
        self.visible = True

    def make_invisible(self):
        self.visible = False

    def move(self, x, y, z):
        for i, p in enumerate(self.co):
            self.co[i] = tuple(np.array([x, y, z]) + np.array(self.co[i]))
        rn.app.reshare = True

    def rotate(self, x_angle, y_angle, z_angle, center, *rot):
        if rot:
            self.xrot, self.yrot, self.zrot = rot
        else:
            self.xrot, self.yrot, self.zrot = calc_matrixes(x_angle, y_angle, z_angle)

        if center == 'self':
            center = np.mean(self.co, axis=0)

        self.xangle -= x_angle
        self.yangle -= y_angle
        self.zangle -= z_angle

        if (x_angle, y_angle, z_angle) == (0, 0, 0):
            return

        for i, p in enumerate(self.co):
            self.co[i] = tuple(rotate(p, self.xrot, self.yrot, self.zrot, center=np.array([center[0],
                                                                                           -center[1],
                                                                                           center[2]])))
        rn.app.reshare = True

    def find_intersection(self, rayDirection, rayPoint, max_distance, record_distance, _):
        point = linePlaneIntersection(self.planeNormal, self.co[0], rayDirection, rayPoint)
        if not point is None and not (point - rayPoint).dot(rayDirection) < 0:
            distance = np.linalg.norm(rayPoint - point)
            if distance <= max_distance and distance < record_distance:
                if self.unbounded:
                    return point, distance
                else:
                    # 2D coordinates, drop one axis (depending on plate rotation)
                    if np.argmax(abs(self.planeNormal)) == 2:
                        plate_2d = [co[:2] for co in self.co]
                        point_2d = point[:2]
                    elif np.argmax(abs(self.planeNormal)) == 0:
                        plate_2d = [co[1:] for co in self.co]
                        point_2d = point[1:]
                    else:
                        plate_2d = [np.array(co)[[0, 2]] for co in self.co]
                        point_2d = point[[0, 2]]

                    # Inside of plate?
                    if check_inside_shape(point_2d, np.round(plate_2d, 5)):
                        return point, distance

        return None, None  # Return None when there's no intersection

    def getColor(self, instance, x, y, z):
        return self.fill
