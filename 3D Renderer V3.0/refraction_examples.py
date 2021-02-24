from renderer.renderer import *


# !: Press 'b' to start raytracing
# More info about methods and variables (including materials, etc.) in renderer-info.md


def checkerboard_pattern(instance, x, y, z):
    x /= 5
    z /= 5
    if (floor(x) + floor(z) % 2) % 2:
        # instance.transparency = 0
        # instance.shadows = 100
        # instance.transparency = 85
        # instance.shadows = 10
        # instance.ior = 1.5
        # instance.thickness = 1
        return [255, 255, 255]
    else:
        # instance.transparency = 85
        # instance.shadows = 10
        # instance.ior = 1
        return [50, 50, 50]


# Functions of basic-renderer are explained in example_scene.py
init_window('RaytracingTest', 1280, 720)
change_background_color('RaytracingTest', 'grey20')

camera = Camera(0, 0, -2, resolution=(100, 100))
# camera.rotate(0, 180, 0)
camera.displaying = "RaytracingTest"
camera.on()
# camera.visible = True
# camera.box_size = 2

l = Light(-4, 7, 5, brightness=30, color=[255, 255, 255])
# l.visible = True
# l.box_size = 2
# l.off()

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

cube = Cube(0, 0, 5, size=3)
cube.rotate(45, 45, 45)
# cube.change_var('shadows', 20)
# cube.change_var('transparency', 85)
# cube.change_var('ior', 1.5)
# cube.change_var('volume', True)
# cube.change_var('project_color', 50)

# cube2 = Cube(0, 0, -5, size=2)
# cube2.change_var('reflectiveness', 40)
# cube.change_var('shadows', 10)
# cube2.rotate(90, 90, 0)
# cube2.rotate(15, 90, 0)

# Cuboid 'filled with water' (like glass, but refractive index of water) with 'stick'
# cuboid = Cuboid(-2, -3, 3, 2, 3, 7)
# cuboid.change_var('shadows', 0)
# cuboid.change_var('transparency', 95)
# cuboid.change_var('ior', 1.5)
# cuboid.change_var('volume', True)
# cuboid.change_var('project_color', 50)
# stick = Cuboid(-0.3, -5, 4.7, 0.3, 5, 5.3)
# stick.rotate(30, 0, 0)
# stick.rotate(0, 45, 0)

# Ground plane
ground = Plate([(-15, -4, -10), (15, -4, 20)], fill='grey75', orientation=2)
# ground.getColor = checkerboard_pattern
# ground.unbounded = True
# ground.shadows = 0

plate = Plate([(-5, -4, 2), (5, 5, 2)], fill='blue')
plate.reflectiveness = 0
plate.transparency = 60
plate.ior = 1.5
plate.shadows = 40
plate.volume = False
plate.thickness = 1

# plate.roughness = 20  # Rough surfaces and blurry refraction / reflections, makes it look translucent
# plate.num_ray_splits = 6  # More samples (only for roughness)

plate2 = Plate([(-2, -2, 0), (2, 2, 0)], fill='green')
plate2.reflectiveness = 0
plate2.transparency = 50
plate2.ior = 1.5
plate2.shadows = 30
plate2.volume = False
plate2.thickness = 1

# Transparent sphere
# sphere = Sphere(0, 0, 0, radius=2, fill=[0, 0, 100])
# sphere.shadows = 0
# sphere.transparency = 85
# sphere.ior = 1.5
# sphere.volume = True
# sphere.project_color = 50

while True:
    controller.check_events()

    if controller.b_down:
        set_variable(mouse_reset_pos=None)
        mainloop(rayTrace=True, camera=camera, output='output.jpg',
                 preview_mode='REFINE_SCANNER', update_frequency_in_pixels=500, max_bounces=3,
                 resize=True, add_RGB=1)
        # preview_mode = 'REFINE', 'SCANNER', 'REFINE_SCANNER' or None
        # (speed: fastest --> None > REFINE > SCANNER > REFINE_SCANNER <-- slowest), the higher update freq, the slower

        # Second camera example (you do have to add one for this to work):
        # mainloop(rayTrace=True, camera=camera2, output='output2.jpg',
        #          preview_mode='REFINE_SCANNER', update_frequency_in_pixels=500, max_bounces=0, resize=True)

        freeze_update(infinite=True)
    else:
        mainloop()
