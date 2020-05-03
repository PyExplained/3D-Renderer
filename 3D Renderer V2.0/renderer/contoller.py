from renderer.renderer import *
import renderer.renderer as rn


class Controller:
    def __init__(self, object):
        self.object = object
        self.keys = {}
        self.pause_key = 'Key.esc'
        self.reset_key = 'r'

        from pynput.keyboard import Listener
        Listener(on_press=self.on_press, on_release=self.on_release).start()

    def bind(self, event, action, amount, around='self'):
        self.keys[event] = [False, action, amount, 'bind', 0, around]

    def notify(self, event, event_sort, variable):
        setattr(self, variable, False)
        self.keys[event] = [False, event, event_sort, 'notify', variable, None]

    def check_events(self):
        # Check for 'player'-input
        if not rn.pause:
            for item in self.keys.items():
                if item[1][3] == 'bind':
                    if item[0] == 'mouse_x':
                        xx = (rn.px - mouse.position[0]) * item[1][2]
                        item[1][0] = True
                        item[1][4] = xx
                    elif item[0] == 'mouse_y':
                        yy = (rn.py - mouse.position[1]) * item[1][2]
                        item[1][0] = True
                        item[1][4] = yy
                    else:
                        item[1][4] = item[1][2]

                if not item[1][0]:
                    if item[1][3] == 'notify':
                        setattr(self, item[1][4], False)

                if item[1][0]:
                    if item[1][3] == 'notify':
                        setattr(self, item[1][4], True)

                    if item[1][3] == 'bind':
                        if item[1][1] == 'forward':
                            x = sin(self.object.yangle / 360 * pi * 2)
                            z = cos(self.object.yangle / 360 * pi * 2)
                            self.object.move(x * item[1][4], 0, z * item[1][4])
                        if item[1][1] == 'left':
                            x = sin((self.object.yangle - 90) / 360 * pi * 2)
                            z = cos((self.object.yangle - 90) / 360 * pi * 2)
                            self.object.move(x * item[1][4], 0, z * item[1][4])
                        if item[1][1] == 'backwards':
                            x = sin((self.object.yangle - 180) / 360 * pi * 2)
                            z = cos((self.object.yangle - 180) / 360 * pi * 2)
                            self.object.move(x * item[1][4], 0, z * item[1][4])
                        if item[1][1] == 'right':
                            x = sin((self.object.yangle + 90) / 360 * pi * 2)
                            z = cos((self.object.yangle + 90) / 360 * pi * 2)
                            self.object.move(x * item[1][4], 0, z * item[1][4])
                        if item[1][1] == 'x':
                            self.object.move(item[1][4], 0, 0)
                        if item[1][1] == 'y':
                            self.object.move(0, item[1][4], 0)
                        if item[1][1] == 'z':
                            self.object.move(0, 0, item[1][4])
                        if item[1][1] == 'x_rotation':
                            self.object.rotate(item[1][4], 0, 0, center=item[1][5])
                        if item[1][1] == 'y_rotation':
                            self.object.rotate(0, item[1][4], 0, center=item[1][5])
                        if item[1][1] == 'z_rotation':
                            self.object.rotate(0, 0, item[1][4], center=item[1][5])


    def on_press(self, key):
        global forward, left, backwards, right, reset, y_pos, y_neg, pause, mouse, px, py

        if type(key) != str:
            key = str(key)

        if not 'Key' in key:
            key = key.replace("'", "")

        for item in self.keys.items():
            if key == item[0]:
                if item[1][2] != 'toggle':
                    self.keys[item[0]][0] = True
                else:
                    if self.keys[item[0]][0]:
                        self.keys[item[0]][0] = False
                    else:
                        self.keys[item[0]][0] = True

        if key == self.reset_key:
            rn.reset = True

        if key == 'Key.shift':
            y_neg = True

        if key == self.pause_key:
            if rn.pause:
                rn.pause = False
                if rn.mouse_reset_pos_:
                    mouse.position = rn.mouse_reset_pos_
                    px, py = rn.mouse_reset_pos_
            else:
                rn.pause = True

    def on_release(self, key):
        global forward, left, backwards, right, reset, y_pos, y_neg

        if type(key) != str:
            key = str(key)

        if not 'Key' in key:
            key = key.replace("'", "")

        for item in self.keys.items():
            if key == item[0]:
                if item[1][2] != 'toggle':
                    self.keys[item[0]][0] = False

        if key == self.reset_key:
            rn.reset = False

        if key == self.pause_key:
            y_pos = False

