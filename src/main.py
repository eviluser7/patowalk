import pyglet
from pyglet import resource
from pyglet import sprite

resource.path = ['../resources', '../resources/img']
resource.reindex()

window = pyglet.window.Window(800, 600, caption="Pato Goes For a Walk")
duck = resource.image('duck_idle_right.png')


@window.event
def on_draw():
    window.clear()
    duck.blit(0, 0)


pyglet.app.run()
