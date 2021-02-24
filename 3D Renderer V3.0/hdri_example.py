from renderer.renderer import *


# !: Press 'b' to start raytracing
# More info about methods and variables (including materials, etc.) in renderer-info.md


init_window('RaytracingTest', 1280, 720)
change_background_color('RaytracingTest', 'grey20')

camera = Camera(0, 0, 0, resolution=(100, 100))  # Resolution is only for ray tracing
camera.displaying = "RaytracingTest"
camera.on()
# camera.visible = True
# camera.box_size = 2
camera.hdri = rayTracer.load_hdri(r"insert_path")

# l = Light(-3, 10, 3, brightness=30, color=[255, 255, 255])
# l.visible = True

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

sphere = Sphere(0, 0, 0, radius=2, fill='white')
sphere.reflectiveness = 95
sphere.shadows = 0

while True:
    controller.check_events()

    if controller.b_down:
        set_variable(mouse_reset_pos=None)
        mainloop(rayTrace=True, camera=camera, output='output.jpg',
                 preview_mode='REFINE_SCANNER', update_frequency_in_pixels=500, max_bounces=3,
                 resize=True, add_RGB=1)
        # mainloop(rayTrace=True, camera=camera2, output='output2.jpg',
        #          preview_mode='REFINE_SCANNER', update_frequency_in_pixels=500, max_bounces=0, resize=True)
        # preview_mode = 'REFINE', 'SCANNER', 'REFINE_SCANNER' or None
        # (speed: fastest --> None > REFINE > SCANNER > REFINE_SCANNER <-- slowest), the higher update freq, the slower

        freeze_update(infinite=True)
    else:
        mainloop()
