from renderer.renderer import *
from statistics import *
import cv2


class Plate:
    def __init__(self, co, texture=None, resolution=1, fill='blue', smart_coords=True, orientation=1, alpha=100):
        self.fill = fill
        self.alpha = alpha
        self.visible = True
        if not self.alpha in [25, 50, 75, 100]:
            raise ValueError('Alpha value should be 25, 50, 75 or 100. Not ' + str(self.alpha))

        self.prev_xangle, self.prev_yangle, self.prev_zangle = None, None, None

        n_co = []
        for p in co:
            n_co.append((p[0], -p[1], p[2]))
        co = n_co

        if not texture:
            rend_info['PLATES'].append(self)

        if smart_coords:
            (self.x1, self.y1, self.z1), (self.x2, self.y2, self.z2) = co[0], co[1]
            if smart_coords:
                if orientation == 1:
                    self.co = [(self.x2, self.y1, self.z2),
                               (self.x2, self.y2, self.z2),
                               (self.x1, self.y2, self.z1),
                               (self.x1, self.y1, self.z1)]
                elif orientation == 2:
                    self.co = [(self.x1, self.y1, self.z2),
                               (self.x2, self.y2, self.z2),
                               (self.x2, self.y2, self.z1),
                               (self.x1, self.y1, self.z1)]
        else:
            self.co = co
        self.smart_coords = smart_coords

        if texture:
            img = cv2.imread(texture)
            step_size = round(1 / resolution)
            if abs(self.y1 - self.y2) > 0 and abs(self.z1 - self.z2):
                pix_dir = 'x'
                pix_w = abs(self.z1 - self.z2) / len(img[0])
                pix_h = abs(self.y1 - self.y2) / len(img)
            elif abs(self.x1 - self.x2) > 0 and abs(self.z1 - self.z2):
                pix_dir = 'y'
                pix_w = abs(self.x1 - self.x2) / len(img[0])
                pix_h = abs(self.z1 - self.z2) / len(img)
            elif abs(self.x1 - self.x2) > 0 and abs(self.y1 - self.y2):
                pix_dir = 'z'
                pix_w = abs(self.x1 - self.x2) / len(img[0])
                pix_h = abs(self.y1 - self.y2) / len(img)
            self.y1 *= -1
            for c1 in range(0, len(img), step_size):
                for c2 in range(0, len(img[0]), step_size):
                    b, g, r = img[len(img) - c1 - 1][c2]
                    if pix_dir == 'x':
                        Plate([(self.x1, self.y1 + c2 * pix_h, self.z1 + c1 * pix_w),
                               (self.x1, self.y1 + c2 * pix_h + pix_h * step_size,
                                self.z1 + c1 * pix_w + pix_w * step_size)],
                              fill='#{:02x}{:02x}{:02x}'.format(r, g, b), smart_coords=True, orientation=orientation)
                    elif pix_dir == 'y':
                        Plate([(self.x1 + c1 * pix_w, self.y1, self.z1 + c2 * pix_h),
                               (self.x1 + c1 * pix_w + pix_w * step_size, self.y1,
                                self.z1 + c2 * pix_h + pix_h * step_size)],
                              fill='#{:02x}{:02x}{:02x}'.format(r, g, b), smart_coords=True, orientation=orientation)
                    elif pix_dir == 'z':
                        Plate([(self.x1 + c2 * pix_w, self.y1 + c1 * pix_h, self.z1),
                               (self.x1 + c2 * pix_w + pix_w * step_size, self.y1 + c1 * pix_h + pix_h * step_size,
                                self.z1)],
                              fill='#{:02x}{:02x}{:02x}'.format(r, g, b), smart_coords=True, orientation=orientation)

        self.share_coords()

    def update(self, camera):
        res = []
        for pp in self.co:
            try:
                res.append(camera.glob_coords[pp])
            except KeyError:
                pass
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

        if ((max(x_list) > width and min(x_list) < 0) or (
                max(y_list) > height and min(y_list) < 0)) and min(
            z_list) < 0:
            zz = [False, False, False, False]

        if zz.count(False) < len(self.co):
            self.init_draw(camera, mean(z_list), final_list, True)
        else:
            self.init_draw(camera, mean(z_list), final_list, False)

    def init_draw(self, camera, co1, co2, dr):
        if dr:
            camera.draw.append([co1, co2, self.fill, self.alpha])

    def share_coords(self):
        for c in rend_info['CAMERAS']:
            for p in self.co:
                c.glob_coords[p] = None

    def delete(self):
        del rend_info['PLATES'][rend_info['PLATES'].index(self)]

    def make_visible(self):
        self.visible = True

    def make_invisible(self):
        self.visible = False

    def rotate(self, x_angle, y_angle, z_angle, center, xrot, yrot, zrot):
        import renderer.renderer as rn

        self.xrot, self.yrot, self.zrot = xrot, yrot, zrot

        if (x_angle, y_angle, z_angle) != (0, 0, 0):
            if np.all(xrot == None) and np.all(xrot == None) and np.all(xrot == None) and \
                    ((self.prev_xangle, self.prev_yangle, self.prev_zangle) != (x_angle, y_angle, z_angle)):
                self.xrot, self.yrot, self.zrot = calc_matrixes(x_angle, y_angle, z_angle)
                self.prev_xangle, self.prev_yangle, self.prev_zangle = x_angle, y_angle, z_angle

            for i, p in enumerate(self.co):
                self.co[i] = tuple(rotate(p, self.xrot, self.yrot, self.zrot, center=np.array(center)))
            rn.reshare = True
