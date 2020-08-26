import operator
from enum import Enum
from math import floor
from random import randrange

import pygame

from library import colours

from consts import GRIDPADDING
from consts import BLOCK_SIZE

from sprites import (
    mine, detonation,
    flag, greenflag,
    zero,
    one,
    two,
    three,
    four,
    five,
    six,
    seven,
    eight,
)


transformations = [
    (-1, 0),
    (1, 0),
    (-1, -1),
    (+1, +1),
    (0, -1),
    (0, +1),
    (-1, +1),
    (+1, -1),
]


def add(a, b):
    return tuple(map(operator.add, a, b))


def _normalise_pos(pos):
    a, b = pos
    return 16 * floor(a/16), 16 * floor(b/16)


def _floor_pos(pos):
    a, b = pos
    return floor(a/16) - 1, floor(b/16) - 1


class TileType(Enum):

    Empty = 0
    One = 1
    Two = 2
    Three = 3
    Four = 4
    Five = 5
    Six = 6
    Seven = 7
    Eight = 8
    Mine = "mine"
    Detonation = "detonation"


def get_sprite(type):
    if type == TileType.Mine:
        return mine
    if type == TileType.Detonation:
        return detonation

    if type == TileType.One:
        return one
    if type == TileType.Two:
        return two
    if type == TileType.Three:
        return three
    if type == TileType.Four:
        return four
    if type == TileType.Five:
        return five
    if type == TileType.Six:
        return six
    if type == TileType.Seven:
        return seven
    if type == TileType.Eight:
        return eight

    if type == TileType.Empty:
        return zero


class Flag:

    Red = "red"
    Green = "green"


class Tile:
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.n = 0
        self.type = type
        self.flagged = False
        self._flag_colour = Flag.Red
        self.visible = False

    def render(self, win):
        pos = (
            GRIDPADDING + (self.x * BLOCK_SIZE),
            GRIDPADDING + (self.y * BLOCK_SIZE),
        )
        if self.flagged:
            if self._flag_colour == Flag.Red:
                win.blit(flag, pos)
            else:
                win.blit(greenflag, pos)

        if not self.visible:
            return

        sprite = get_sprite(self.type)
        if sprite:
            px, py = pos
            rect = pygame.Rect(pos, (16, 16))
            pygame.draw.rect(win, (170,170,170), rect)

        if sprite is not zero:
            win.blit(sprite, pos)

    def toggle_visible(self):
        if self.visible:
            return

        self.visible= True

    def toggle_flag(self):
        if self.flagged:
            self.flagged = False
        else:
            self.flagged = True

    def set_type(self, type):
        self.type = type

    def set_green(self):
        self._flag_colour = Flag.Green

    def increment(self):
        if self.type == TileType.Mine:
            raise ValueError("Can't increment a mine")
        self.n += 1
        self.type = TileType(self.n)

    def around(self):
        pos = (self.x, self.y)
        yield from _around(pos)


def _around(pos):
    for t in transformations:
        other = add(pos, t)
        yield other


class Board:

    def rightclick(self, pos):
        realx, realy = _floor_pos(pos)
        if self._inside_board(realx, realy):
            if self.grid:
                self.grid[realx][realy].toggle_flag()
                self.flags.add((realx, realy))

    def leftclick(self, pos) -> bool:
        """The return value determines if the player survived."""
        realx, realy = _floor_pos(pos)
        if not self.grid:
            self.grid = self._construct_grid(self.x, self.y, (realx, realy))

        if self._inside_board(realx, realy):
            tile = self.grid[realx][realy]
            if tile.type == TileType.Mine:
                tile.type = TileType.Detonation
                return False

            if tile.visible:
                return True

            searched = set()
            tile.toggle_visible()
            self._zero_search(tile, searched)
        return True

    def show_mines(self):
        if not self._revealed:
            self._revealed = True

            for pos in self.mines:
                px, py = pos
                tile = self.grid[px][py]
                if pos not in self.flags:
                    tile.toggle_visible()
                else:
                    tile.set_green()

    def _zero_search(self, tile, searched):
        if tile.n != 0:
            return searched

        if tile.type == TileType.Mine or tile.flagged:
            return searched

        for pos in tile.around():
            px, py = pos
            if self._inside_board(px, py):
                tile = self.grid[px][py]
                if tile not in searched:
                    searched.add(tile)
                    searched = self._zero_search(tile, searched)

                tile.toggle_visible()

        return searched

    def __init__(self, x, y, mines: int):
        self.x = x
        self.y = y
        self.n_mines = mines
        self.flags = set()
        self.grid = None
        self._revealed = False

        x_blocks = x * BLOCK_SIZE
        y_blocks = y * BLOCK_SIZE

        self.tl = (GRIDPADDING, GRIDPADDING)
        self.tr = (GRIDPADDING, GRIDPADDING + x_blocks)
        self.bl = (GRIDPADDING + y_blocks, GRIDPADDING)
        self.br = (GRIDPADDING + y_blocks, GRIDPADDING + x_blocks)

    def _construct_grid(self, x, y, first_pos):
        exclude = {pos for pos in _around(first_pos)}
        exclude.add(first_pos)

        # Generate Grid.
        grid = [
            [Tile(rx, ry, TileType.Empty) for ry in range(y)]
            for rx in range(x)
        ]

        # Placing the mines on the board
        mines = set()
        while len(mines) < self.n_mines:
            mx, my = randrange(self.x), randrange(self.y)
            if ((mx, my) not in mines) and ((mx, my) not in exclude):
                mines.add((mx, my))
                tile = grid[mx][my]
                tile.set_type(TileType.Mine)

        # Calculate Numbers surrounding mines
        for mine in mines:
            mx, my = mine
            tile = grid[mx][my]
            for ox, oy in tile.around():
                if self._inside_board(ox, oy):
                    other_tile = grid[ox][oy]
                    if other_tile.type != TileType.Mine:
                        other_tile.increment()

        self.mines = mines

        return grid

    def _inside_board(self, x, y):
        return (0 <= x <= self.x - 1) and (0 <= y <= self.y - 1)

    def _render_grid(self, win):
        for row in self.grid:
            for tile in row:
                tile.render(win)

    def render(self, win):
        if self.grid:
            self._render_grid(win)

        # Outline
        for i in range(0, self.x + 1):
            left = add(self.tl, (i*16, 0))
            right = add(self.tr, (i*16, 0))
            pygame.draw.line(win, colours.BLACK, left , right, 1)

        for i in range(0, self.y + 1):
            top = add(self.tl, (0, i*16))
            bottom = add(self.bl, (0, i*16))
            pygame.draw.line(win, colours.BLACK, top, bottom, 1)
