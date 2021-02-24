from renderer.renderer import *


# !: Press 'b' to start raytracing
# More info about methods and variables (including materials, etc.) in renderer-info.md


# def checkerboard_pattern(instance, x, y, z):
#     x /= 5
#     z /= 5
#     if (floor(x) + floor(z) % 2) % 2:
#         instance.reflectiveness = 0  # Change material-properties of tiles
#         instance.shadows = 100
#         return [255, 255, 255]
#     else:
#         instance.reflectiveness = 85
#         instance.shadows = 10
#         return [50, 50, 50]


# Functions of basic-renderer are explained in example_scene.py
init_window('RaytracingTest', 1280, 720)
change_background_color('RaytracingTest', 'grey20')

camera = Camera(0, 0, 0, resolution=(100, 100))
camera.displaying = "RaytracingTest"
camera.on()
# camera.visible = True
# camera.box_size = 2

l = Light(-3, 10, 3, brightness=30, color=[255, 255, 255])
# l.off()
l.visible = True
# l.box_size = 2

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

# cube = Cube(0, 0, 5, size=2)
cube = Cube(3, 0, 5, size=3)
cube.rotate(45, 45, 45)
cube.change_var('reflectiveness', 40)
cube.change_var('shadows', 10)

cube2 = Cube(3, 0, -3, size=4)
cube2.change_var('reflectiveness', 40)
cube2.change_var('shadows', 10)
cube2.rotate(90, 90, 0)

# Ground plane
ground = Plate([(-15, -4, -10), (15, -4, 20)], fill='grey75', orientation=2)
# ground.getColor = checkerboard_pattern
# ground.unbounded = True

ground.reflectiveness = 50  # 50% reflective
ground.shadows = 50
# ground.roughness = 5  # Rough surfaces and blurry reflections / refraction
# ground.num_ray_splits = 5  # More samples (only for roughness)

sphere = Sphere(-7, 0, 1, radius=2, fill=[0, 0, 100])
sphere.reflectiveness = 50
sphere.shadows = 0

# Reflective mirror-chamber
# chamber = Cube(0, 0, 0, size=10, fill=['white']*6)
# chamber.change_var('reflectiveness', 100)
# chamber.change_var('shadows', 0)

while True:
    controller.check_events()

    if controller.b_down:
        set_variable(mouse_reset_pos=None)
        mainloop(rayTrace=True, camera=camera, output='output.jpg',
                 preview_mode='REFINE_SCANNER', update_frequency_in_pixels=500, max_bounces=3,
                 resize=True, add_RGB=1)  # add_rgb so objects aren't not 100% absorbent
        # preview_mode = 'REFINE', 'SCANNER', 'REFINE_SCANNER' or None
        # (speed: fastest --> None > REFINE > SCANNER > REFINE_SCANNER <-- slowest), the higher update freq, the slower

        # Second camera example (you do have to add one for this to work):
        # mainloop(rayTrace=True, camera=camera2, output='output2.jpg',
        #          preview_mode='REFINE_SCANNER', update_frequency_in_pixels=500, max_bounces=0, resize=True)

        freeze_update(infinite=True)
    else:
        mainloop()
