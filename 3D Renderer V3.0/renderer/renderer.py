from statistics import *
from tkinter import *
import numpy as np
from math import *
import PIL.ImageTk
import PIL.Image
import warnings
import time

try:
    import cv2
except ImportError:
    warnings.warn("Unable to import cv2")


class App:
    def __init__(self):
        self.fov_ = 500
        self.sleep_time_ = 0.01  # If your computer is slow, make the sleep_time lower.
        #                     If your computer is fast, make the sleep_time higher.

        self.l_fps = 0
        self.fps = 0
        self.last_time = time.time()
        self.start = True
        self.reshare = False
        self.cam_rot = False

        self.mouse_reset_pos_ = (950, 540)
        self.pause_text_ = 'Renderer Paused'
        self.pause_color_ = 'gray10'

        self.pause = False
        self.reset = False


def rotate(point, xrot, yrot, zrot, center=np.array([0, 0, 0]), td=False):
    pos = np.matmul(point - center, yrot)
    pos = np.matmul(pos, xrot)
    pos = np.matmul(pos, zrot) + center

    if td:
        z = app.fov_ / pos[2]
        persp = np.array([[z, 0, 0], [0, z, 0]])
        res = np.matmul(persp, pos)

        return [z, [res[0], res[1]]]
    else:
        return pos


def calc_matrixes(xangle, yangle, zangle):
    xangle = xangle / 360 * pi * 2
    yangle = yangle / 360 * pi * 2
    zangle = zangle / 360 * pi * 2
    xrot = np.array(
        [[1, 0, 0], [0, cos(xangle), -sin(xangle)], [0, sin(xangle), cos(xangle)]])
    yrot = np.array(
        [[cos(yangle), 0, sin(yangle)], [0, 1, 0], [-sin(yangle), 0, cos(yangle)]])
    zrot = np.array(
        [[cos(zangle), -sin(zangle), 0], [sin(zangle), cos(zangle), 0], [0, 0, 1]])

    return xrot, yrot, zrot


def rotate_2D(x, y, cx, cy, angle):
    angle_rad = -np.radians(angle)
    dist_x = x - cx
    dist_y = y - cy
    current_angle = atan2(dist_y, dist_x)
    angle_rad += current_angle
    radius = sqrt(dist_x ** 2 + dist_y ** 2)
    x = cx + radius * cos(angle_rad)
    y = cy + radius * sin(angle_rad)

    return x, y


def local_rot2global_rot(xangle, yangle):
    sine_result = sin(-yangle / 180 * pi)
    cosine_result = cos(-yangle / 180 * pi)
    new_xangle = cosine_result * xangle
    new_zangle = sine_result * xangle

    return new_xangle, new_zangle


def linePlaneIntersection(planeNormal, planePoint, rayDirection, rayPoint, epsilon=1e-6):
    ndotu = planeNormal.dot(rayDirection)

    if abs(ndotu) < epsilon:
        return

    w = rayPoint - planePoint
    si = -planeNormal.dot(w) / ndotu
    Psi = w + si * rayDirection + planePoint
    return Psi


def check_inside_shape(point, shape):
    count = 0
    for tri in [np.array((shape[0], shape[i + 1], shape[i])) for i in range(1, len(shape) - 1)]:
        if check_inside_triangle(point, tri):
            count += 1

    if count % 2 == 1:
        return True
    else:
        return False


def check_inside_triangle(P, tri):
    x1, y1, x2, y2, x3, y3, xp, yp = tri.reshape(6).tolist() + P.tolist()
    c1 = (x2 - x1) * (yp - y1) - (y2 - y1) * (xp - x1)
    c2 = (x3 - x2) * (yp - y2) - (y3 - y2) * (xp - x2)
    c3 = (x1 - x3) * (yp - y3) - (y1 - y3) * (xp - x3)
    if (c1 < 0 and c2 < 0 and c3 < 0) or (c1 > 0 and c2 > 0 and c3 > 0):
        return True
    else:
        return


def color2rgb(color):
    canvas = list(rend_info['WINDOWS'].values())[0][1]
    if type(color) == str:
        color = np.array(canvas.winfo_rgb(color)) / 257
    color = np.array(color).astype('float64')
    return color


def color2hex(r, g, b):
    return '#%02x%02x%02x' % (min(int(r), 255), min(int(g), 255), min(int(b), 255))


def sortFirst(val):
    return int(round(val[0]))


def calculate(camera, point, width, height):
    res = rotate([point[0] - camera.x,
                  point[1] + camera.y,
                  point[2] - camera.z],
                 camera.xrot_, camera.yrot_, camera.zrot_,
                 td=True)

    camera.glob_coords[point] = [res[0], [res[1][0] + width / 2, res[1][1] + height / 2]]


def give_fps():
    print(app.l_fps)


def set_variable(sleep_time=0.01, fov=500, pause_color='gray10', pause_text='Renderer Paused',
                 mouse_reset_pos=(950, 540)):
    app.sleep_time_ = sleep_time
    app.fov_ = fov
    app.pause_color_ = pause_color
    app.pause_text_ = pause_text
    app.mouse_reset_pos_ = mouse_reset_pos


def change_background_color(winname, color):
    rend_info['WINDOWS'][winname][1].configure(bg=color)


def change_cursor(winname, cursor):
    rend_info['WINDOWS'][winname][1].config(cursor=cursor)


def init_window(name, w, h):
    tk = Tk()
    tk.title(name)
    tk.resizable(0, 0)
    canvas = Canvas(tk, width=w, height=h)
    canvas.pack()
    tk.update()

    rend_info['WINDOWS'][name] = (tk, canvas)


def freeze_update(infinite=False):
    while infinite:
        for window in rend_info['WINDOWS'].values():
            window[0].update()
    for window in rend_info['WINDOWS'].values():
        window[0].update()


def mainloop(rayTrace=False, camera=None, output=None, preview_mode='SCANNER', update_frequency_in_pixels=100,
             max_bounces=0, resize=True, add_RGB=1):
    # fps
    if time.time() - app.last_time >= 1:
        app.l_fps = app.fps
        app.fps = 0
        app.last_time = time.time()

    # Test for reset
    if not app.pause:
        if app.reset:
            for c in rend_info['CAMERAS']:
                c.reset()

        # clear display(s)
        for window in rend_info['WINDOWS'].values():
            window[1].delete('all')

        # Cameras and lights visible in 3D
        boxes = []
        for box in rend_info['CAMERAS']:
            if (box.visible and not rayTrace) or (box.ray_tracer_visible and rayTrace):
                # Calculate x, y and z angles from local angles
                xangle, zangle = local_rot2global_rot(-box.xangle, box.yangle)
                # xangle, zangle = -box.xangle, box.zangle
                # xangle *= -1
                boxes.append(Cube(box.x, box.y, box.z, size=0.1 * box.box_size,
                                  fill=['black', 'gray50', 'black', 'black', 'black', 'black'],
                                  x_angle=xangle, y_angle=-box.yangle, z_angle=zangle))
                boxes[-1].change_var('is_camera_box', box)

        for box in rend_info['LIGHTS']:
            if (box.visible and not rayTrace) or (box.ray_tracer_visible and rayTrace):
                box.color = color2rgb(box.color)
                if box.is_on:
                    boxes.append(Cube(box.x, box.y, box.z, size=0.1 * box.box_size,
                                      fill=[np.array(box.color) * box.brightness / 65 for _ in range(6)],
                                      x_angle=box.xangle, y_angle=box.yangle, z_angle=box.zangle))
                else:
                    boxes.append(Cube(box.x, box.y, box.z, size=0.1 * box.box_size,
                                      fill=[[0, 0, 0] for _ in range(6)],
                                      x_angle=box.xangle, y_angle=box.yangle, z_angle=box.zangle))
                boxes[-1].change_var('is_camera_box', box)

        # Check if coords of plates changed, then reshare them
        if not rayTrace:
            if app.reshare:
                for c in rend_info['CAMERAS']:
                    c.glob_coords = {}
                for p in rend_info['PLATES']:
                    p.share_coords()
                app.reshare = False

            for c in rend_info['CAMERAS']:
                if c.is_on or app.start:
                    # global camera constants
                    c.xrot_, c.yrot_, c.zrot_ = calc_matrixes(c.xangle, c.yangle, c.zangle)

                # calculate
                for point in c.glob_coords:
                    if c.displaying:
                        canvas = rend_info['WINDOWS'][c.displaying][1]
                        width = canvas.winfo_width()
                        height = canvas.winfo_height()
                    else:
                        width = 1280
                        height = 720
                    calculate(c, point, width, height)

                # update plates
                for u in rend_info['PLATES']:
                    if u.visible:
                        u.update(c)

        if rayTrace:
            rayTracer.rayTrace(camera, output, preview_mode, update_frequency_in_pixels, max_bounces,
                               resize, add_RGB=add_RGB)

        # Delete boxes of cameras and lights in 3D
        for b in boxes:
            b.delete()

        # Display
        for name in rend_info['WINDOWS'].keys():
            display = False
            canvas = rend_info['WINDOWS'][name][1]
            for c in rend_info['CAMERAS']:
                if c.displaying == name and c.is_on:
                    display = True

                    if not rayTrace:
                        while len(c.draw) > 0:
                            record = inf
                            record_i = 0
                            for i, dr in enumerate(c.draw):
                                if dr[0] < record:
                                    record = dr[0]
                                    record_i = i
                            # draw
                            plate = c.draw[record_i][3]
                            if plate.is_camera_box != c:
                                if len(c.draw[record_i][1]) > 1:
                                    # co1, co2, color, self.alpha, self.is_camera_box, self.outline, self.width
                                    if plate.alpha == 100:
                                        canvas.create_polygon(c.draw[record_i][1], fill=c.draw[record_i][2],
                                                              outline=plate.outline, width=plate.outline_thickness)
                                    else:
                                        canvas.create_polygon(c.draw[record_i][1], fill=c.draw[record_i][2],
                                                              stipple='gray' + str(plate.alpha),
                                                              outline=plate.outline, width=plate.outline_thickness)
                                else:
                                    canvas.create_oval(
                                        [list(np.array(c.draw[record_i][1][0]) - plate.radius * c.draw[record_i][0]),
                                         list(np.array(c.draw[record_i][1][0]) + plate.radius * c.draw[record_i][0])],
                                        fill=c.draw[record_i][2], outline=plate.outline, width=plate.outline_thickness)

                            del c.draw[record_i]
                    else:
                        canvas.create_image(0, 0, image=c.photo, anchor=NW)

            if not display:
                width = canvas.winfo_width()
                height = canvas.winfo_height()
                canvas.create_rectangle([-1, -1], [width + 1, height + 1], fill='black')
                canvas.create_text(width / 20 * 18, height / 23, anchor=CENTER,
                                   text="No Camera Set",
                                   font=('helvetica', round(width / 64), 'bold'), fill='white')

        # Reset mouse pos
        if app.mouse_reset_pos_:
            mouse.position = app.mouse_reset_pos_
            app.px, app.py = app.mouse_reset_pos_

    else:
        for window in rend_info['WINDOWS'].values():
            width = window[1].winfo_width()
            height = window[1].winfo_height()
            window[1].create_text(width / 2, height / 2, anchor=CENTER, text=app.pause_text_,
                                  font=('helvetica', 40, 'bold'), fill=app.pause_color_)

    if app.start:
        app.start = False

    for window in rend_info['WINDOWS'].values():
        window[0].update()
    time.sleep(app.sleep_time_)
    app.fps += 1

    app.cam_rot = False


rend_info = {'PLATES': [], 'CAMERAS': [], 'LIGHTS': [], 'SPHERES': [], 'WINDOWS': {}}

font = cv2.FONT_HERSHEY_TRIPLEX

app = App()

from pynput.mouse import Controller as contr

mouse = contr()
mouse.position = app.mouse_reset_pos_
app.px, app.py = mouse.position

from renderer.object_parent import object_parent
from renderer.plate import Plate
from renderer.dust import DustParticle
from renderer.camera import Camera
from renderer.cube import Cube
from renderer.cuboid import Cuboid
from renderer.sphere import Sphere
from renderer.model import Model
from renderer.light import Light
from renderer.contoller import *
import renderer.ray_tracer as rayTracer
