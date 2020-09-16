from region import Region
from camera import Camera

import pyglet
from pyglet import resource
from pyglet import sprite
from pyglet.window import key
from pyglet.gl import gl

gl.glEnable(gl.GL_TEXTURE_2D)
gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
pyglet.image.Texture.default_mag_filter = gl.GL_NEAREST
pyglet.image.Texture.default_min_filter = gl.GL_NEAREST

map_width = 2400
map_height = 1800

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

        self.x = 400
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
                print(self.vx, self.vy)
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

    def change_direction(self, vx, vy, direction):
        self.vx = vx
        self.vy = vy
        self.direction = direction


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
            self.bread_text.x = self.bread_display.x + 85
        elif self.bread_amount < 100 and self.bread_amount > 9:
            self.bread_text.x = self.bread_display.x + 80

        self.bread_display.x = camera.offset_x + 580
        self.bread_display.y = camera.offset_y + 490
        self.bread_text.y = self.bread_display.y + 42


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


# Scenes
class ParkScene(Scene):

    bg = resource.image('tile_bg.png')

    def __init__(self):
        self.obj_list = []

    def draw(self):
        self.bg.blit(0, 0)

    def update(self, dt):

        # Linear movement
        if keys[key.W]:
            duck.change_direction(0, 170, duck.direction)
            duck.moving = True

        if keys[key.A]:
            duck.change_direction(-170, 0, 0)
            duck.moving = True

        if keys[key.S]:
            duck.change_direction(0, -170, duck.direction)
            duck.moving = True

        if keys[key.D]:
            duck.change_direction(170, 0, 1)
            duck.moving = True

        # Diagonal movement
        if keys[key.W] and keys[key.A]:
            duck.change_direction(-170, 170, 0)
            duck.moving = True

        if keys[key.W] and keys[key.D]:
            duck.change_direction(170, 170, 1)
            duck.moving = True

        if keys[key.S] and keys[key.A]:
            duck.change_direction(-170, -170, 0)
            duck.moving = True

        if keys[key.S] and keys[key.D]:
            duck.change_direction(170, -170, 1)
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


keys = key.KeyStateHandler()
window.push_handlers(keys)

duck = Player()
park = ParkScene()
game = Game(park)
camera = Camera(scroll_speed=5)
gui_camera = Camera(scroll_speed=5)

# Objects for scenes
boundary_up = SceneObject(id=0, solid=True, tag="boundary_up", x=0, y=600,
                          w=map_width, h=1, visible=False)

boundary_left = SceneObject(id=1, solid=True, tag="boundary_left", x=0, y=0,
                            w=1, h=map_height, visible=False)


# Appending those objects to the scenes
park.obj_list.append(boundary_up)
park.obj_list.append(boundary_left)


pyglet.clock.schedule_interval(update, 1/30)
pyglet.app.run()
