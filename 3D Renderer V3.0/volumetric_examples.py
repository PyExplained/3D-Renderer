# from matplotlib import colors
from renderer.renderer import *


# !: Press 'b' to start raytracing
# More info about methods and variables (including materials, etc.) in renderer-info.md


def hole(instance, x, y, z):
    # width = 20
    # height = 20
    # cx = 0
    # cy = 0
    # image = instance.image
    #
    # x = floor((x - cx + width / 2) / width * image.shape[1])
    # y = floor((y - cy + height / 2) / height * image.shape[0])
    #
    # if 0 <= x < image.shape[1] and 0 <= y < image.shape[0]:
    #     instance.transparency = 100 - np.mean(image[y, x]) / 2.55
    #     return image[y, x]

    holes = [[-2, 0, 1], [2, 0, 1]]  # [x, y, size]
    for cx, cy, s in holes:
        if cx-s/2 < x < cx+s/2 and cy-s/2 < y < cy+s/2:
            return None

    return instance.fill


# def rainbow(instance, x, y, z):
#     return colors.hsv_to_rgb([z / 20 % 1, 1, 1]) * 255  # Uncomment matplotlib import


def smoke(instance, x, y, z):
    # Sphere
    if np.linalg.norm(np.array([x, y, z]) - np.array([0, 0, 0])) <= 6:
        instance.density = 20
        return [175, 0, 0]
    else:
        instance.density = 0

    # Cube
    # if -7 <= x <= 7 and -7 <= y <= 7 and -7 <= z <= 7:
    #     instance.density = 10
    #     # return [255, 0, 0]
    # else:
    #     instance.density = 0

    # Rainbow Torus
    # inner_center = np.array([0, 0, 0])
    # inner_radius = 7
    # outer_radius = 2
    #
    # point = np.array([x, y, z]) - inner_center
    # if inner_radius - outer_radius <= np.linalg.norm(point[[0, 2]]) <= inner_radius + outer_radius:
    #     outer_center = point[[0, 2]] / np.linalg.norm(point[[0, 2]]) * inner_radius
    #     outer_center = np.array([outer_center[0], inner_center[1], outer_center[1]])
    #     if np.linalg.norm(point - outer_center) <= outer_radius:
    #         instance.density = 20
    #         # return [255, 0, 0]
    #         # return instance.fill
    #
    #         angle = atan2(*point[[0, 2]])
    #         return colors.hsv_to_rgb([(angle + pi) / (2 * pi), 1, 1]) * 255
    # instance.density = 0

    return instance.fill


# Functions of basic-renderer are explained in example_scene.py
init_window('RaytracingTest', 1280, 720)
change_background_color('RaytracingTest', 'grey20')

camera = Camera(0, 0, 0, resolution=(250, 200))
# camera.rotate(0, 180, 0)
camera.displaying = "RaytracingTest"
camera.on()
# camera.visible = True
# camera.box_size = 2
camera.volumetric_particle.density = 5
camera.volumetric_checks = 1  # Dust-collision-checks per distance-unit
# camera.volumetric_particle.fill = [255, 255, 255]
# camera.volumetric_particle.visible = True
# camera.volumetric_particle.getColor = smoke
# camera.volumetric_activated = True  # When density gets procedurally changed

# l = Light(0, 3, -7, brightness=100, color=[255, 255, 255])
# l.visible = True
# l.ray_tracer_visible = False

l = Light(-8, 8, 8, brightness=30, color=[255, 255, 255])
l.visible = True
l.ray_tracer_visible = False

# Spotlight
# l.direction = np.array([0, -1, 0])
# l.direction = rotate(np.array([0, -1, 0]), *calc_matrixes(0, 45, 0))  # Rotate certain amount
# l.direction = -np.array([l.x, l.y, l.z])  # Point to (0, 0, 0)
# l.direction = l.direction / np.linalg.norm(l.direction)
# l.lighting_angle = 10

controller = Controller(camera)
controller.bind('mouse_y', 'x_rotation', -0.5)
controller.bind('mouse_x', 'y_rotation', 0.5)
controller.bind('z', 'forward', 0.2)
controller.bind('q', 'left', 0.2)
controller.bind('s', 'backwards', 0.2)
controller.bind('d', 'right', 0.2)
controller.bind('Key.space', 'y', 0.2)
controller.bind('Key.shift', 'y', -0.2)
controller.notify('b', 'hold', 'b_down')

sphere = Sphere(0, 0, 0, radius=2, fill=[0, 0, 100])

# cube = Cube(0, 0, 7, size=20, fill=['grey50']*6)
# cube.change_var('unbounded', True)
# cube.change_var('project_color', 100)
# cube.plates[0].image = cv2.cvtColor(cv2.imread("test_img.png"), cv2.COLOR_BGR2RGB)
# cube.plates[0].getColor = hole

while True:
    controller.check_events()

    if controller.b_down:
        set_variable(mouse_reset_pos=None)
        mainloop(rayTrace=True, camera=camera, output='yt_outputs/output11_2.jpg',
                 preview_mode='REFINE', update_frequency_in_pixels=500, max_bounces=3,
                 resize=True, add_RGB=1)
        # preview_mode = 'REFINE', 'SCANNER', 'REFINE_SCANNER' or None
        # (speed: fastest --> None > REFINE > SCANNER > REFINE_SCANNER <-- slowest), the higher update freq, the slower

        # Second camera example (you do have to add one for this to work):
        # mainloop(rayTrace=True, camera=camera2, output='output2.jpg',
        #          preview_mode='REFINE_SCANNER', update_frequency_in_pixels=500, max_bounces=0, resize=True)

        freeze_update(infinite=True)
    else:
        mainloop()
