from renderer.renderer import *
import random
import time

init_window("Renderer", 1280, 720)

camera = Camera(0, 0, 0)
camera.controllable = True
camera.displaying = True
camera.on()
camera.visible = True

camera = Camera(1, 1, 1)
camera.controllable = False
camera.displaying = False
camera.off()
camera.visible = True

cubes = []
size = 4
for x in range(size):
    for y in range(size):
        for z in range(size):
            colors = ['red', 'black', 'green', 'blue', 'purple', 'yellow']
            random.shuffle(colors)
            alpha = random.choice([25, 50, 75, 100])
            cube = Cube(size-2.5*x, size-2.5*y-3, size*3-2.5*z, size=1, fill=colors, alpha=[alpha for n in range(6)],
                         x_angle=random.randint(0, 360), y_angle=random.randint(0, 360), z_angle=random.randint(0, 360))
            cube.x_rotation = random.randint(-5, 5)
            cube.y_rotation = random.randint(-5, 5)
            cube.z_rotation = random.randint(-5, 5)
            cubes.append(cube)

# p = Plate([(4, -1, 4), (6, 1, 4), (6, -1, 4)], texture=None, fill='red', smart_coords=False, orientation=1)
# Plate([(-1, -1, 4), (1, 1, 4)], texture=None, fill='blue', smart_coords=True, orientation=1)
# Plate([(-5, -5, 10), (5, 5, 10)],
#       texture=r'img_path', resolution=0.035,
#       fill=None, smart_coords=True, orientation=1)
# Cube(5, 2, 5, size=1, fill=['red', 'black', 'green', 'blue', 'purple', 'yellow'])
c = Cuboid(10, 0, 0, 11, 1, 5, fill=['red', 'black', 'green', 'blue', 'purple', 'yellow'], x_angle=90)
c.x_rotation = random.randint(-5, 5)
c.y_rotation = random.randint(-5, 5)
c.z_rotation = random.randint(-5, 5)
cubes.append(c)

set_frame_interval(0)
set_fov(500)
last_time = time.time()
while True:
    for c in cubes:
        c.rotate(c.x_rotation, c.y_rotation, c.z_rotation)
        if random.uniform(0, 1) < 0.01 and type(c) != Cuboid:
            if c.visible:
                c.make_invisible()
            else:
                c.make_visible()

    if time.time() - last_time >= 1:
        give_fps()
        last_time = time.time()
    mainloop()
