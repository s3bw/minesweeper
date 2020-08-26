
from math import floor

from library.spritesheet import SpriteSheet


sprites = SpriteSheet("sprites-t.png")


class Sprite:

    def __init__(self, px, py):
        # x, y, w, h
        self.sprite = sprites.image_at((px, py, 16, 16))
        # Transparency
        self.sprite.set_alpha(204)


zero = Sprite(0, 0).sprite
one = Sprite(16, 0).sprite
two = Sprite(32, 0).sprite
three = Sprite(0, 16).sprite
four = Sprite(16, 16).sprite
five = Sprite(32, 16).sprite
six = Sprite(0, 32).sprite
seven = Sprite(16, 32).sprite
eight = Sprite(32, 32).sprite

detonation = Sprite(48, 0).sprite
flag = Sprite(48, 16).sprite
greenflag = Sprite(48, 32).sprite
mine = Sprite(0, 48).sprite
