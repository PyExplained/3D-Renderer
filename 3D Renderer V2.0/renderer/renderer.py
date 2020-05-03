from matplotlib import colors
from tkinter import *
import numpy as np
from math import *
import time
import cv2

sleep_time_ = 0.01     # If your computer is slow, make the sleep_time lower.
                        # If your computer is fast, make the sleep_time higher.
fov_ = 500


def rotate(point, xrot, yrot, zrot, center=np.array([0, 0, 0]), td=False):
    pos = np.matmul(point - center, yrot)
    pos = np.matmul(pos, xrot)
    pos = np.matmul(pos, zrot) + center

    if td:
        z = fov_ / pos[2]
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
    print(l_fps)

def set_variable(sleep_time=0.01, fov=500, pause_color='gray10', pause_text='Renderer Paused', mouse_reset_pos=(950, 540)):
    global sleep_time_, fov_, pause_color_, pause_text_, mouse_reset_pos_

    sleep_time_ = sleep_time
    fov_ = fov
    pause_color_ = pause_color
    pause_text_ = pause_text
    mouse_reset_pos_ = mouse_reset_pos

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

def mainloop():
    global last_time, px, py, fps, l_fps, xrot, yrot, zrot, forward, left, backwards, right, reset, y_pos, y_neg, pause, \
        mouse, start, reshare, cam_rot, pause_text_, pause_color_, mouse_reset_pos_

    # fps
    if time.time() - last_time >= 1:
        l_fps = fps
        fps = 0
        last_time = time.time()

    # Test for reset
    if not pause:
        if reset:
            for c in rend_info['CAMERAS']:
                c.reset()

        # clear display(s)
        for window in rend_info['WINDOWS'].values():
            window[1].delete('all')

        # Cameras and lights visible in 3D
        boxes = []
        for box in rend_info['CAMERAS']:
            if box.visible:
                boxes.append(Cube(box.x, box.y, box.z, size=0.1,
                                  fill=['black', 'gray50', 'black', 'black', 'black', 'black'],
                                  x_angle=box.xangle, y_angle=-box.yangle, z_angle=box.zangle))
                for p in boxes[-1].plates:
                    p.is_camera_box = box

        for box in rend_info['LIGHTS']:
            if box.visible:
                if box.is_on:
                    boxes.append(Cube(box.x, box.y, box.z, size=0.1,
                                      fill=[np.array(box.color) * box.brightness / 65 for n in range(6)],
                                      x_angle=box.xangle, y_angle=box.yangle, z_angle=box.zangle))
                else:
                    boxes.append(Cube(box.x, box.y, box.z, size=0.1,
                                      fill=[[0, 0, 0] for n in range(6)],
                                      x_angle=box.xangle, y_angle=box.yangle, z_angle=box.zangle))

        # Check if coords of plates changed, than reshare them
        if reshare:
            for c in rend_info['CAMERAS']:
                c.glob_coords = {}
            for p in rend_info['PLATES']:
                p.share_coords()
            reshare = False

        for c in rend_info['CAMERAS']:
            if c.is_on or start:
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

        # Delete boxes of cameras and light in 3D
        for b in boxes:
            b.delete()

        # Display
        for name in rend_info['WINDOWS'].keys():
            display = False
            canvas = rend_info['WINDOWS'][name][1]
            for c in rend_info['CAMERAS']:
                if c.displaying == name and c.is_on:
                    display = True

                    while len(c.draw) > 0:
                        record = inf
                        record_i = 0
                        for i, dr in enumerate(c.draw):
                            if dr[0] < record:
                                record = dr[0]
                                record_i = i
                        # draw
                        if c.draw[record_i][4] != c:
                            if len(c.draw[record_i][1]) > 1:
                                if c.draw[record_i][3] == 100:
                                    canvas.create_polygon(c.draw[record_i][1], fill=c.draw[record_i][2],
                                                          outline=c.draw[record_i][5], width=c.draw[record_i][6])
                                else:
                                    canvas.create_polygon(c.draw[record_i][1], fill=c.draw[record_i][2],
                                                          stipple='gray' + str(c.draw[record_i][3]),
                                                          outline=c.draw[record_i][5], width=c.draw[record_i][6])
                            else:
                                canvas.create_oval([c.draw[record_i][1][0],
                                                    list(np.array(c.draw[record_i][1][0])+c.draw[record_i][6]*2)],
                                                   fill=c.draw[record_i][5])

                        del c.draw[record_i]

            if not display:
                width = canvas.winfo_width()
                height = canvas.winfo_height()
                canvas.create_rectangle([-1, -1], [width + 1, height + 1], fill='black')
                canvas.create_text(width / 20 * 18, height / 23, anchor=CENTER,
                                                                  text="No Camera Set",
                                                                  font=('helvetica', round(width/64), 'bold'), fill='white')

        # Reset mouse pos
        if mouse_reset_pos_:
            mouse.position = mouse_reset_pos_
            px, py = mouse_reset_pos_

    else:
        for window in rend_info['WINDOWS'].values():
            width = window[1].winfo_width()
            height = window[1].winfo_height()
            window[1].create_text(width / 2, height / 2, anchor=CENTER, text=pause_text_,
                                  font=('helvetica', 40, 'bold'), fill=pause_color_)

    if start:
        start = False

    for window in rend_info['WINDOWS'].values():
        window[0].update()
    time.sleep(sleep_time_)
    fps += 1

    cam_rot = False


rend_info = {'PLATES': [], 'CAMERAS':[], 'LIGHTS':[], 'WINDOWS':{}}

font = cv2.FONT_HERSHEY_TRIPLEX

l_fps = 0
fps = 0
last_time = time.time()
start = True
reshare = False
cam_rot = False

mouse_reset_pos_ = (950, 540)
pause_text_ = 'Renderer Paused'
pause_color_ = 'gray10'

pause = False
reset = False

from pynput.mouse import Controller as contr
mouse = contr()
mouse.position = mouse_reset_pos_
px, py = mouse.position


from renderer.object_parent import object_parent
from renderer.plate import Plate
from renderer.camera import Camera
from renderer.cube import Cube
from renderer.cuboid import Cuboid
from renderer.model import Model
from renderer.light import Light
from renderer.contoller import *
