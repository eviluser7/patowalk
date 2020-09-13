import pyglet
from pyglet.gl import gl


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
