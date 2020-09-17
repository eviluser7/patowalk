from region import Region
from camera import Camera

import pyglet
from pyglet import resource
from pyglet import sprite
from pyglet.window import key
from pyglet.gl import gl
from random import randint

gl.glEnable(gl.GL_TEXTURE_2D)
gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
pyglet.image.Texture.default_mag_filter = gl.GL_NEAREST
pyglet.image.Texture.default_min_filter = gl.GL_NEAREST

map_width = 2400
map_height = 1200
frames = 30

resource.path = ['../resources', '../resources/img']
resource.reindex()

window = pyglet.window.Window(800, 600, caption="Pato Goes For a Walk")

gui_batch = pyglet.graphics.Batch()

duck_idle_right = resource.image('duck_idle_right.png')
duck_idle_left = resource.image('duck_idle_left.png')
shadow = resource.image('shadow.png')
hud_bread = resource.image('hud_bread.png')
default_cur = window.get_system_mouse_cursor(window.CURSOR_DEFAULT)
choose_cur = window.get_system_mouse_cursor(window.CURSOR_HAND)


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


# Code structure
class Game:

    def __init__(self, scene):
        self.scene = scene
        self.mouse_x = 0
        self.mouse_y = 0
        self.hud = Hud()

    def draw(self):
        self.scene.draw()

    def update(self, dt):
        window.set_mouse_cursor(default_cur)
        self.scene.update(dt)

    def mouse_xy(self, x, y, dx, dy):
        self.mouse_x = x
        self.mouse_y = y

    def on_click(self, x, y, button):
        self.scene.on_click(x, y, button)

    def set_scene_to(self, scene):
        self.scene = scene


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

    def draw(self):
        self.shadow.draw()
        self.sprite.draw()

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

            if obj_hit == boundary_down:
                print(boundary_down.x, boundary_down.y)

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


class Hud:

    bread_display = sprite.Sprite(hud_bread, x=580, y=490, batch=gui_batch)

    def __init__(self):
        self.bread_amount = 0
        self.bread_text = pyglet.text.Label(f"{self.bread_amount}", x=660,
                                            y=533, anchor_x='center',
                                            anchor_y='center', font_size=24,
                                            bold=True, batch=gui_batch)

    def draw(self):
        self.bread_display.draw()
        self.bread_text.draw()

    def update(self, dt):
        self.update_text()

    def update_text(self):
        if self.bread_amount < 10:
            self.text_x = self.bread_text.x = self.bread_display.x + 85
        elif self.bread_amount < 100 and self.bread_amount > 9:
            self.text_x = self.bread_text.x = self.bread_display.x + 80

        self.bread_display.x = camera.offset_x + 580
        self.bread_display.y = camera.offset_y + 490
        self.text_y = self.bread_text.y = self.bread_display.y + 42

        self.bread_text = pyglet.text.Label(f"{self.bread_amount}",
                                            x=self.text_x, y=self.text_y,
                                            anchor_x='center',
                                            anchor_y='center', font_size=24,
                                            bold=True, batch=gui_batch)


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
        print(boundary_down.x, boundary_down.y)

    def on_key_press(self, symbol, modifiers):
        pass


# Scenes
class ParkScene(Scene):

    bg = resource.image('tile_bg.png')
    street_north = resource.image('street_up.png')
    street_east = resource.image('street_east.png')
    street_south = resource.image('street_down.png')
    street_west = resource.image('street_right.png')
    boundary_vertical = resource.image('boundary_vertical.png')
    boundary_horizontal = resource.image('boundary_horizontal.png')

    def __init__(self):
        self.begin()
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
            sprite.Sprite(self.boundary_vertical, x=1500, y=570),
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

    def draw(self):

        # Drawing street tiles
        for streets in self.streets:
            streets.draw()

        # Drawing grass tiles
        for grass in self.grass_tiles:
            grass.draw()

        # Drawing boundaries
        for boundaries in self.boundaries:
            boundaries.draw()

        # Drawing breads
        for breads in self.bread_objs:
            breads.draw()

    def update(self, dt):

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

    def begin(self):
        pyglet.clock.schedule_interval(bread_spawn, randint(2, 6))

    def spawn_bread(self, dt):
        if len(self.bread_objs) >= 0:
            new_bread = Bread()
            self.bread_objs.append(new_bread)
            bread.x = randint(125, 2297)
            bread.y = randint(-1035, 511)

            print("Bread spawned at: ", bread.x, bread.y)

    def detect_bread_collision(self):
        for bread in self.bread_objs:
            if duck.hitbox.collides(bread.hitbox) and \
               len(self.bread_objs) > 0:
                bread.is_grabbed()
                game.hud.bread_amount += 1
                print(game.hud.bread_amount)

    def on_click(self, x, y, button):
        pass

    def on_key_press(self, symbol, modifiers):
        pass

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

    with gui_camera:
        gui_batch.draw()

    game.draw()
    duck.draw()
    game.hud.draw()
    gui_camera.end()
    camera.end()


@window.event
def update(dt):
    game.update(dt)
    duck.update(dt)
    game.hud.update(dt)


@window.event
def on_mouse_press(x, y, button, modifiers):
    print("Player: ", duck.x // 2, duck.y // 2)


# Custom timers
def bread_spawn(dt):
    park.spawn_bread(dt)


keys = key.KeyStateHandler()
window.push_handlers(keys)

bread = Bread()
duck = Player()
park = ParkScene()
game = Game(park)
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


# Appending those objects to the scenes
park.obj_list.append(boundary_up)
park.obj_list.append(boundary_left)
park.obj_list.append(boundary_down)
park.obj_list.append(boundary_right)

pyglet.clock.schedule_interval(update, 1/frames)
pyglet.app.run()
