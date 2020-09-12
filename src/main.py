import pyglet
from pyglet import resource
from pyglet import sprite
from pyglet.window import key

resource.path = ['../resources', '../resources/img']
resource.reindex()

window = pyglet.window.Window(800, 600, caption="Pato Goes For a Walk")
duck_idle_right = resource.image('duck_idle_right.png')
duck_idle_left = resource.image('duck_idle_left.png')
default_cur = window.get_system_mouse_cursor(window.CURSOR_DEFAULT)
choose_cur = window.get_system_mouse_cursor(window.CURSOR_HAND)


def center_image(img):
    img.anchor_x = img.width // 2
    img.anchor_y = img.height // 2


center_image(duck_idle_right)
center_image(duck_idle_left)


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
        self.moving = False

    def draw(self):
        self.sprite.draw()

    def update(self, dt):
        new_x = self.x + self.vx * dt
        new_y = self.y + self.vy * dt

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

    def change_direction(self, vx, vy, direction):
        self.vx = vx
        self.vy = vy
        self.direction = direction


class Scene:

    def __init__(self):
        pass

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

    def __init__(self):
        pass

    def draw(self):
        pass

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

pyglet.clock.schedule_interval(update, 1/30)
pyglet.app.run()
