from renderer.renderer import *
import random
import time

# !: Things that are commented out (other than comments that explain stuff) are examples of what you can do.
#    You can 'uncomment' them to see what they do. The explanation is above the block of code.

# Initialize window (window-name, width, height)
init_window("Window1", 1280, 720)
# init_window("Window2", 500, 500)

change_background_color('Window1', 'black')
# change_background_color('Window2', 'black')
# change_cursor('Window1', 'crosshair')  # Change cursor to one Tkinter's builtin cursors

# 2 Camera Example
camera = Camera(0, 0, -3)
camera.displaying = "Window1"  # (window-name)
camera.on()
camera.visible = True

# camera2 = Camera(1, 1, 1)
# camera2.displaying = "Window2"
# camera2.on()  # To display, it needs to be on
# camera2.visible = True

rotating = []

# "Cube of rotating cubes"
size = 4
for x in range(size):
    for y in range(size):
        for z in range(size):
            colors_ = ['red', 'black', 'green', 'blue', 'purple', 'yellow']
            random.shuffle(colors_)
            alpha = random.choice([25, 50, 75, 100])  # Random transparency
            cube = Cube(size-2.5*x, size-2.5*y-3, size*3-2.5*z, size=1, fill=colors_, alpha=[alpha for n in range(6)],
                         x_angle=random.randint(0, 360), y_angle=random.randint(0, 360), z_angle=random.randint(0, 360),
                        shading=True)
            cube.x_rotation = random.randint(-5, 5)
            cube.y_rotation = random.randint(-5, 5)
            cube.z_rotation = random.randint(-5, 5)
            rotating.append(cube)

# Examples of objects
# p = Plate([(4, -1, 0), (6, 1, 0), (6, -1, 4)], texture=None, fill='red', smart_coords=False, orientation=1)
# Plate([(-1, -1, 0), (1, 1, 0)], texture=None, fill='blue', smart_coords=True, orientation=1)
# Plate([(-15, -5, 15), (-5, 5, 15)],
#       texture=r'C:\Users\manud\OneDrive\Bureaublad\test_img.jpg', resolution=0.025,
#       fill=None, smart_coords=True, orientation=1)
# Cube(5, 2, -2, size=1, fill=['red', 'black', 'green', 'blue', 'purple', 'yellow'])

# 3D Model (only supports .STL)
# m = Model(0, 0, -1, 'rabbit.stl', fill='white', size=0.01, alpha=100, z_angle=-90, y_angle=90, shading=True, recenter=True)
# m.x_rotation = random.randint(-5, 5)
# m.y_rotation = random.randint(-5, 5)
# m.z_rotation = random.randint(-5, 5)
# rotating.append(m)

# Line and Point in 3D (Handy for debugging)
# Plate([(-1, 0, 1), (1, 1, 1.5)], smart_coords=False, outline='white', outline_thickness=1)
# Plate([(3, 1, 1)], smart_coords=False, outline='blue', outline_thickness=3)

# Light (is needed to see objects if shading is activated)
hue = 0
hue_add = 0.03  # Disco light
l = Light(0, -3, -1, brightness=250, color=[255, 255, 255])
l.visible = True

# Controller object (is needed to control camera)
controller = Controller(camera)
controller.bind('mouse_y', 'x_rotation', -0.5)
controller.bind('mouse_x', 'y_rotation', 0.5)
controller.bind('w', 'forward', 0.5)
controller.bind('a', 'left', 0.5)
controller.bind('s', 'backwards', 0.5)
controller.bind('d', 'right', 0.5)
controller.bind('Key.space', 'y', 0.5)
controller.bind('Key.shift', 'y', -0.5)
# controller.notify('a', 'toggle', 'test')  # key, toggle or hold, variable name (to see value of variable, use
                                                                                # controller.test)

# Rotating Cuboid
# c = Cuboid(10, 0, 0, 11, 1, 5, fill=['red', 'black', 'green', 'blue', 'purple', 'yellow'], x_angle=90)
# c.x_rotation = random.randint(-5, 5)
# c.y_rotation = random.randint(-5, 5)
# c.z_rotation = random.randint(-5, 5)
# rotating.append(c)

# Renderer Constants (fov is more like zoom, not really field of view)
set_variable(sleep_time=0, pause_color='gray70')

import renderer.renderer as rn
last_time = time.time()
while True:
    if not rn.pause:
        # Let light rotate around cubes
        l.rotate(0, 5, 0, center=[0, 0, 8])

        for c in rotating:
            # Random movement
            # c.move(random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1))

            # Rotation on 3 axis
            c.rotate(c.x_rotation, c.y_rotation, c.z_rotation)  # You can add: center=[x, y, z] to rotate round that point

            # Random appearing and disappearing
            # if random.uniform(0, 1) < 0.01 and type(c) != Cuboid:
            #     if c.visible:
            #         c.make_invisible()
            #     else:
            #         c.make_visible()

        # Random light flickering, only works when there is a light in the scene
        # if random.uniform(0, 1) < 0.2:
        #     if l.is_on:
        #         l.off()
        #     else:
        #         l.on()

        # Disco Light
        if hue < 0 or hue > 1:
            hue_add *= -1
            hue = 0

        l.color = np.array(colors.hsv_to_rgb([hue, 1, 1])) * 255
        hue += hue_add

    controller.check_events()

    # Print fps
    if time.time() - last_time >= 1:
        give_fps()
        last_time = time.time()

    mainloop()