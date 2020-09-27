import json
import os.path
import pyglet
from pyglet import resource
from pyglet import sprite
from pyglet import text
from pyglet.window import key
from pyglet.window import mouse
from pyglet.gl import gl
from random import randint

gl.glEnable(gl.GL_TEXTURE_2D)
gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
pyglet.image.Texture.default_mag_filter = gl.GL_NEAREST
pyglet.image.Texture.default_min_filter = gl.GL_NEAREST

map_width = 2400
map_height = 1200
FREE = "free"
NORMAL = "normal"

resource.path = ['./resources', './resources/img', './resources/sfx']
resource.reindex()
pyglet.options['debug_gl'] = False

window = pyglet.window.Window(800, 600, caption="Pato Goes For a Walk")

icon16 = resource.image('icon16.png')
icon32 = resource.image('icon32.png')
window.set_icon(icon16, icon32)

gui_batch = pyglet.graphics.Batch()

dark = resource.image('black.png')
duck_idle_right = resource.image('duck_idle_right.png')
duck_idle_left = resource.image('duck_idle_left.png')
shadow = resource.image('shadow.png')
hud_bread = resource.image('hud_bread.png')
timer_hud = resource.image('timer_hud.png')
button_raw = resource.image('button.png')
title = resource.image('title.png')
water = resource.image('water.png')
flower = resource.image('flower.png')
win_text = resource.image('win_text.png')
lose_text = resource.image('lose_text.png')
page_left = resource.image('pageL.png')
page_right = resource.image('pageR.png')
quack = resource.media('quack.wav', streaming=False)
eat_bread = resource.media('eat_bread.wav', streaming=False)
victory = resource.media('victory.wav', streaming=False)
game_over = resource.media('gameover.wav', streaming=False)
ambience = resource.media('ambience.wav', streaming=False)
black = sprite.Sprite(dark, x=0, y=0)

amb = pyglet.media.Player()
amb.queue(ambience)
amb.loop = True

default_cur = window.get_system_mouse_cursor(window.CURSOR_DEFAULT)
choose_cur = window.get_system_mouse_cursor(window.CURSOR_HAND)


class Camera:

    def __init__(self, scroll_speed=1, min_zoom=1, max_zoom=4):
        assert min_zoom <= max_zoom
        self.scroll_speed = scroll_speed
        self.max_zoom = max_zoom
        self.min_zoom = min_zoom
        self.offset_x = 0
        self.offset_y = 0
        self._zoom = max(min(1, self.max_zoom), self.min_zoom)

    @property
    def zoom(self):
        return self._zoom

    @zoom.setter
    def zoom(self, value):
        self._zoom = max(min(value, self.max_zoom), self.min_zoom)

    @property
    def position(self):
        return self.offset_x, self.offset_y

    @position.setter
    def position(self, value):
        self.offset_x, self.offset_y = value

    def move(self, axis_x, axis_y):
        self.offset_x += self.scroll_speed * axis_x
        self.offset_y += self.scroll_speed * axis_y

    def begin(self):
        gl.glTranslatef(-self.offset_x * self._zoom,
                        -self.offset_y * self._zoom, 0)
        gl.glScalef(self._zoom, self._zoom, 1)

    def end(self):
        gl.glScalef(1 / self._zoom, 1 / self._zoom, 1)
        gl.glTranslatef(self.offset_x * self._zoom,
                        self.offset_y * self._zoom, 0)

    def __enter__(self):
        self.begin()

    def __exit__(self, exception_type, exception_value, traceback):
        self.end()


def position_camera(self, camera: Camera, position: tuple = (0, 0),
                    zoom: float = 1, min_pos: tuple = (None, None),
                    max_pos: tuple = (None, None)):

    zoom = min(window.width // self.DEFAULT_SIZE[0],
               window.height // self.DEFAULT_SIZE[1]) * zoom

    if self.camera.zoom != zoom:
        self.camera.zoom = zoom

        x = -window.width // 2 // zoom
        y = -window.height // 2 // zoom

        target_x = position[0]
        target_y = position[1]

        if min_pos[0] is not None:
            target_x = max(target_x, min_pos[0])
        if min_pos[1] is not None:
            target_y = max(target_y, min_pos[1])
        if max_pos[0] is not None:
            target_x = min(target_x, max_pos[0])
        if max_pos[1] is not None:
            target_y = min(target_y, max_pos[1])

        x += target_x
        y += target_y

        if self.camera.position != (x, y):
            self.camera.position = (x, y)


def center_image(img):
    img.anchor_x = img.width // 2
    img.anchor_y = img.height // 2


center_image(duck_idle_right)
center_image(duck_idle_left)
center_image(shadow)
center_image(button_raw)
center_image(title)
center_image(water)
center_image(win_text)
center_image(lose_text)


# Utils

class Rect:

    def __init__(self, x, y, w, h):
        self.set(x, y, w, h)

    def draw(self):
        pyglet.graphics.draw(4, gl.GL_QUADS, self._quad)

    def set(self, x=None, y=None, w=None, h=None):
        self._x = self._x if x is None else x
        self._y = self._y if y is None else y
        self._w = self._w if w is None else w
        self._h = self._h if h is None else h
        self._quad = ('v2f', (self._x, self._y,
                              self._x + self._w, self._y,
                              self._x + self._w, self._y + self._h,
                              self._x, self._y + self._h))


class Region:

    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def contain(self, x, y):
        inside_x = False
        inside_y = False

        if x >= self.x and x <= (self.x + self.w):
            inside_x = True

        if y >= self.y and y <= (self.y + self.h):
            inside_y = True

        if inside_x and inside_y:
            return True
        else:
            return False

    def collides(self, r2):
        # Check the edge collision
        if self.x < r2.x + r2.w and \
           self.x + self.w > r2.x and \
           self.y < r2.y + r2.h and \
           self.h + self.y > r2.y:
            return True

        return False

    def draw(self):
        r = Rect(self.x, self.y, self.w, self.h)
        r.draw()


# Code structure
class Game:

    def __init__(self, scene):
        self.scene = scene
        self.mouse_x = 0
        self.mouse_y = 0
        self.hud = Hud()
        self.on_exit = False
        self.opacity = 0
        self.next_scene = scene
        self.mode = FREE

    def draw(self):
        self.scene.draw()

        if self.scene == park:
            self.hud.draw()

        if self.on_exit:
            self.opacity += 20
            black.opacity = min(self.opacity, 255)
            black.draw()

    def update(self, dt):
        window.set_mouse_cursor(default_cur)
        self.scene.update(dt)

        if self.opacity >= 255:
            self.enter()

    def mouse_xy(self, x, y, dx, dy):
        self.mouse_x = x
        self.mouse_y = y

    def on_click(self, x, y, button):
        self.scene.on_click(x, y, button)

    def on_key_press(self, symbol, modifiers):
        self.scene.on_key_press(symbol, modifiers)

    def set_scene_to(self, scene):
        self.scene = self.next_scene

    def set_next_scene(self, next_scene):
        pyglet.clock.schedule_once(self.set_scene_to, 0.2)
        self.next_scene = next_scene
        self.on_exit = True

    def enter(self):
        self.scene.enter()
        self.opacity = 0
        self.on_exit = False

    def restart(self):
        park.target_amount = randint(10, 46)
        duck.x = 1570
        duck.y = 500
        self.hud.bread_amount = 0
        self.hud.timer = 100
        self.set_next_scene(park)
        park.begin()
        park.update_bread_count()
        amb.play()


class Player:

    idle_images = [
        resource.image('duck_idle_right.png'),
        resource.image('duck_idle_left.png')
    ]

    walk_left_frames = [
        resource.image('duck_walk_left_1.png'),
        resource.image('duck_idle_left.png'),
    ]

    walk_right_frames = [
        resource.image('duck_walk_right_1.png'),
        resource.image('duck_idle_right.png'),
    ]

    walk_left = pyglet.image.Animation.from_image_sequence(walk_left_frames,
                                                           duration=0.1,
                                                           loop=True)

    walk_right = pyglet.image.Animation.from_image_sequence(walk_right_frames,
                                                            duration=0.1,
                                                            loop=True)

    air = resource.image('air.png')
    witch_hat = resource.image('witch_hat.png')
    top_hat = resource.image('top_hat.png')
    builder_hat = resource.image('builder_hat.png')
    bread_hat = resource.image('bread_hat.png')
    birthday_hat = resource.image('birthday_hat.png')
    among_hat = resource.image('among_hat.png')
    rainbow_hat = resource.image('rainbow_hat.png')
    jimmy_hat = resource.image('jimmy_hat.png')
    plant_hat = resource.image('plant_hat.png')

    def __init__(self):
        for img in self.walk_left_frames:
            img.anchor_x = img.width // 2
            img.anchor_y = img.height // 2

        for img in self.walk_right_frames:
            img.anchor_x = img.width // 2
            img.anchor_y = img.height // 2

        self.x = 2000
        self.y = 300
        self.vx = 0
        self.vy = 0
        self.direction = 1
        self.i_right = sprite.Sprite(duck_idle_right)
        self.i_left = sprite.Sprite(duck_idle_left)
        self.w_right = sprite.Sprite(self.walk_right)
        self.w_left = sprite.Sprite(self.walk_left)
        self.sprite = self.i_right
        self.shadow = sprite.Sprite(shadow)
        self.moving = False
        self.hitbox = Region(self.x - self.sprite.width // 2,
                             self.y - self.sprite.height // 2,
                             60, 50)

        # Hats
        self.hat_0 = sprite.Sprite(self.air)
        self.hat_1 = sprite.Sprite(self.witch_hat)
        self.hat_2 = sprite.Sprite(self.top_hat)
        self.hat_3 = sprite.Sprite(self.builder_hat)
        self.hat_4 = sprite.Sprite(self.bread_hat)
        self.hat_5 = sprite.Sprite(self.birthday_hat)
        self.hat_6 = sprite.Sprite(self.among_hat)
        self.hat_7 = sprite.Sprite(self.rainbow_hat)
        self.hat_8 = sprite.Sprite(self.jimmy_hat)
        self.hat_9 = sprite.Sprite(self.plant_hat)

        self.hat_value = 0

        self.hat_wear = self.hat_0

    def draw(self):
        self.shadow.draw()
        self.sprite.draw()
        self.hat_wear.draw()

    def detect_collision(self, hitbox):
        for obj in game.scene.obj_list:
            if obj.solid and hitbox.collides(obj.hitbox):
                return obj

    def update(self, dt):
        new_x = self.x + self.vx * dt
        new_y = self.y + self.vy * dt
        new_hitbox = Region(x=new_x - 70 // 2,
                            y=new_y - 90 // 2,
                            w=70, h=50)

        obj_hit = self.detect_collision(new_hitbox)

        # Check collisions
        if game.scene == park:
            if obj_hit is not None:
                self.vx = 0
                self.vy = 0
                self.sprite = self.i_right
                self.sprite.x = self.x
                self.sprite.y = self.y
                return

        # Check sprite
        if not self.moving and \
           self.direction == 1:
            self.sprite = self.i_right

        if not self.moving and \
           self.direction == 0:
            self.sprite = self.i_left

        if self.moving and \
           self.direction == 1:
            self.sprite = self.w_right

        if self.moving and \
           self.direction == 0:
            self.sprite = self.w_left

        self.x = new_x
        self.y = new_y
        self.sprite.x = self.x
        self.sprite.y = self.y
        self.shadow.x = self.x - 5 if self.direction == 1 else self.x + 5
        self.shadow.y = self.y - 45
        self.hitbox = new_hitbox

        if game.scene == park:
            self.hat_wear.x = self.x - 30 if self.direction == 0 else \
             self.x - 20
            self.hat_wear.y = self.y + 20 if self.hat_wear in \
                [self.hat_5] else self.y + 15
            self.hat_wear.scale = 1
            self.sprite.scale = 1

        if self.hat_value == 0:
            self.hat_wear = self.hat_0
        elif self.hat_value == 1:
            self.hat_wear = self.hat_1
        elif self.hat_value == 2:
            self.hat_wear = self.hat_2
        elif self.hat_value == 3:
            self.hat_wear = self.hat_3
        elif self.hat_value == 4:
            self.hat_wear = self.hat_4
        elif self.hat_value == 5:
            self.hat_wear = self.hat_5
        elif self.hat_value == 6:
            self.hat_wear = self.hat_6
        elif self.hat_value == 7:
            self.hat_wear = self.hat_7
        elif self.hat_value == 8:
            self.hat_wear = self.hat_8
        elif self.hat_value == 9:
            self.hat_wear = self.hat_9
        else:
            self.hat_value = 0

    def change_direction(self, vx, vy, direction):
        self.vx = vx
        self.vy = vy
        self.direction = direction


class Bread:

    bread_raw = resource.image('bread.png')

    def __init__(self):
        self.x = randint(125, 2297)
        self.y = randint(-1035, 511)
        self.sprite = sprite.Sprite(self.bread_raw, x=self.x, y=self.y)
        self.hitbox = Region(self.sprite.x,
                             self.sprite.y,
                             self.sprite.width, self.sprite.height)

    def draw(self):
        self.sprite.draw()

    def update(self, dt):
        self.sprite.x = self.x
        self.sprite.y = self.y

    def is_grabbed(self):
        park.bread_objs.remove(self)
        eat_bread.play()


class Hud:

    bread_display = sprite.Sprite(hud_bread, x=580, y=490, batch=gui_batch)
    time_display = sprite.Sprite(timer_hud, x=580, y=400, batch=gui_batch)

    def __init__(self):
        self.bread_amount = 0
        self.bread_text = text.Label(f"{self.bread_amount}", x=660,
                                     y=533, anchor_x='center',
                                     anchor_y='center', font_size=24,
                                     bold=True, batch=gui_batch)
        self.timer = 1
        self.timer_text = text.Label(f"{self.timer}", x=660,
                                     y=450, anchor_x='center',
                                     anchor_y='center', font_size=24,
                                     bold=True, batch=gui_batch)

        self.leave_text = text.Label("Press L to leave",
                                     x=100, y=510, anchor_x='center',
                                     anchor_y='center',
                                     color=(255, 255, 255, 255),
                                     font_size=16, bold=True)

    def draw(self):
        self.bread_display.draw()
        self.bread_text.draw()
        self.leave_text.draw()

        if game.mode == NORMAL:
            self.time_display.draw()
            self.timer_text.draw()

    def update(self, dt):
        self.update_text()

    def update_text(self):
        self.bread_display.x = camera.offset_x + 580
        self.bread_display.y = camera.offset_y + 490
        self.bread_text_x = self.bread_text.x = self.bread_display.x + 80
        self.bread_text_y = self.bread_text.y = self.bread_display.y + 42
        self.leave_text.x = camera.offset_x + 100
        self.leave_text.y = camera.offset_y + 580

        if self.bread_amount != park.target_amount:
            self.bread_text = text.Label(f"{self.bread_amount}",
                                         x=self.bread_text_x,
                                         y=self.bread_text_y,
                                         anchor_x='center',
                                         anchor_y='center',
                                         font_size=24,
                                         color=(255, 255, 255, 255),
                                         bold=True, batch=gui_batch)
        if self.bread_amount >= park.target_amount:
            self.bread_text = text.Label(f"{self.bread_amount}",
                                         x=self.bread_text_x,
                                         y=self.bread_text_y,
                                         anchor_x='center',
                                         anchor_y='center',
                                         font_size=24,
                                         color=(155, 227, 103, 255),
                                         bold=True, batch=gui_batch)

        self.time_display.x = camera.offset_x + 580
        self.time_display.y = camera.offset_y + 400
        self.time_text_x = self.timer_text.x = self.time_display.x + 80
        self.time_text_y = self.timer_text.y = self.time_display.y + 42

        self.timer_text = text.Label(f"{self.timer}",
                                     x=self.time_text_x,
                                     y=self.time_text_y,
                                     anchor_x='center',
                                     anchor_y='center', font_size=24,
                                     bold=True, batch=gui_batch)


class GameState:

    def __init__(self):
        pass

    def save(self, duck, filename="patodata.json"):
        state = {}

        state["current_hat"] = duck.hat_value

        # Saving
        f = open(filename, "w")
        f.write(json.dumps(state))
        f.close()

    def load(self, duck, filename="patodata.json"):
        f = open(filename, "r")
        state = json.load(f)

        duck.hat_value = state.get("current_hat", 0)

    def state_exists(self, filename="patodata.json"):
        return os.path.isfile(filename)


class SceneObject:

    def __init__(self, id, solid, tag, x, y, w=0, h=0, spr=None, visible=True):
        self.id = id
        self.solid = solid
        self.tag = tag
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.spr = spr
        self.visible = visible

        if spr is not None:
            self.spr.x = self.x
            self.spr.y = self.y

        if spr is not None and w == 0 and h == 0:
            self.hitbox = Region(self.x - self.spr.width // 2,
                                 self.y - self.spr.height // 2,
                                 self.spr.width,
                                 self.spr.height)

        else:
            self.hitbox = Region(self.x - self.w // 2,
                                 self.y - self.h // 2,
                                 self.w,
                                 self.h)


class Scene:

    def __init__(self):
        self.obj_list = []

    def draw(self):
        pass

    def update(self, dt):
        pass

    def on_click(self, x, y, button):
        pass

    def on_key_press(self, symbol, modifiers):
        pass

    def enter(self):
        pass


# Scenes
class Introduction(Scene):

    logo = resource.image('logo.png')
    center_image(logo)

    def __init__(self):
        self.obj_list = []
        self.count = 0
        self.text = text.Label("eviluser7 presents...", x=400, y=200,
                               anchor_x='center', anchor_y='center',
                               bold=True, color=(255, 255, 255, 255))

    def draw(self):
        self.logo.blit(400, 300)
        self.text.draw()

    def update(self, dt):
        self.count += 1
        if self.count >= 120:
            game.set_next_scene(menu)

    def on_click(self, x, y, button):
        pass


class MenuScene(Scene):

    background = resource.image('bg.png')
    info = resource.image('info.png')
    hat_button = resource.image('hat_button.png')

    def __init__(self):
        gs = GameState()

        self.obj_list = []
        self.button = sprite.Sprite(button_raw, x=400, y=200)
        self.button_r = Region(self.button.x - self.button.width // 2,
                               self.button.y - self.button.height // 2,
                               self.button.width, self.button.height)
        self.title_spr = sprite.Sprite(title, x=400, y=400)
        self.bg = sprite.Sprite(self.background, x=0, y=0)
        self.info_button = sprite.Sprite(self.info, x=700, y=50)
        self.hat_click = sprite.Sprite(self.hat_button, x=700, y=120)
        self.info_region = Region(700, 50, 64, 64)
        self.hat_region = Region(700, 120, 64, 64)
        self.author = text.Label("Made by eviluser7 in 2020",
                                 x=640, y=15, anchor_x='center',
                                 anchor_y='center', font_size=16,
                                 color=(0, 0, 0, 255),
                                 bold=True)
        self.version = text.Label("v1.01", x=577, y=326,
                                  anchor_x='center', anchor_y='center',
                                  font_size=24,
                                  color=(255, 255, 255, 255),
                                  bold=True)

        if gs.state_exists():
            gs.load(duck)

    def draw(self):
        self.bg.draw()
        self.button.draw()
        self.title_spr.draw()
        self.info_button.draw()
        self.hat_click.draw()
        self.author.draw()
        self.version.draw()
        duck.hat_wear.draw()

    def update(self, dt):
        if self.button_r.contain(game.mouse_x, game.mouse_y) or \
           self.info_region.contain(game.mouse_x, game.mouse_y) or \
           self.hat_region.contain(game.mouse_x, game.mouse_y):
            window.set_mouse_cursor(choose_cur)

        duck.hat_wear.x = 650
        duck.hat_wear.y = 125
        duck.hat_wear.scale = 1
        camera.position = (0, 0)

    def on_click(self, x, y, button):
        if self.button_r.contain(x, y) and \
           game.mode == NORMAL:
            park.begin()
            game.set_next_scene(park)
            duck.x = 1570
            duck.y = 500
            game.hud.bread_amount = 0
            game.hud.timer = 100
            park.update_bread_count()
            amb.play()

        if self.button_r.contain(x, y) and \
           game.mode == FREE:
            game.set_next_scene(park)
            duck.x = 1570
            duck.y = 500
            game.hud.bread_amount = 0
            amb.play()
            pyglet.clock.schedule_interval(bread_spawn, 2)

        if self.info_region.contain(x, y):
            game.set_next_scene(licenses)

        if self.hat_region.contain(x, y):
            game.set_next_scene(hats)

    def on_key_press(self, symbol, modifiers):
        pass

    def enter(self):
        quack.play()
        amb.pause()


class Licenses(Scene):

    license_bg = resource.image('license_bg.png')
    credits_back = resource.image('credits_back.png')
    gameplay = resource.image('gameplay.png')
    pageL = sprite.Sprite(page_left, x=350, y=5)
    pageR = sprite.Sprite(page_right, x=420, y=5)
    back_spr = sprite.Sprite(credits_back, x=10, y=500)
    instructions = sprite.Sprite(gameplay, x=0, y=0)

    def __init__(self):
        amb.pause()
        self.bg = sprite.Sprite(self.license_bg, x=0, y=0)
        self.obj_list = []
        self.page = 1
        self.back = Region(10, 500, 135, 86)
        self.go_right = Region(420, 5, 64, 64)
        self.go_left = Region(350, 5, 64, 64)
        self.license = text.Label(
            """
            Copyright (c) 2006-2008 Alex Holkner
    Copyright (c) 2008-2020 pyglet contributors
    All rights reserved.
    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are met:
        * Redistributions of source code must retain the above copyright
            notice, this list of conditions and the following disclaimer.
        * Redistributions in binary form must reproduce the above copyright
            notice, this list of conditions and the following disclaimer in
            the documentation and/or other materials provided with the
            distribution.
        * Neither the name of pyglet nor the names of its
            contributors may be used to endorse or promote products
            derived from this software without specific prior written
            permission.
    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
    "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
    LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
    FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
    COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
    INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
    BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
    LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
    CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
    LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
    ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
    POSSIBILITY OF SUCH DAMAGE.
            """,
            x=550, y=230, anchor_x='center', anchor_y='center', font_size=10,
            bold=True, color=(0, 0, 0, 255),
            multiline=True, width=800, height=600
        )

        self.license_header = text.Label("License", x=400, y=550,
                                         anchor_x='center',
                                         anchor_y='center',
                                         font_size=24, bold=True,
                                         color=(0, 0, 0, 255))

    def draw(self):
        self.bg.draw()
        if self.page == 1:
            self.license.draw()
            self.license_header.draw()
            self.pageR.draw()

        if self.page == 2:
            self.instructions.draw()
            self.pageL.draw()

        self.back_spr.draw()

    def update(self, dt):
        if self.go_right.contain(game.mouse_x, game.mouse_y) and \
           self.page == 1:
            window.set_mouse_cursor(choose_cur)

        if self.go_left.contain(game.mouse_x, game.mouse_y) and \
           self.page == 2:
            window.set_mouse_cursor(choose_cur)

        if self.back.contain(game.mouse_x, game.mouse_y):
            window.set_mouse_cursor(choose_cur)

    def on_click(self, x, y, button):
        if self.go_right.contain(x, y) and self.page == 1:
            self.page = 2

        if self.go_left.contain(x, y) and self.page == 2:
            self.page = 1

        if self.back.contain(x, y):
            game.set_next_scene(menu)

    def on_key_press(self, symbol, modifiers):
        pass


class HatSelection(Scene):

    hat0_select = resource.image('hat0_select.png')
    hat1_select = resource.image('hat1_select.png')
    hat2_select = resource.image('hat2_select.png')
    hat3_select = resource.image('hat3_select.png')
    hat4_select = resource.image('hat4_select.png')
    hat5_select = resource.image('hat5_select.png')
    hat6_select = resource.image('hat6_select.png')
    hat7_select = resource.image('hat7_select.png')
    hat8_select = resource.image('hat8_select.png')
    hat9_select = resource.image('hat9_select.png')

    def __init__(self):
        self.obj_list = []
        self.back = Region(10, 500, 135, 86)
        duck.x = 160
        duck.y = 200

        self.hat_icons = [
            sprite.Sprite(self.hat1_select, x=420, y=400),
            sprite.Sprite(self.hat2_select, x=550, y=400),
            sprite.Sprite(self.hat3_select, x=670, y=400),
            sprite.Sprite(self.hat4_select, x=420, y=280),
            sprite.Sprite(self.hat5_select, x=550, y=280),
            sprite.Sprite(self.hat6_select, x=670, y=280),
            sprite.Sprite(self.hat7_select, x=420, y=160),
            sprite.Sprite(self.hat8_select, x=550, y=160),
            sprite.Sprite(self.hat9_select, x=670, y=160),
            sprite.Sprite(self.hat0_select, x=550, y=40)
        ]

        self.hat_selectors = [
            Region(420, 400, 100, 100),
            Region(550, 400, 100, 100),
            Region(670, 400, 100, 100),
            Region(420, 280, 100, 100),
            Region(550, 280, 100, 100),
            Region(670, 280, 100, 100),
            Region(420, 160, 100, 100),
            Region(550, 160, 100, 100),
            Region(670, 160, 100, 100),
            Region(550, 40, 100, 100)
        ]

        self.warn = text.Label("Warning: hats here are not shown accurately",
                               x=200, y=400, anchor_x='center',
                               anchor_y='center',
                               color=(255, 255, 255, 255),
                               bold=True, font_size=10)

    def draw(self):
        licenses.bg.draw()
        licenses.back_spr.draw()
        duck.sprite.draw()
        duck.hat_wear.draw()
        self.warn.draw()

        for hats in self.hat_icons:
            hats.draw()

    def update(self, dt):
        gs = GameState()

        if self.back.contain(game.mouse_x, game.mouse_y):
            window.set_mouse_cursor(choose_cur)

        for selectors in self.hat_selectors:
            if selectors.contain(game.mouse_x, game.mouse_y):
                window.set_mouse_cursor(choose_cur)

        duck.hat_wear.x = duck.x - 60
        duck.hat_wear.y = duck.y + 35
        duck.sprite.scale = 2.8
        duck.hat_wear.scale = 2.8
        if gs.state_exists():
            gs.load(duck)

    def on_click(self, x, y, button):
        gs = GameState()

        if self.back.contain(x, y):
            game.set_next_scene(menu)

        if self.hat_selectors[0].contain(x, y):
            duck.hat_value = 1
            gs.save(duck)

        if self.hat_selectors[1].contain(x, y):
            duck.hat_value = 2
            gs.save(duck)

        if self.hat_selectors[2].contain(x, y):
            duck.hat_value = 3
            gs.save(duck)

        if self.hat_selectors[3].contain(x, y):
            duck.hat_value = 4
            gs.save(duck)

        if self.hat_selectors[4].contain(x, y):
            duck.hat_value = 5
            gs.save(duck)

        if self.hat_selectors[5].contain(x, y):
            duck.hat_value = 6
            gs.save(duck)

        if self.hat_selectors[6].contain(x, y):
            duck.hat_value = 7
            gs.save(duck)

        if self.hat_selectors[7].contain(x, y):
            duck.hat_value = 8
            gs.save(duck)

        if self.hat_selectors[8].contain(x, y):
            duck.hat_value = 9
            gs.save(duck)

        if self.hat_selectors[9].contain(x, y):
            duck.hat_value = 0
            gs.save(duck)


class ParkScene(Scene):

    bg = resource.image('tile_bg.png')
    street_north = resource.image('street_up.png')
    street_east = resource.image('street_east.png')
    street_south = resource.image('street_down.png')
    street_west = resource.image('street_right.png')
    boundary_vertical = resource.image('boundary_vertical.png')
    boundary_horizontal = resource.image('boundary_horizontal.png')
    sign = resource.image('sign.png')

    def __init__(self):
        self.bread_objs = []
        self.obj_list = []

        self.grass_tiles = [
            sprite.Sprite(self.bg, x=0, y=0),
            sprite.Sprite(self.bg, x=800, y=0),
            sprite.Sprite(self.bg, x=1600, y=0),
            sprite.Sprite(self.bg, x=0, y=-600),
            sprite.Sprite(self.bg, x=0, y=-1200),
            sprite.Sprite(self.bg, x=800, y=-600),
            sprite.Sprite(self.bg, x=800, y=-1200),
            sprite.Sprite(self.bg, x=1600, y=-600),
            sprite.Sprite(self.bg, x=1600, y=-1200)
        ]

        self.boundaries = [
            sprite.Sprite(self.boundary_vertical, x=0, y=570),
            sprite.Sprite(self.boundary_vertical, x=300, y=570),
            sprite.Sprite(self.boundary_vertical, x=600, y=570),
            sprite.Sprite(self.boundary_vertical, x=900, y=570),
            sprite.Sprite(self.boundary_vertical, x=1200, y=570),
            sprite.Sprite(self.boundary_vertical, x=1800, y=570),
            sprite.Sprite(self.boundary_vertical, x=2100, y=570),
            sprite.Sprite(self.boundary_vertical, x=0, y=-1200),
            sprite.Sprite(self.boundary_vertical, x=300, y=-1200),
            sprite.Sprite(self.boundary_vertical, x=600, y=-1200),
            sprite.Sprite(self.boundary_vertical, x=900, y=-1200),
            sprite.Sprite(self.boundary_vertical, x=1200, y=-1200),
            sprite.Sprite(self.boundary_vertical, x=1500, y=-1200),
            sprite.Sprite(self.boundary_vertical, x=1800, y=-1200),
            sprite.Sprite(self.boundary_vertical, x=2100, y=-1200),

            # Sign
            sprite.Sprite(self.sign, x=1650, y=470),

            sprite.Sprite(self.boundary_horizontal, x=-10, y=360),
            sprite.Sprite(self.boundary_horizontal, x=-10, y=70),
            sprite.Sprite(self.boundary_horizontal, x=-10, y=-230),
            sprite.Sprite(self.boundary_horizontal, x=-10, y=-530),
            sprite.Sprite(self.boundary_horizontal, x=-10, y=-830),
            sprite.Sprite(self.boundary_horizontal, x=-10, y=-1130),
            sprite.Sprite(self.boundary_horizontal, x=2390, y=342),
            sprite.Sprite(self.boundary_horizontal, x=2390, y=52),
            sprite.Sprite(self.boundary_horizontal, x=2390, y=-238),
            sprite.Sprite(self.boundary_horizontal, x=2390, y=-530),
            sprite.Sprite(self.boundary_horizontal, x=2390, y=-830),
            sprite.Sprite(self.boundary_horizontal, x=2390, y=-1130)
        ]

        self.streets = [
            sprite.Sprite(self.street_north, x=-400, y=550),
            sprite.Sprite(self.street_north, x=0, y=550),
            sprite.Sprite(self.street_north, x=400, y=550),
            sprite.Sprite(self.street_north, x=800, y=550),
            sprite.Sprite(self.street_north, x=1200, y=550),
            sprite.Sprite(self.street_north, x=1600, y=550),
            sprite.Sprite(self.street_north, x=2000, y=550),
            sprite.Sprite(self.street_north, x=2400, y=550),

            sprite.Sprite(self.street_east, x=2400, y=0),
            sprite.Sprite(self.street_east, x=2400, y=200),
            sprite.Sprite(self.street_east, x=2400, y=-200),
            sprite.Sprite(self.street_east, x=2400, y=-600),
            sprite.Sprite(self.street_east, x=2400, y=-1000),
            sprite.Sprite(self.street_east, x=2400, y=-1400),
            sprite.Sprite(self.street_east, x=2400, y=-1800),

            sprite.Sprite(self.street_south, x=0, y=-1700),
            sprite.Sprite(self.street_south, x=400, y=-1700),
            sprite.Sprite(self.street_south, x=800, y=-1700),
            sprite.Sprite(self.street_south, x=1200, y=-1700),
            sprite.Sprite(self.street_south, x=1600, y=-1700),
            sprite.Sprite(self.street_south, x=2000, y=-1700),

            sprite.Sprite(self.street_west, x=-600, y=200),
            sprite.Sprite(self.street_west, x=-600, y=-200),
            sprite.Sprite(self.street_west, x=-600, y=-600),
            sprite.Sprite(self.street_west, x=-600, y=-1000),
            sprite.Sprite(self.street_west, x=-600, y=-1400),
            sprite.Sprite(self.street_west, x=-600, y=-1800)
        ]

        self.water_ponds = [
            sprite.Sprite(water, x=400, y=400),
            sprite.Sprite(water, x=1200, y=200),
            sprite.Sprite(water, x=800, y=-100),
            sprite.Sprite(water, x=1700, y=-300),
            sprite.Sprite(water, x=500, y=-700),
            sprite.Sprite(water, x=800, y=-1700),
        ]

        self.flowers = [
            sprite.Sprite(flower, x=0, y=0),
            sprite.Sprite(flower, x=800, y=0),
            sprite.Sprite(flower, x=1600, y=0),
            sprite.Sprite(flower, x=0, y=-600),
            sprite.Sprite(flower, x=0, y=-1200),
            sprite.Sprite(flower, x=800, y=-600),
            sprite.Sprite(flower, x=800, y=-1200),
            sprite.Sprite(flower, x=1600, y=-600),
            sprite.Sprite(flower, x=1600, y=-1200),
        ]

        self.exit_region = Region(1450, 580, 360, 100)

        self.has_game_finished = False
        self.duck_won = False
        self.target_amount = randint(10, 46)
        self.timed_out = False
        self.target_text = text.Label(f"{self.target_amount}",
                                      x=1670, y=510, bold=True)
        self.update_bread_count()

    def draw(self):

        # Drawing street tiles
        for streets in self.streets:
            streets.draw()

        # Drawing grass tiles
        for grass in self.grass_tiles:
            grass.draw()

        for flower in self.flowers:
            flower.draw()

        # Drawing boundaries
        for boundaries in self.boundaries:
            boundaries.draw()

        # Drawing breads
        for breads in self.bread_objs:
            breads.draw()

        # Drawing water
        for water in self.water_ponds:
            water.draw()

        self.target_text.draw()

    def update(self, dt):
        gs = GameState()

        # Linear movement
        if keys[key.W]:
            duck.change_direction(0, 340, duck.direction)
            duck.moving = True

        if keys[key.A]:
            duck.change_direction(-340, 0, 0)
            duck.moving = True

        if keys[key.S]:
            duck.change_direction(0, -340, duck.direction)
            duck.moving = True

        if keys[key.D]:
            duck.change_direction(340, 0, 1)
            duck.moving = True

        # Diagonal movement
        if keys[key.W] and keys[key.A]:
            duck.change_direction(-300, 300, 0)
            duck.moving = True

        if keys[key.W] and keys[key.D]:
            duck.change_direction(300, 300, 1)
            duck.moving = True

        if keys[key.S] and keys[key.A]:
            duck.change_direction(-300, -300, 0)
            duck.moving = True

        if keys[key.S] and keys[key.D]:
            duck.change_direction(300, -300, 1)
            duck.moving = True

        # Stop if two keys are pressed at the same time
        if keys[key.W] and keys[key.S]:
            duck.change_direction(0, 0, duck.direction)
            duck.moving = False

        if keys[key.A] and keys[key.D]:
            duck.change_direction(0, 0, duck.direction)
            duck.moving = False

        # If no key is pressed
        if not self.is_key_pressed():
            duck.change_direction(0, 0, duck.direction)
            duck.moving = False

        camera.position = (duck.x - 400,
                           duck.y - 300)

        # Grab bread
        self.detect_bread_collision()

        # Finish game
        if game.hud.timer <= 0 and \
           game.mode == NORMAL:
            self.end_game()
            self.duck_won = False
            self.timed_out = True
            lose_results = LoseScreen()
            game.set_next_scene(lose_results)

        if duck.hitbox.collides(self.exit_region) and \
           game.hud.bread_amount >= self.target_amount and \
           game.mode == NORMAL:
            self.end_game()
            self.duck_won = True
            self.timed_out = False
            win_results = WinScreen()
            game.set_next_scene(win_results)
            win_results.play_sound()

        if gs.state_exists():
            gs.load(duck)

    def update_bread_count(self):
        self.target_amount = randint(10, 46)

        if game.mode == NORMAL:
            self.target_text = text.Label(f"{self.target_amount}",
                                          x=1670, y=510, bold=True)
        else:
            self.target_text = text.Label("Fun",
                                          x=1670, y=510, bold=True)

    def begin(self):
        pyglet.clock.schedule_interval(bread_spawn, 2)
        pyglet.clock.schedule_interval(timer, 1)

    def end_game(self):
        pyglet.clock.unschedule(bread_spawn)
        pyglet.clock.unschedule(timer)
        self.has_game_finished = True

        if len(self.bread_objs) > 0:
            for bread in self.bread_objs:
                self.bread_objs.remove(bread)

    def spawn_bread(self, dt):
        if len(self.bread_objs) >= 0:
            new_bread = Bread()
            self.bread_objs.append(new_bread)
            bread.x = randint(125, 2297)
            bread.y = randint(-1035, 511)

    def detect_bread_collision(self):
        for bread in self.bread_objs:
            if duck.hitbox.collides(bread.hitbox) and \
               len(self.bread_objs) > 0:
                bread.is_grabbed()
                game.hud.bread_amount += 1

    def decrease_timer(self, dt):
        game.hud.timer -= 1

    def on_click(self, x, y, button):
        pass

    def on_key_press(self, symbol, modifiers):
        if symbol == key.L:
            game.set_next_scene(menu)

    def is_key_pressed(self):
        for _, v in keys.items():
            if v:
                return True

        return False


class WinScreen(Scene):

    def __init__(self):
        amb.pause()
        self.obj_list = []
        self.text = sprite.Sprite(win_text, x=400, y=300)
        self.lose_text = sprite.Sprite(lose_text, x=400, y=300)

        self.restart = text.Label("Press 'R' to restart", x=400, y=200,
                                  anchor_x='center', anchor_y='center',
                                  bold=True, font_size=24,
                                  color=(255, 255, 255, 255))

        self.leave = text.Label("Press 'L' to return to the menu",
                                x=400, y=150,
                                anchor_x='center', anchor_y='center',
                                bold=True, font_size=24,
                                color=(255, 255, 255, 255))

    def draw(self):
        self.text.draw()
        self.restart.draw()
        self.leave.draw()

    def update(self, dt):
        camera.position = (0, 0)

    def on_click(self, x, y, button):
        pass

    def on_key_press(self, symbol, modifiers):
        if symbol == key.R:
            game.restart()

        if symbol == key.L:
            game.set_next_scene(menu)

    def is_key_pressed(self):
        for _, v in keys.items():
            if v:
                return True

        return False

    def play_sound(self):
        self.audio_player = pyglet.media.Player()
        self.audio_player.queue(victory)
        self.audio_player.play()


class LoseScreen(Scene):

    def __init__(self):
        amb.pause()
        game_over.play()
        self.obj_list = []
        self.text = sprite.Sprite(lose_text, x=400, y=300)

        self.restart = text.Label("Press 'R' to restart", x=400, y=200,
                                  anchor_x='center', anchor_y='center',
                                  bold=True, font_size=24,
                                  color=(255, 255, 255, 255))

        self.leave = text.Label("Press 'L' to return to the menu",
                                x=400, y=150,
                                anchor_x='center', anchor_y='center',
                                bold=True, font_size=24,
                                color=(255, 255, 255, 255))

    def draw(self):
        self.text.draw()
        self.restart.draw()
        self.leave.draw()

    def update(self, dt):
        camera.position = (0, 0)

    def on_click(self, x, y, button):
        pass

    def on_key_press(self, symbol, modifiers):
        if symbol == key.R:
            game.restart()

        if symbol == key.L:
            game.set_next_scene(menu)

    def is_key_pressed(self):
        for _, v in keys.items():
            if v:
                return True

        return False


@window.event
def on_draw():
    window.clear()
    camera.begin()
    gui_camera.begin()
    game.draw()

    if game.scene == park:
        duck.draw()

    gui_camera.end()
    camera.end()


@window.event
def update(dt):
    game.update(dt)
    duck.update(dt)
    game.hud.update(dt)


@window.event
def on_mouse_press(x, y, button, modifiers):
    if button & mouse.LEFT:
        game.scene.on_click(x, y, button)


@window.event
def on_mouse_motion(x, y, dx, dy):
    game.mouse_xy(x, y, dx, dy)


@window.event
def on_key_press(symbol, modifiers):
    game.on_key_press(symbol, modifiers)


# Custom timers
def bread_spawn(dt):
    park.spawn_bread(dt)


def timer(dt):
    park.decrease_timer(dt)


def savestate(dt):
    if game.scene == hats:
        gs = GameState()
        gs.save(duck)


keys = key.KeyStateHandler()
window.push_handlers(keys)

bread = Bread()
duck = Player()
intro = Introduction()
menu = MenuScene()
licenses = Licenses()
hats = HatSelection()
game = Game(intro)
park = ParkScene()
camera = Camera(scroll_speed=5)
gui_camera = Camera(scroll_speed=5)

# Objects for scenes
boundary_up = SceneObject(id=0, solid=True, tag="boundary_up", x=1200, y=600,
                          w=map_width, h=1, visible=False)

boundary_left = SceneObject(id=1, solid=True, tag="boundary_left", x=0, y=-300,
                            w=1, h=1800, visible=False)

boundary_down = SceneObject(id=2, solid=True, tag="boundary_down", x=1200,
                            y=-1120, w=map_width, h=1, visible=False)

boundary_right = SceneObject(id=3, solid=True, tag="boundary_right",
                             x=map_width, y=-300, w=1, h=1800,
                             visible=False)

water_1 = SceneObject(id=4, solid=True, tag="water_1",
                      x=400, y=400, w=175, h=57, visible=False)

water_2 = SceneObject(id=5, solid=True, tag="water_2", x=1200, y=200,
                      w=175, h=57, visible=False)

water_3 = SceneObject(id=6, solid=True, tag="water_3", x=800, y=-100,
                      w=175, h=57, visible=False)

water_4 = SceneObject(id=7, solid=True, tag="water_4", x=1700, y=-300,
                      w=175, h=57, visible=False)

water_5 = SceneObject(id=8, solid=True, tag="water_5", x=500, y=-700,
                      w=175, h=57, visible=False)

water_6 = SceneObject(id=9, solid=True, tag="water_6", x=800, y=-1700,
                      w=175, h=57, visible=False)


# Appending those objects to the scenes
park.obj_list.append(boundary_up)
park.obj_list.append(boundary_left)
park.obj_list.append(boundary_down)
park.obj_list.append(boundary_right)
park.obj_list.append(water_1)
park.obj_list.append(water_2)
park.obj_list.append(water_3)
park.obj_list.append(water_4)
park.obj_list.append(water_5)
park.obj_list.append(water_6)

pyglet.clock.schedule_interval(update, 1/60)
pyglet.clock.schedule_interval(savestate, 2)
pyglet.app.run()
