from region import Region
import pyglet
from pyglet import resource
from pyglet import sprite
from pyglet.window import key

map_width = 2400
map_height = 1800

resource.path = ['../resources', '../resources/img']
resource.reindex()

window = pyglet.window.Window(800, 600, caption="Pato Goes For a Walk")
duck_idle_right = resource.image('duck_idle_right.png')
duck_idle_left = resource.image('duck_idle_left.png')
shadow = resource.image('shadow.png')
default_cur = window.get_system_mouse_cursor(window.CURSOR_DEFAULT)
choose_cur = window.get_system_mouse_cursor(window.CURSOR_HAND)


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
        self.idle = sprite.Sprite(self.idle_images[0])
        self.w_right = sprite.Sprite(self.walk_right)
        self.w_left = sprite.Sprite(self.walk_left)
        self.sprite = self.idle
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
                self.sprite = self.idle
                self.sprite.x = self.x
                self.sprite.y = self.y
                return

        # Check sprite
        if not self.moving:
            self.sprite = self.idle

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
    game.draw()
    duck.draw()


@window.event
def update(dt):
    game.update(dt)
    duck.update(dt)


keys = key.KeyStateHandler()
window.push_handlers(keys)

duck = Player()
park = ParkScene()
game = Game(park)

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
