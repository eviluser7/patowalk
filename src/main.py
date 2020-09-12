import pyglet
from pyglet import resource
from pyglet import sprite

resource.path = ['../resources', '../resources/img']
resource.reindex()

window = pyglet.window.Window(800, 600, caption="Pato Goes For a Walk")
duck = resource.image('duck_idle_right.png')
default_cur = window.get_system_mouse_cursor(window.CURSOR_DEFAULT)
choose_cur = window.get_system_mouse_cursor(window.CURSOR_HAND)


def center_image(img):
    img.anchor_x = img.width // 2
    img.anchor_y = img.height // 2


center_image(duck)


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


@window.event
def on_draw():
    window.clear()
    duck.blit(400, 300)


pyglet.app.run()
