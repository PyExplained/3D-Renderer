from matplotlib import colors
from tkinter import *
import numpy as np
from math import *
import time
import cv2

sleep_time = 0.01     # If your computer is slow, make the sleep_time lower.
                        # If your computer is fast, make the sleep_time higher.
fov = 500


def rotate(point, xrot, yrot, zrot, center=np.array([0, 0, 0]), td=False):
    pos = np.matmul(np.array(point) - center, yrot)
    pos = np.matmul(np.array(pos), xrot)
    pos = np.matmul(np.array(pos), zrot) + center

    if td:
        z = fov / pos[2]

        persp = np.array([[z, 0, 0], [0, z, 0]])
        res = np.matmul(persp, pos)

        return [z, [res[0] + width / 2, res[1] + height / 2]]
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

def on_press(key):
    global w, a, s, d, r, space, shift, esc, mouse, px, py

    key = str(key)
    if key == "'w'":
        w = True
    if key == "'a'":
        a = True
    if key == "'s'":
        s = True
    if key == "'d'":
        d = True
    if key == "'r'":
        r = True
    if key == 'Key.space':
        space = True
    if key == 'Key.shift':
        shift = True
    if key == 'Key.esc':
        if esc:
            esc = False
            mouse.position = (950, 540)
            px, py = 950, 540
        else:
            esc = True

def on_release(key):
    global w, a, s, d, r, space, shift

    key = str(key)
    if key == "'w'":
        w = False
    if key == "'a'":
        a = False
    if key == "'s'":
        s = False
    if key == "'d'":
        d = False
    if key == "'r'":
        r = False
    if key == 'Key.shift':
        shift = False
    if key == 'Key.space':
        space = False

def sortFirst(val):
    return int(round(val[0]))

def calculate(camera, point):
    global xrot, yrot, zrot

    camera.glob_coords[point] = rotate([point[0] - camera.x,
                                        point[1] + camera.y,
                                        point[2] - camera.z],
                                        xrot, yrot, zrot,
                                        td=True)


def give_fps():
    print(l_fps)

def set_frame_interval(n):
    global sleep_time

    sleep_time = n

def set_fov(n):
    global fov

    fov = n

def init_window(name, w, h):
    global width, height, tk, canvas, window_name

    tk = Tk()
    tk.title("Renderer")
    tk.resizable(0, 0)
    tk.wm_attributes("-topmost", 1)
    width = w
    height = h
    canvas = Canvas(tk, width=width, height=height)
    canvas.pack()

def mainloop():
    global last_time, px, py, fps, l_fps, xrot, yrot, zrot, w, a, s, d, r, space, shift, esc, \
        mouse, start, reshare

    # fps
    if time.time() - last_time >= 1:
        l_fps = fps
        fps = 0
        last_time = time.time()

    # Test for reset
    if not esc:
        if r:
            for c in rend_info['CAMERAS']:
                c.reset()

        # clear display
        canvas.delete('all')

        boxes = []
        for box in rend_info['CAMERAS']:
            if not box.displaying and box.visible:
                boxes.append(
                    Cube(box.x, box.y, box.z, size=0.1, fill=['black', 'gray50', 'black', 'black', 'black', 'black'],
                         x_angle=-box.xangle, y_angle=-box.yangle, z_angle=box.zangle))

        if reshare:
            for c in rend_info['CAMERAS']:
                c.glob_coords = {}
            for p in rend_info['PLATES']:
                p.share_coords()
            reshare = False

        xx = px - mouse.position[0]
        yy = py - mouse.position[1]
        display = False
        for c in rend_info['CAMERAS']:
            # key-input
            if c.controllable:
                if w:
                    x = sin(c.yangle / 360 * pi * 2)
                    z = cos(c.yangle / 360 * pi * 2)
                    c.x += x / 4
                    c.z += z / 4
                if a:
                    x = sin((c.yangle - 90) / 360 * pi * 2)
                    z = cos((c.yangle - 90) / 360 * pi * 2)
                    c.x += x / 4
                    c.z += z / 4
                if s:
                    x = sin((c.yangle - 180) / 360 * pi * 2)
                    z = cos((c.yangle - 180) / 360 * pi * 2)
                    c.x += x / 4
                    c.z += z / 4
                if d:
                    x = sin((c.yangle + 90) / 360 * pi * 2)
                    z = cos((c.yangle + 90) / 360 * pi * 2)
                    c.x += x / 4
                    c.z += z / 4
                if space:
                    c.y += 1 / 4
                if shift:
                    c.y -= 1 / 4

                # mouse-input
                c.yangle -= xx / 2
                c.xangle += yy / 2

            if c.is_on and (xx != 0 or yy != 0) or start:
                # global camera constants
                xrot, yrot, zrot = calc_matrixes(c.xangle, c.yangle, c.zangle)
                start = False

            # calculate
            for point in c.glob_coords:
                calculate(c, point)

            for u in rend_info['PLATES']:
                if u.visible:
                    u.update(c)

            if c.displaying:
                display = True
                while len(c.draw) > 0:
                    record = inf
                    record_i = 0
                    for i, dr in enumerate(c.draw):
                        if dr[0] < record:
                            record = dr[0]
                            record_i = i
                    # draw
                    if c.draw[record_i][3] == 100:
                        canvas.create_polygon(c.draw[record_i][1], fill=c.draw[record_i][2])
                    else:
                        canvas.create_polygon(c.draw[record_i][1], fill=c.draw[record_i][2], stipple='gray' + str(c.draw[record_i][3]))

                    del c.draw[record_i]

        for b in boxes:
            b.delete()

        if not display:
            canvas.create_rectangle([0, 0], [width, height], fill='black')
            canvas.create_text(width / 20 * 19, height / 25, anchor=CENTER, text="No Camera Set",
                               font=('helvetica', 10, 'bold'), fill='white')
        else:
            mouse.position = (950, 540)
            px, py = 950, 540
    else:
        canvas.create_text(width / 2, height / 2, anchor=CENTER, text="Renderer Paused",
                           font=('helvetica', 40, 'bold'), fill='gray5')

    tk.update()
    time.sleep(sleep_time)
    fps += 1


rend_info = {'PLATES': [], 'CAMERAS':[]}

font = cv2.FONT_HERSHEY_TRIPLEX

from pynput.keyboard import Listener
Listener(on_press=on_press, on_release=on_release).start()
w = False
a = False
s = False
d = False
r = False
space = False
shift = False
esc = False
from pynput.mouse import Controller
mouse = Controller()
mouse.position = (950, 540)
px, py = mouse.position

l_fps = 0
fps = 0
last_time = time.time()
start = True
reshare = False

width = 1280
height = 720

from renderer.plate import Plate
from renderer.camera import Camera
from renderer.cube import Cube
from renderer.cuboid import Cuboid