from renderer.renderer import *

class Sphere:
    def __init__(self, x, y, z, radius=1, fill='blue',
                 shading=False, outline=None, outline_thickness=1):
        self.visible = True
        self.ray_tracer_visible = True
        self.shading = shading
        self.radius = radius
        self.fill = fill
        self.outline = outline
        self.outline_thickness = outline_thickness
        self.x, self.y, self.z = x, y, z
        self.is_camera_box = False

        self.shadows = 100
        self.roughness = 0
        self.num_ray_splits = 1
        self.reflectiveness = 0
        self.transparency = 0
        self.ior = 1
        self.volume = False
        self.thickness = 1
        self.project_color = 100

        if type(self.fill) == list or type(self.fill) == tuple or type(self.fill) == np.ndarray:
            self.fill = color2hex(*self.fill)  # RGB to HEX

        self.plate_indicator = Plate([(self.x, self.y, self.z)], smart_coords=False, fill=self.fill, outline=self.outline,
                                     outline_thickness=self.outline_thickness, radius=self.radius, shading=self.shading)
        self.plate_indicator.is_sphere_indicator = True
        self.plate_indicator.visible = self.visible
        self.plate_indicator.ray_tracer_visible = self.ray_tracer_visible

        rend_info['SPHERES'].append(self)

    def find_intersection(self, rayDirection, rayPoint, max_distance, record_distance, except_):
        center = np.array([self.x, -self.y, self.z])
        t = np.dot(center - rayPoint, rayDirection)
        p = rayPoint + rayDirection * t
        y = np.linalg.norm(center - p)
        if y <= self.radius:
            x = sqrt(self.radius ** 2 - y ** 2)
            t1 = t - x
            t2 = t + x
            p1 = rayPoint + rayDirection * t1
            p2 = rayPoint + rayDirection * t2
            hit_points = [p1, p2]
            record_point = None
            for point in hit_points:
                distance = np.linalg.norm(point - rayPoint)
                not_same_point = not (self == except_ and distance < 10 ** -10)
                if distance <= max_distance and np.linalg.norm(rayPoint - point) < record_distance \
                        and not_same_point and not (point - rayPoint).dot(
                        rayDirection) < 0:
                    record_point = point
                    record_distance = distance

            if record_point is not None:
                return record_point, record_distance

        return None, None  # Return None when there's no intersection

    def delete(self):
        self.plate_indicator.delete()
        del rend_info['SPHERES'][rend_info['SPHERES'].index(self)]

    def make_visible(self):
        self.visible = True
        self.plate_indicator.make_visible()

    def make_invisible(self):
        self.visible = False
        self.plate_indicator.make_invisible()

    def move(self, x, y, z):
        self.x += x
        self.y += y
        self.z += z
        self.plate_indicator.move(x, y, z)

    def getColor(self, instance, x, y, z):
        return self.fill
