import pyglet
from pyglet import resource
from pyglet import sprite

resource.path = ['../resources', '../resources/img']
resource.reindex()

window = pyglet.window.Window(800, 600, caption="Pato Goes For a Walk")
duck = resource.image('duck_idle_right.png')


def center_image(img):
    img.anchor_x = img.width // 2
    img.anchor_y = img.height // 2


center_image(duck)


@window.event
def on_draw():
    window.clear()
    duck.blit(400, 300)


pyglet.app.run()
